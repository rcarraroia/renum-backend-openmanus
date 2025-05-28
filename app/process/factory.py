"""
Process Factory for OpenManus agents.

This module provides a factory for creating and managing OpenManus agent processes,
with dynamic loading from Supabase configuration.
"""

import os
import uuid
import json
import asyncio
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from loguru import logger

from app.db.supabase import get_supabase_client
from app.utils.crypto import decrypt_api_key
from app.llm.providers import get_llm_provider
from app.memory.memory import get_memory_manager
from app.knowledge.knowledge_base import get_knowledge_base

class AgentProcessFactory:
    """
    Factory for creating and managing OpenManus agent processes.
    
    This class handles the lifecycle of agent processes, including:
    - Creating agents based on Supabase configuration
    - Sending prompts to agents
    - Managing multiple concurrent agents
    - Terminating agents when they're no longer needed
    """
    
    def __init__(self):
        """Initialize the factory with empty process registry."""
        self.processes: Dict[str, subprocess.Popen] = {}
        self.agent_configs: Dict[str, Dict[str, Any]] = {}
        self.agent_tools: Dict[str, List[Dict[str, Any]]] = {}
        self.supabase = get_supabase_client()
    
    async def load_agent_config(self, agent_id: str) -> Dict[str, Any]:
        """
        Load agent configuration from Supabase.
        
        Args:
            agent_id: ID of the agent to load
            
        Returns:
            Dict containing the agent configuration
            
        Raises:
            ValueError: If agent not found or configuration is invalid
        """
        try:
            # Fetch agent configuration
            response = self.supabase.table("agents").select("*").eq("id", agent_id).execute()
            
            if not response.data or len(response.data) == 0:
                raise ValueError(f"Agent with ID {agent_id} not found")
            
            agent_config = response.data[0]
            
            # Fetch associated tools
            tools_response = self.supabase.table("agent_tools").select("*").eq("agent_id", agent_id).execute()
            agent_tools = []
            
            for agent_tool in tools_response.data:
                tool_id = agent_tool["tool_id"]
                tool_response = self.supabase.table("tools").select("*").eq("id", tool_id).execute()
                
                if tool_response.data and len(tool_response.data) > 0:
                    tool = tool_response.data[0]
                    
                    # If tool requires credentials, fetch them
                    if tool.get("requires_credentials", False):
                        credential_provider = tool.get("credential_provider")
                        if credential_provider:
                            # Get user ID from agent config
                            user_id = agent_config["created_by"]
                            
                            # Fetch credential
                            credential_response = self.supabase.table("credentials") \
                                .select("*") \
                                .eq("user_id", user_id) \
                                .eq("provider", credential_provider) \
                                .execute()
                            
                            if credential_response.data and len(credential_response.data) > 0:
                                credential = credential_response.data[0]
                                # Decrypt API key
                                api_key = decrypt_api_key(credential["api_key_encrypted"])
                                
                                # Add credential to tool configuration
                                tool_config = agent_tool.get("tool_configuration", {})
                                tool_config["api_key"] = api_key
                                agent_tool["tool_configuration"] = tool_config
                    
                    # Combine tool data with agent_tool configuration
                    combined_tool = {
                        **tool,
                        "configuration": agent_tool.get("tool_configuration", {}),
                        "enabled": agent_tool.get("enabled", True)
                    }
                    
                    if combined_tool["enabled"]:
                        agent_tools.append(combined_tool)
            
            # Store agent config and tools
            self.agent_configs[agent_id] = agent_config
            self.agent_tools[agent_id] = agent_tools
            
            return agent_config
            
        except Exception as e:
            logger.error(f"Error loading agent configuration: {str(e)}")
            raise ValueError(f"Failed to load agent configuration: {str(e)}")
    
    async def create_agent(self, agent_id: str) -> str:
        """
        Create a new agent process based on Supabase configuration.
        
        Args:
            agent_id: ID of the agent to create
            
        Returns:
            process_id: Unique ID for the created process
            
        Raises:
            ValueError: If agent creation fails
        """
        try:
            # Load agent configuration if not already loaded
            if agent_id not in self.agent_configs:
                await self.load_agent_config(agent_id)
            
            agent_config = self.agent_configs[agent_id]
            agent_tools = self.agent_tools.get(agent_id, [])
            
            # Generate a unique process ID
            process_id = str(uuid.uuid4())
            
            # Configure LLM provider
            llm_config = agent_config.get("llm_config", {})
            llm_provider = get_llm_provider(llm_config)
            
            # Configure memory
            memory_config = agent_config.get("memory_config", {})
            memory_manager = get_memory_manager(memory_config)
            
            # Configure knowledge base
            kb_config = agent_config.get("knowledge_base_config", {})
            knowledge_base = get_knowledge_base(kb_config)
            
            # Prepare system prompt
            system_prompt = agent_config.get("system_prompt", "")
            
            # Prepare tools
            tools_config = []
            for tool in agent_tools:
                if tool.get("enabled", True):
                    tools_config.append({
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "class_name": tool["backend_tool_class_name"],
                        "parameters": tool.get("parameters_schema", {}),
                        "configuration": tool.get("configuration", {})
                    })
            
            # Create agent process
            # In a real implementation, this would launch a subprocess or create a thread
            # For now, we'll simulate this with a dictionary entry
            self.processes[process_id] = {
                "agent_id": agent_id,
                "llm_provider": llm_provider,
                "memory_manager": memory_manager,
                "knowledge_base": knowledge_base,
                "system_prompt": system_prompt,
                "tools": tools_config,
                "active": True
            }
            
            logger.info(f"Created agent process {process_id} for agent {agent_id}")
            return process_id
            
        except Exception as e:
            logger.error(f"Error creating agent: {str(e)}")
            raise ValueError(f"Failed to create agent: {str(e)}")
    
    async def send_prompt(self, process_id: str, prompt: str) -> Dict[str, Any]:
        """
        Send a prompt to an agent process.
        
        Args:
            process_id: ID of the process to send the prompt to
            prompt: The prompt text to send
            
        Returns:
            Dict containing the agent's response
            
        Raises:
            ValueError: If process not found or sending prompt fails
        """
        try:
            if process_id not in self.processes:
                raise ValueError(f"Process with ID {process_id} not found")
            
            process = self.processes[process_id]
            
            if not process.get("active", False):
                raise ValueError(f"Process with ID {process_id} is not active")
            
            # In a real implementation, this would send the prompt to the subprocess
            # and wait for a response. For now, we'll simulate a response.
            
            # Get the LLM provider
            llm_provider = process.get("llm_provider")
            
            # Get the memory manager
            memory_manager = process.get("memory_manager")
            
            # Add prompt to memory
            memory_manager.add_user_message(prompt)
            
            # Get conversation history
            conversation = memory_manager.get_conversation_history()
            
            # Get the knowledge base
            knowledge_base = process.get("knowledge_base")
            
            # Enrich prompt with relevant knowledge
            enriched_prompt = knowledge_base.enrich_prompt(prompt)
            
            # Get system prompt
            system_prompt = process.get("system_prompt", "")
            
            # Get available tools
            tools = process.get("tools", [])
            
            # Generate response using LLM
            response = llm_provider.generate_response(
                system_prompt=system_prompt,
                conversation=conversation,
                tools=tools,
                enriched_prompt=enriched_prompt
            )
            
            # Add response to memory
            memory_manager.add_assistant_message(response["content"])
            
            return {
                "process_id": process_id,
                "agent_id": process.get("agent_id"),
                "content": response["content"],
                "tool_calls": response.get("tool_calls", [])
            }
            
        except Exception as e:
            logger.error(f"Error sending prompt to agent: {str(e)}")
            raise ValueError(f"Failed to send prompt to agent: {str(e)}")
    
    def terminate_agent(self, process_id: str) -> bool:
        """
        Terminate an agent process.
        
        Args:
            process_id: ID of the process to terminate
            
        Returns:
            bool: True if termination was successful, False otherwise
        """
        try:
            if process_id not in self.processes:
                logger.warning(f"Process with ID {process_id} not found")
                return False
            
            # In a real implementation, this would terminate the subprocess
            # For now, we'll just remove it from our dictionary
            process = self.processes[process_id]
            process["active"] = False
            
            logger.info(f"Terminated agent process {process_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error terminating agent: {str(e)}")
            return False
    
    def terminate_all_agents(self) -> int:
        """
        Terminate all active agent processes.
        
        Returns:
            int: Number of processes terminated
        """
        terminated_count = 0
        
        for process_id in list(self.processes.keys()):
            if self.terminate_agent(process_id):
                terminated_count += 1
        
        logger.info(f"Terminated {terminated_count} agent processes")
        return terminated_count
    
    def get_active_agents(self) -> List[str]:
        """
        Get a list of active agent process IDs.
        
        Returns:
            List[str]: List of active process IDs
        """
        return [
            process_id 
            for process_id, process in self.processes.items() 
            if process.get("active", False)
        ]
    
    def get_agent_status(self, process_id: str) -> Dict[str, Any]:
        """
        Get the status of an agent process.
        
        Args:
            process_id: ID of the process to get status for
            
        Returns:
            Dict containing the agent's status
            
        Raises:
            ValueError: If process not found
        """
        if process_id not in self.processes:
            raise ValueError(f"Process with ID {process_id} not found")
        
        process = self.processes[process_id]
        
        return {
            "process_id": process_id,
            "agent_id": process.get("agent_id"),
            "active": process.get("active", False),
            "tools_count": len(process.get("tools", [])),
            "memory_size": process.get("memory_manager").get_memory_size() if process.get("memory_manager") else 0
        }

# Singleton instance
agent_factory = AgentProcessFactory()

def get_agent_factory() -> AgentProcessFactory:
    """
    Get the singleton instance of the AgentProcessFactory.
    
    Returns:
        AgentProcessFactory: The singleton instance
    """
    return agent_factory
