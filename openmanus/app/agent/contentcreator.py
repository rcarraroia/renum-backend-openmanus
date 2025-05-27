"""
Content Creator agent implementation for the Renum project.

This agent specializes in generating creative content such as email drafts
and social media posts based on user prompts.
"""

from typing import Dict, List, Any, Optional

from app.agent.base import BaseAgent
from app.tool.content_creation import ContentStore, EmailGeneratorTool, SocialMediaPostTool


class ContentCreatorAgent(BaseAgent):
    """
    Agent specialized in generating creative content.
    
    This agent can create various types of content including email drafts
    and social media posts based on natural language prompts.
    """
    
    def __init__(self, model: str = "gpt-4", temperature: float = 0.7):
        """
        Initialize the ContentCreatorAgent.
        
        Args:
            model: LLM model to use
            temperature: Temperature for generation (higher = more creative)
        """
        super().__init__(model=model, temperature=temperature)
        
        # Initialize content store
        self.content_store = ContentStore()
        
        # Register tools
        self._register_tools()
        
        # Set system prompt
        self._set_system_prompt()
    
    def _register_tools(self) -> None:
        """Register all tools for the content creator agent."""
        # Email generator tool
        email_tool = EmailGeneratorTool(self.content_store)
        self.register_tool(email_tool)
        
        # Social media post tool
        social_tool = SocialMediaPostTool(self.content_store)
        self.register_tool(social_tool)
    
    def _set_system_prompt(self) -> None:
        """Set the system prompt for the content creator agent."""
        system_prompt = """
        You are a professional content creator specializing in crafting engaging and effective written content.
        Your expertise includes writing email drafts, social media posts, and other short-form content.
        
        When responding to user requests:
        1. Analyze the user's intent and identify the type of content they need
        2. Extract key information such as recipients, topics, themes, and key points
        3. Use the appropriate tool to generate the requested content
        4. Provide a brief explanation of your approach and any recommendations
        
        For emails:
        - Consider the recipient, topic, and key points
        - Adapt the tone appropriately (formal, professional, friendly, urgent)
        - Structure with clear introduction, body, and conclusion
        
        For social media:
        - Consider the platform-specific constraints and best practices
        - Adapt content for the target platform (Twitter, LinkedIn, Instagram, Facebook)
        - Use appropriate tone and style for the platform and audience
        - Include relevant hashtags when appropriate
        
        Always aim to be helpful, clear, and responsive to the user's specific needs.
        """
        
        self.set_system_prompt(system_prompt)
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        """
        Process a user message and generate appropriate content.
        
        Args:
            message: User message requesting content generation
            
        Returns:
            Dictionary with the agent's response and any generated content
        """
        # Process the message using the LLM and tools
        response = await self.generate_response(message)
        
        # Extract any content IDs from the response for reference
        content_ids = self._extract_content_ids(response)
        
        # Retrieve the full content objects if any were created
        contents = []
        for content_id in content_ids:
            content = self.content_store.get_content(content_id)
            if content:
                contents.append(content.to_dict())
        
        return {
            "response": response,
            "contents": contents
        }
    
    def _extract_content_ids(self, response: str) -> List[str]:
        """
        Extract content IDs from the agent's response.
        
        Args:
            response: Agent's response text
            
        Returns:
            List of content IDs mentioned in the response
        """
        # Simple regex pattern to find content IDs
        # This assumes IDs follow patterns like "email-12345678" or "social_post-12345678"
        import re
        
        patterns = [
            r"email-[a-f0-9]{8}",
            r"social_post-[a-f0-9]{8}"
        ]
        
        content_ids = []
        for pattern in patterns:
            matches = re.findall(pattern, response)
            content_ids.extend(matches)
        
        return content_ids
    
    async def get_all_contents(self, content_type: Optional[str] = None, search_term: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all contents from the store, optionally filtered.
        
        Args:
            content_type: Filter by content type (email, social_post)
            search_term: Filter by search term in title or body
            
        Returns:
            List of content dictionaries
        """
        contents = self.content_store.get_contents(content_type, search_term)
        return [content.to_dict() for content in contents]
