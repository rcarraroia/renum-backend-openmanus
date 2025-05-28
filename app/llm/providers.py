"""
LLM integration module for OpenManus agents.

This module provides integration with various LLM providers,
including OpenAI, Gemini, Groq, and others.
"""

from typing import Dict, List, Any, Optional, Tuple
import os
import json
import time
from loguru import logger

# Tentativa de importação de bibliotecas de LLM
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Generative AI library not available")

try:
    import boto3
    BEDROCK_AVAILABLE = True
except ImportError:
    BEDROCK_AVAILABLE = False
    logger.warning("Boto3 library not available for AWS Bedrock")

class BaseLLMProvider:
    """Base class for LLM provider implementations."""
    
    def __init__(self, config: Dict[str, Any] = {}):
        """
        Initialize LLM provider with configuration.
        
        Args:
            config: Configuration dictionary for LLM provider
        """
        self.config = config
        self.model = config.get("model", "")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 1000)
    
    def generate_response(
        self, 
        system_prompt: str, 
        conversation: List[Dict[str, Any]], 
        tools: List[Dict[str, Any]] = [],
        enriched_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a response from the LLM.
        
        Args:
            system_prompt: System prompt for the LLM
            conversation: Conversation history
            tools: Available tools for the LLM
            enriched_prompt: Optional enriched prompt from knowledge base
            
        Returns:
            Dictionary containing the response
        """
        # Implement in subclasses
        return {"content": "Not implemented", "tool_calls": []}
    
    def generate_text(self, prompt: str) -> str:
        """
        Generate text from a simple prompt.
        
        Args:
            prompt: Text prompt
            
        Returns:
            Generated text
        """
        # Implement in subclasses
        return "Not implemented"


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider implementation."""
    
    def __init__(self, config: Dict[str, Any] = {}):
        """
        Initialize OpenAI provider.
        
        Args:
            config: Configuration dictionary for OpenAI
        """
        super().__init__(config)
        
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not available")
        
        self.api_key = config.get("api_key", os.environ.get("OPENAI_API_KEY"))
        
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        
        self.model = config.get("model", "gpt-4")
        self.client = openai.OpenAI(api_key=self.api_key)
    
    def generate_response(
        self, 
        system_prompt: str, 
        conversation: List[Dict[str, Any]], 
        tools: List[Dict[str, Any]] = [],
        enriched_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a response from OpenAI.
        
        Args:
            system_prompt: System prompt for the LLM
            conversation: Conversation history
            tools: Available tools for the LLM
            enriched_prompt: Optional enriched prompt from knowledge base
            
        Returns:
            Dictionary containing the response
        """
        try:
            # Format messages for OpenAI
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history
            for message in conversation:
                role = message.get("role", "user")
                content = message.get("content", "")
                
                if role in ["user", "assistant", "system"]:
                    messages.append({"role": role, "content": content})
            
            # If we have an enriched prompt, replace the last user message
            if enriched_prompt and messages[-1]["role"] == "user":
                messages[-1]["content"] = enriched_prompt
            
            # Format tools for OpenAI
            openai_tools = []
            for tool in tools:
                openai_tool = {
                    "type": "function",
                    "function": {
                        "name": tool.get("name", ""),
                        "description": tool.get("description", ""),
                        "parameters": tool.get("parameters", {})
                    }
                }
                openai_tools.append(openai_tool)
            
            # Generate response
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            if openai_tools:
                kwargs["tools"] = openai_tools
            
            response = self.client.chat.completions.create(**kwargs)
            
            # Extract response content and tool calls
            content = response.choices[0].message.content or ""
            
            tool_calls = []
            if hasattr(response.choices[0].message, "tool_calls") and response.choices[0].message.tool_calls:
                for tool_call in response.choices[0].message.tool_calls:
                    if tool_call.type == "function":
                        tool_calls.append({
                            "name": tool_call.function.name,
                            "arguments": json.loads(tool_call.function.arguments)
                        })
            
            return {
                "content": content,
                "tool_calls": tool_calls
            }
            
        except Exception as e:
            logger.error(f"Error generating response from OpenAI: {str(e)}")
            return {
                "content": f"Error generating response: {str(e)}",
                "tool_calls": []
            }
    
    def generate_text(self, prompt: str) -> str:
        """
        Generate text from a simple prompt using OpenAI.
        
        Args:
            prompt: Text prompt
            
        Returns:
            Generated text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content or ""
            
        except Exception as e:
            logger.error(f"Error generating text from OpenAI: {str(e)}")
            return f"Error generating text: {str(e)}"


class GeminiProvider(BaseLLMProvider):
    """Google Gemini API provider implementation."""
    
    def __init__(self, config: Dict[str, Any] = {}):
        """
        Initialize Gemini provider.
        
        Args:
            config: Configuration dictionary for Gemini
        """
        super().__init__(config)
        
        if not GEMINI_AVAILABLE:
            raise ImportError("Google Generative AI library not available")
        
        self.api_key = config.get("api_key", os.environ.get("GEMINI_API_KEY"))
        
        if not self.api_key:
            raise ValueError("Gemini API key not provided")
        
        self.model = config.get("model", "gemini-pro")
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(self.model)
    
    def generate_response(
        self, 
        system_prompt: str, 
        conversation: List[Dict[str, Any]], 
        tools: List[Dict[str, Any]] = [],
        enriched_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a response from Gemini.
        
        Args:
            system_prompt: System prompt for the LLM
            conversation: Conversation history
            tools: Available tools for the LLM
            enriched_prompt: Optional enriched prompt from knowledge base
            
        Returns:
            Dictionary containing the response
        """
        try:
            # Format messages for Gemini
            chat = self.client.start_chat(history=[])
            
            # Add system prompt
            chat.send_message(system_prompt)
            
            # Add conversation history
            for message in conversation:
                role = message.get("role", "user")
                content = message.get("content", "")
                
                if role == "user":
                    chat.send_message(content)
                elif role == "assistant":
                    # Gemini doesn't support adding assistant messages directly
                    # We'll simulate this by adding a user message and then the assistant response
                    pass
            
            # Get the last user message
            last_user_message = ""
            for message in reversed(conversation):
                if message.get("role") == "user":
                    last_user_message = message.get("content", "")
                    break
            
            # If we have an enriched prompt, use it instead of the last user message
            if enriched_prompt:
                last_user_message = enriched_prompt
            
            # Generate response
            response = chat.send_message(last_user_message)
            
            # Extract response content
            content = response.text
            
            # Gemini doesn't support tool calls directly, so we'll parse the response
            # to look for tool calls in a specific format
            tool_calls = []
            if tools and "TOOL_CALL:" in content:
                # Extract tool calls from the response
                tool_call_sections = content.split("TOOL_CALL:")[1:]
                
                for section in tool_call_sections:
                    try:
                        # Extract tool name and arguments
                        tool_data = section.strip().split("\n", 1)[0].strip()
                        if "{" in tool_data:
                            tool_json = json.loads(tool_data)
                            tool_calls.append({
                                "name": tool_json.get("name", ""),
                                "arguments": tool_json.get("arguments", {})
                            })
                    except Exception as e:
                        logger.error(f"Error parsing tool call from Gemini: {str(e)}")
            
            return {
                "content": content,
                "tool_calls": tool_calls
            }
            
        except Exception as e:
            logger.error(f"Error generating response from Gemini: {str(e)}")
            return {
                "content": f"Error generating response: {str(e)}",
                "tool_calls": []
            }
    
    def generate_text(self, prompt: str) -> str:
        """
        Generate text from a simple prompt using Gemini.
        
        Args:
            prompt: Text prompt
            
        Returns:
            Generated text
        """
        try:
            response = self.client.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating text from Gemini: {str(e)}")
            return f"Error generating text: {str(e)}"


class GroqProvider(BaseLLMProvider):
    """Groq API provider implementation (uses OpenAI-compatible API)."""
    
    def __init__(self, config: Dict[str, Any] = {}):
        """
        Initialize Groq provider.
        
        Args:
            config: Configuration dictionary for Groq
        """
        super().__init__(config)
        
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not available (required for Groq)")
        
        self.api_key = config.get("api_key", os.environ.get("GROQ_API_KEY"))
        
        if not self.api_key:
            raise ValueError("Groq API key not provided")
        
        self.model = config.get("model", "llama3-70b-8192")
        self.client = openai.OpenAI(api_key=self.api_key, base_url="https://api.groq.com/openai/v1")
    
    def generate_response(
        self, 
        system_prompt: str, 
        conversation: List[Dict[str, Any]], 
        tools: List[Dict[str, Any]] = [],
        enriched_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a response from Groq.
        
        Args:
            system_prompt: System prompt for the LLM
            conversation: Conversation history
            tools: Available tools for the LLM
            enriched_prompt: Optional enriched prompt from knowledge base
            
        Returns:
            Dictionary containing the response
        """
        try:
            # Format messages for Groq (OpenAI-compatible)
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history
            for message in conversation:
                role = message.get("role", "user")
                content = message.get("content", "")
                
                if role in ["user", "assistant", "system"]:
                    messages.append({"role": role, "content": content})
            
            # If we have an enriched prompt, replace the last user message
            if enriched_prompt and messages[-1]["role"] == "user":
                messages[-1]["content"] = enriched_prompt
            
            # Generate response
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            # Note: Groq may not support tools in the same way as OpenAI
            response = self.client.chat.completions.create(**kwargs)
            
            # Extract response content
            content = response.choices[0].message.content or ""
            
            # Groq doesn't support tool calls directly, so we'll return an empty list
            tool_calls = []
            
            return {
                "content": content,
                "tool_calls": tool_calls
            }
            
        except Exception as e:
            logger.error(f"Error generating response from Groq: {str(e)}")
            return {
                "content": f"Error generating response: {str(e)}",
                "tool_calls": []
            }
    
    def generate_text(self, prompt: str) -> str:
        """
        Generate text from a simple prompt using Groq.
        
        Args:
            prompt: Text prompt
            
        Returns:
            Generated text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content or ""
            
        except Exception as e:
            logger.error(f"Error generating text from Groq: {str(e)}")
            return f"Error generating text: {str(e)}"


class BedrockProvider(BaseLLMProvider):
    """AWS Bedrock API provider implementation."""
    
    def __init__(self, config: Dict[str, Any] = {}):
        """
        Initialize AWS Bedrock provider.
        
        Args:
            config: Configuration dictionary for Bedrock
        """
        super().__init__(config)
        
        if not BEDROCK_AVAILABLE:
            raise ImportError("Boto3 library not available (required for AWS Bedrock)")
        
        self.region = config.get("region", os.environ.get("AWS_REGION", "us-east-1"))
        self.model = config.get("model", "anthropic.claude-3-sonnet-20240229-v1:0")
        
        # Create Bedrock client
        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name=self.region
        )
    
    def generate_response(
        self, 
        system_prompt: str, 
        conversation: List[Dict[str, Any]], 
        tools: List[Dict[str, Any]] = [],
        enriched_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a response from AWS Bedrock.
        
        Args:
            system_prompt: System prompt for the LLM
            conversation: Conversation history
            tools: Available tools for the LLM
            enriched_prompt: Optional enriched prompt from knowledge base
            
        Returns:
            Dictionary containing the response
        """
        try:
            # Format messages based on the model provider
            if "anthropic.claude" in self.model:
                # Format for Claude models
                messages = [{"role": "system", "content": system_prompt}]
                
                # Add conversation history
                for message in conversation:
                    role = message.get("role", "user")
                    content = message.get("content", "")
                    
                    if role == "user":
                        messages.append({"role": "user", "content": content})
                    elif role == "assistant":
                        messages.append({"role": "assistant", "content": content})
                
                # If we have an enriched prompt, replace the last user message
                if enriched_prompt and messages[-1]["role"] == "user":
                    messages[-1]["content"] = enriched_prompt
                
                # Prepare request body
                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "messages": messages
                }
                
                # Invoke model
                response = self.client.invoke_model(
                    modelId=self.model,
                    body=json.dumps(body)
                )
                
                # Parse response
                response_body = json.loads(response["body"].read().decode("utf-8"))
                content = response_body.get("content", [{"text": "No response"}])[0].get("text", "")
                
                return {
                    "content": content,
                    "tool_calls": []  # Claude via Bedrock doesn't support tool calls in the same way
                }
                
            else:
                # Generic format for other models
                prompt = f"{system_prompt}\n\n"
                
                for message in conversation:
                    role = message.get("role", "user")
                    content = message.get("content", "")
                    
                    if role == "user":
                        prompt += f"User: {content}\n"
                    elif role == "assistant":
                        prompt += f"Assistant: {content}\n"
                
                # If we have an enriched prompt, add it
                if enriched_prompt:
                    prompt += f"\nAdditional context: {enriched_prompt}\n"
                
                prompt += "\nAssistant: "
                
                # Prepare request body
                body = {
                    "prompt": prompt,
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature
                }
                
                # Invoke model
                response = self.client.invoke_model(
                    modelId=self.model,
                    body=json.dumps(body)
                )
                
                # Parse response
                response_body = json.loads(response["body"].read().decode("utf-8"))
                content = response_body.get("completion", "")
                
                return {
                    "content": content,
                    "tool_calls": []
                }
            
        except Exception as e:
            logger.error(f"Error generating response from AWS Bedrock: {str(e)}")
            return {
                "content": f"Error generating response: {str(e)}",
                "tool_calls": []
            }
    
    def generate_text(self, prompt: str) -> str:
        """
        Generate text from a simple prompt using AWS Bedrock.
        
        Args:
            prompt: Text prompt
            
        Returns:
            Generated text
        """
        try:
            if "anthropic.claude" in self.model:
                # Format for Claude models
                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
                
                # Invoke model
                response = self.client.invoke_model(
                    modelId=self.model,
                    body=json.dumps(body)
                )
                
                # Parse response
                response_body = json.loads(response["body"].read().decode("utf-8"))
                return response_body.get("content", [{"text": "No response"}])[0].get("text", "")
                
            else:
                # Generic format for other models
                body = {
                    "prompt": prompt,
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature
                }
                
                # Invoke model
                response = self.client.invoke_model(
                    modelId=self.model,
                    body=json.dumps(body)
                )
                
                # Parse response
                response_body = json.loads(response["body"].read().decode("utf-8"))
                return response_body.get("completion", "")
            
        except Exception as e:
            logger.error(f"Error generating text from AWS Bedrock: {str(e)}")
            return f"Error generating text: {str(e)}"


class DummyProvider(BaseLLMProvider):
    """Dummy LLM provider for testing."""
    
    def __init__(self, config: Dict[str, Any] = {}):
        """
        Initialize dummy provider.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
    
    def generate_response(
        self, 
        system_prompt: str, 
        conversation: List[Dict[str, Any]], 
        tools: List[Dict[str, Any]] = [],
        enriched_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a dummy response.
        
        Args:
            system_prompt: System prompt for the LLM
            conversation: Conversation history
            tools: Available tools for the LLM
            enriched_prompt: Optional enriched prompt from knowledge base
            
        Returns:
            Dictionary containing the response
        """
        # Get the last user message
        last_user_message = ""
        for message in reversed(conversation):
            if message.get("role") == "user":
                last_user_message = message.get("content", "")
                break
        
        # If we have an enriched prompt, use it
        if enriched_prompt:
            last_user_message = enriched_prompt
        
        # Generate a simple echo response
        response = f"Echo: {last_user_message}"
        
        # If tools are available, simulate a tool call
        tool_calls = []
        if tools and "use tool" in last_user_message.lower():
            tool = tools[0]
            tool_calls.append({
                "name": tool.get("name", ""),
                "arguments": {"text": last_user_message}
            })
        
        return {
            "content": response,
            "tool_calls": tool_calls
        }
    
    def generate_text(self, prompt: str) -> str:
        """
        Generate text from a simple prompt.
        
        Args:
            prompt: Text prompt
            
        Returns:
            Generated text
        """
        return f"Echo: {prompt}"


def get_llm_provider(config: Dict[str, Any] = {}) -> BaseLLMProvider:
    """
    Factory function to create an LLM provider based on configuration.
    
    Args:
        config: LLM provider configuration dictionary
        
    Returns:
        LLM provider instance
    """
    provider_type = config.get("provider", "openai").lower()
    
    try:
        if provider_type == "openai":
            return OpenAIProvider(config)
        elif provider_type == "gemini":
            return GeminiProvider(config)
        elif provider_type == "groq":
            return GroqProvider(config)
        elif provider_type == "bedrock":
            return BedrockProvider(config)
        elif provider_type == "dummy":
            return DummyProvider(config)
        else:
            logger.warning(f"Unknown LLM provider type: {provider_type}, falling back to dummy provider")
            return DummyProvider(config)
    except Exception as e:
        logger.error(f"Error creating LLM provider: {str(e)}, falling back to dummy provider")
        return DummyProvider(config)
