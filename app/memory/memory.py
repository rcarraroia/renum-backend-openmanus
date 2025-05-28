"""
Memory management module for OpenManus agents.

This module provides memory management capabilities for agents,
including conversation history tracking and memory strategies.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from loguru import logger

class BaseMemory:
    """Base class for memory implementations."""
    
    def __init__(self, config: Dict[str, Any] = {}):
        """
        Initialize memory with configuration.
        
        Args:
            config: Configuration dictionary for memory
        """
        self.config = config
        self.messages = []
        self.max_tokens = config.get("max_tokens", 4000)
        self.max_messages = config.get("max_messages", 100)
    
    def add_user_message(self, content: str) -> None:
        """
        Add a user message to memory.
        
        Args:
            content: Message content
        """
        self.messages.append({
            "role": "user",
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self._trim_memory_if_needed()
    
    def add_assistant_message(self, content: str) -> None:
        """
        Add an assistant message to memory.
        
        Args:
            content: Message content
        """
        self.messages.append({
            "role": "assistant",
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self._trim_memory_if_needed()
    
    def add_system_message(self, content: str) -> None:
        """
        Add a system message to memory.
        
        Args:
            content: Message content
        """
        self.messages.append({
            "role": "system",
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self._trim_memory_if_needed()
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Get the conversation history.
        
        Returns:
            List of message dictionaries
        """
        return self.messages
    
    def clear(self) -> None:
        """Clear all messages from memory."""
        self.messages = []
    
    def get_memory_size(self) -> int:
        """
        Get the current size of memory in messages.
        
        Returns:
            Number of messages in memory
        """
        return len(self.messages)
    
    def _trim_memory_if_needed(self) -> None:
        """Trim memory if it exceeds configured limits."""
        # Implement in subclasses
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert memory to dictionary for serialization.
        
        Returns:
            Dictionary representation of memory
        """
        return {
            "config": self.config,
            "messages": self.messages
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseMemory':
        """
        Create memory instance from dictionary.
        
        Args:
            data: Dictionary representation of memory
            
        Returns:
            Memory instance
        """
        instance = cls(data.get("config", {}))
        instance.messages = data.get("messages", [])
        return instance


class SimpleMemory(BaseMemory):
    """Simple memory implementation with basic trimming strategy."""
    
    def _trim_memory_if_needed(self) -> None:
        """Trim memory if it exceeds configured limits."""
        # Trim by message count
        if len(self.messages) > self.max_messages:
            # Keep the most recent messages
            excess = len(self.messages) - self.max_messages
            # Always keep system messages
            system_messages = [m for m in self.messages[:excess] if m["role"] == "system"]
            self.messages = system_messages + self.messages[excess:]


class SummarizingMemory(BaseMemory):
    """Memory implementation that summarizes old messages to save space."""
    
    def __init__(self, config: Dict[str, Any] = {}):
        """
        Initialize summarizing memory.
        
        Args:
            config: Configuration dictionary for memory
        """
        super().__init__(config)
        self.summarization_threshold = config.get("summarization_threshold", 20)
        self.llm_provider = None  # Will be set by the agent factory
    
    def set_llm_provider(self, llm_provider: Any) -> None:
        """
        Set the LLM provider for summarization.
        
        Args:
            llm_provider: LLM provider instance
        """
        self.llm_provider = llm_provider
    
    def _trim_memory_if_needed(self) -> None:
        """Trim memory by summarizing old messages."""
        if len(self.messages) > self.max_messages:
            if self.llm_provider:
                # Summarize oldest messages
                messages_to_summarize = self.messages[:self.summarization_threshold]
                non_system_messages = [m for m in messages_to_summarize if m["role"] != "system"]
                system_messages = [m for m in messages_to_summarize if m["role"] == "system"]
                
                if non_system_messages:
                    # Create a prompt for summarization
                    conversation_text = "\n".join([
                        f"{m['role']}: {m['content']}" for m in non_system_messages
                    ])
                    
                    summarization_prompt = f"Summarize the following conversation concisely:\n\n{conversation_text}"
                    
                    try:
                        # Generate summary
                        summary = self.llm_provider.generate_text(summarization_prompt)
                        
                        # Replace messages with summary
                        summary_message = {
                            "role": "system",
                            "content": f"Summary of previous conversation: {summary}",
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        self.messages = system_messages + [summary_message] + self.messages[self.summarization_threshold:]
                        
                    except Exception as e:
                        logger.error(f"Error summarizing memory: {str(e)}")
                        # Fall back to simple trimming
                        self.messages = system_messages + self.messages[self.summarization_threshold:]
                else:
                    # No non-system messages to summarize
                    self.messages = self.messages[-self.max_messages:]
            else:
                # No LLM provider, fall back to simple trimming
                excess = len(self.messages) - self.max_messages
                system_messages = [m for m in self.messages[:excess] if m["role"] == "system"]
                self.messages = system_messages + self.messages[excess:]


class NoMemory(BaseMemory):
    """Memory implementation that only keeps the most recent exchange."""
    
    def add_user_message(self, content: str) -> None:
        """
        Add a user message, clearing previous non-system messages.
        
        Args:
            content: Message content
        """
        # Keep only system messages
        system_messages = [m for m in self.messages if m["role"] == "system"]
        self.messages = system_messages + [{
            "role": "user",
            "content": content,
            "timestamp": datetime.now().isoformat()
        }]
    
    def add_assistant_message(self, content: str) -> None:
        """
        Add an assistant message.
        
        Args:
            content: Message content
        """
        self.messages.append({
            "role": "assistant",
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def _trim_memory_if_needed(self) -> None:
        """No trimming needed for this implementation."""
        pass


def get_memory_manager(config: Dict[str, Any] = {}) -> BaseMemory:
    """
    Factory function to create a memory manager based on configuration.
    
    Args:
        config: Memory configuration dictionary
        
    Returns:
        Memory manager instance
    """
    memory_type = config.get("type", "simple")
    
    if memory_type == "summarizing":
        return SummarizingMemory(config)
    elif memory_type == "none":
        return NoMemory(config)
    else:  # default to simple
        return SimpleMemory(config)
