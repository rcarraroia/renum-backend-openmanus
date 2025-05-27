"""
Email generator tool for the Content Creation agent.

This module provides tools for generating email drafts based on user prompts.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Any

from app.tool.base import BaseTool
from app.tool.content_creation.content_store import ContentStore, Content


class EmailGeneratorTool(BaseTool):
    """Tool for generating email drafts."""
    
    name = "generate_email_draft"
    description = "Generate an email draft with the given recipient, topic, and key points."
    parameters = {
        "type": "object",
        "properties": {
            "recipient": {
                "type": "string",
                "description": "Name or email address of the recipient"
            },
            "topic": {
                "type": "string",
                "description": "Main topic or subject of the email"
            },
            "key_points": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "List of key points to include in the email"
            },
            "tone": {
                "type": "string",
                "description": "Tone of the email (formal, friendly, urgent, etc.)",
                "default": "professional"
            },
            "include_greeting": {
                "type": "boolean",
                "description": "Whether to include a greeting",
                "default": True
            },
            "include_signature": {
                "type": "boolean",
                "description": "Whether to include a signature",
                "default": True
            }
        },
        "required": ["recipient", "topic", "key_points"]
    }
    
    def __init__(self, content_store: ContentStore):
        """
        Initialize the EmailGeneratorTool.
        
        Args:
            content_store: ContentStore instance for persistence
        """
        super().__init__()
        self.content_store = content_store
    
    async def execute(
        self,
        recipient: str,
        topic: str,
        key_points: List[str],
        tone: str = "professional",
        include_greeting: bool = True,
        include_signature: bool = True
    ) -> Dict[str, Any]:
        """
        Execute the tool to generate an email draft.
        
        Args:
            recipient: Name or email address of the recipient
            topic: Main topic or subject of the email
            key_points: List of key points to include in the email
            tone: Tone of the email (formal, friendly, urgent, etc.)
            include_greeting: Whether to include a greeting
            include_signature: Whether to include a signature
            
        Returns:
            Dictionary with the generated email draft
        """
        # Validate inputs
        if not recipient:
            return {
                "success": False,
                "error": "Recipient cannot be empty."
            }
        
        if not topic:
            return {
                "success": False,
                "error": "Topic cannot be empty."
            }
        
        if not key_points or len(key_points) == 0:
            return {
                "success": False,
                "error": "At least one key point must be provided."
            }
        
        # Normalize tone
        tone = tone.lower()
        valid_tones = ["professional", "formal", "friendly", "casual", "urgent"]
        if tone not in valid_tones:
            tone = "professional"
        
        # Generate the email draft
        email_body = self._generate_email_body(
            recipient=recipient,
            topic=topic,
            key_points=key_points,
            tone=tone,
            include_greeting=include_greeting,
            include_signature=include_signature
        )
        
        # Create a title/subject for the email
        email_subject = self._generate_email_subject(topic, tone)
        
        # Store the generated email
        metadata = {
            "recipient": recipient,
            "tone": tone,
            "key_points": key_points
        }
        
        content = self.content_store.create_content(
            content_type="email",
            title=email_subject,
            body=email_body,
            metadata=metadata
        )
        
        return {
            "success": True,
            "email": {
                "id": content.id,
                "subject": email_subject,
                "body": email_body,
                "recipient": recipient,
                "created_at": content.created_at
            }
        }
    
    def _generate_email_subject(self, topic: str, tone: str) -> str:
        """
        Generate an email subject based on the topic and tone.
        
        Args:
            topic: Main topic of the email
            tone: Tone of the email
            
        Returns:
            Generated email subject
        """
        # For urgent tone, add a prefix
        if tone == "urgent":
            return f"URGENT: {topic}"
        
        # For formal tone, keep it straightforward
        if tone in ["formal", "professional"]:
            return topic
        
        # For friendly/casual tone, make it more conversational
        if tone in ["friendly", "casual"]:
            # If topic ends with punctuation, remove it
            topic = re.sub(r'[.!?]$', '', topic)
            return f"{topic} - let's discuss"
        
        # Default case
        return topic
    
    def _generate_email_body(
        self,
        recipient: str,
        topic: str,
        key_points: List[str],
        tone: str,
        include_greeting: bool,
        include_signature: bool
    ) -> str:
        """
        Generate the email body based on the provided parameters.
        
        Args:
            recipient: Name or email address of the recipient
            topic: Main topic of the email
            key_points: List of key points to include
            tone: Tone of the email
            include_greeting: Whether to include a greeting
            include_signature: Whether to include a signature
            
        Returns:
            Generated email body
        """
        # Extract recipient name (if it's an email address)
        recipient_name = recipient
        if "@" in recipient:
            recipient_name = recipient.split("@")[0]
            # Capitalize and replace dots/underscores with spaces
            recipient_name = recipient_name.replace(".", " ").replace("_", " ")
            recipient_name = recipient_name.title()
        
        # Start building the email
        email_parts = []
        
        # Add greeting if requested
        if include_greeting:
            greeting = self._generate_greeting(recipient_name, tone)
            email_parts.append(greeting)
        
        # Add introduction based on tone and topic
        intro = self._generate_introduction(topic, tone)
        email_parts.append(intro)
        
        # Add key points
        points_text = self._format_key_points(key_points, tone)
        email_parts.append(points_text)
        
        # Add conclusion
        conclusion = self._generate_conclusion(tone)
        email_parts.append(conclusion)
        
        # Add signature if requested
        if include_signature:
            signature = self._generate_signature(tone)
            email_parts.append(signature)
        
        # Join all parts with appropriate spacing
        return "\n\n".join(email_parts)
    
    def _generate_greeting(self, recipient_name: str, tone: str) -> str:
        """
        Generate an appropriate greeting based on tone.
        
        Args:
            recipient_name: Name of the recipient
            tone: Tone of the email
            
        Returns:
            Greeting text
        """
        if tone == "formal":
            return f"Dear {recipient_name},"
        
        if tone == "professional":
            return f"Hello {recipient_name},"
        
        if tone == "urgent":
            return f"Attention {recipient_name},"
        
        if tone == "friendly" or tone == "casual":
            return f"Hi {recipient_name},"
        
        # Default
        return f"Hello {recipient_name},"
    
    def _generate_introduction(self, topic: str, tone: str) -> str:
        """
        Generate an introduction paragraph based on the topic and tone.
        
        Args:
            topic: Main topic of the email
            tone: Tone of the email
            
        Returns:
            Introduction paragraph
        """
        if tone == "formal":
            return f"I am writing to discuss the matter of {topic}."
        
        if tone == "professional":
            return f"I wanted to reach out regarding {topic}."
        
        if tone == "urgent":
            return f"This is an urgent message regarding {topic}. Your immediate attention is required."
        
        if tone == "friendly" or tone == "casual":
            return f"I hope you're doing well! I wanted to chat about {topic}."
        
        # Default
        return f"I'm writing about {topic}."
    
    def _format_key_points(self, key_points: List[str], tone: str) -> str:
        """
        Format the key points based on tone.
        
        Args:
            key_points: List of key points to include
            tone: Tone of the email
            
        Returns:
            Formatted key points text
        """
        # For urgent tone, use bold formatting
        if tone == "urgent":
            points = [f"• IMPORTANT: {point}" for point in key_points]
            return "\n\n".join(points)
        
        # For formal/professional tone, use numbered list
        if tone in ["formal", "professional"]:
            points = [f"{i+1}. {point}" for i, point in enumerate(key_points)]
            return "Here are the key points:\n\n" + "\n".join(points)
        
        # For friendly/casual tone, use bullet points
        if tone in ["friendly", "casual"]:
            points = [f"• {point}" for point in key_points]
            return "I wanted to highlight a few things:\n\n" + "\n".join(points)
        
        # Default
        points = [f"- {point}" for point in key_points]
        return "\n".join(points)
    
    def _generate_conclusion(self, tone: str) -> str:
        """
        Generate a conclusion paragraph based on tone.
        
        Args:
            tone: Tone of the email
            
        Returns:
            Conclusion paragraph
        """
        if tone == "formal":
            return "Please let me know if you require any additional information. I look forward to your response."
        
        if tone == "professional":
            return "Let me know if you have any questions or need more information. I look forward to hearing back from you."
        
        if tone == "urgent":
            return "Please respond as soon as possible. This matter requires immediate attention."
        
        if tone == "friendly" or tone == "casual":
            return "Let me know what you think! Happy to discuss further."
        
        # Default
        return "Looking forward to your response."
    
    def _generate_signature(self, tone: str) -> str:
        """
        Generate an email signature based on tone.
        
        Args:
            tone: Tone of the email
            
        Returns:
            Signature text
        """
        if tone == "formal":
            return "Sincerely,\n[Your Name]\n[Your Position]\n[Your Contact Information]"
        
        if tone == "professional":
            return "Best regards,\n[Your Name]\n[Your Contact Information]"
        
        if tone == "urgent":
            return "Urgently,\n[Your Name]\n[Your Phone Number]"
        
        if tone == "friendly" or tone == "casual":
            return "Cheers,\n[Your Name]"
        
        # Default
        return "Regards,\n[Your Name]"
