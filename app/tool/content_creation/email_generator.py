"""
Email Generator Tool for OpenManus.

This tool provides functionality for generating email drafts based on
recipient, topic, and key points.
"""

import logging
from typing import Dict, Any, List, Optional

from app.tool.base import BaseTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailGeneratorTool(BaseTool):
    """
    Tool for generating email drafts based on specified parameters.
    
    This tool creates structured email drafts with appropriate formatting,
    salutations, and content organization based on the provided parameters.
    """
    
    name = "generate_email_draft"
    description = "Generate an email draft based on recipient, topic, and key points"
    
    def __init__(self):
        """Initialize the EmailGeneratorTool."""
        super().__init__()
        logger.info("EmailGeneratorTool initialized")
    
    async def _arun(
        self,
        recipient: str,
        topic: str,
        key_points: List[str],
        tone: Optional[str] = "professional",
        include_signature: Optional[bool] = True,
        sender_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate an email draft based on the provided parameters.
        
        Args:
            recipient: Name or role of the email recipient
            topic: Main topic or subject of the email
            key_points: List of key points to include in the email body
            tone: Tone of the email (professional, friendly, formal, etc.)
            include_signature: Whether to include a signature
            sender_name: Name to use in the signature (if include_signature is True)
            
        Returns:
            Dictionary containing the generated email draft and metadata
        """
        logger.info(f"Generating email draft for topic: {topic}")
        
        # Validate inputs
        if not recipient:
            return {"error": "Recipient is required"}
        
        if not topic:
            return {"error": "Topic is required"}
        
        if not key_points or len(key_points) == 0:
            return {"error": "At least one key point is required"}
        
        # Normalize tone
        tone = tone.lower() if tone else "professional"
        valid_tones = ["professional", "friendly", "formal", "casual", "urgent"]
        if tone not in valid_tones:
            tone = "professional"
        
        # Generate subject line
        subject = self._generate_subject(topic, tone)
        
        # Generate salutation
        salutation = self._generate_salutation(recipient, tone)
        
        # Generate email body
        body = self._generate_body(topic, key_points, tone)
        
        # Generate closing
        closing = self._generate_closing(tone)
        
        # Generate signature if requested
        signature = ""
        if include_signature:
            signature = self._generate_signature(sender_name)
        
        # Assemble the complete email
        email_draft = f"{salutation}\n\n{body}\n\n{closing}\n{signature}"
        
        # Return the result
        return {
            "email_draft": email_draft,
            "subject": subject,
            "metadata": {
                "recipient": recipient,
                "topic": topic,
                "tone": tone,
                "key_points_count": len(key_points)
            }
        }
    
    def _generate_subject(self, topic: str, tone: str) -> str:
        """
        Generate an appropriate subject line based on the topic and tone.
        
        Args:
            topic: Main topic of the email
            tone: Tone of the email
            
        Returns:
            Generated subject line
        """
        # Implement subject line generation based on tone
        if tone == "urgent":
            return f"URGENT: {topic}"
        elif tone == "formal":
            return f"Regarding: {topic}"
        elif tone == "friendly" or tone == "casual":
            return f"{topic} - Quick Update"
        else:  # professional (default)
            return topic
    
    def _generate_salutation(self, recipient: str, tone: str) -> str:
        """
        Generate an appropriate salutation based on the recipient and tone.
        
        Args:
            recipient: Name or role of the recipient
            tone: Tone of the email
            
        Returns:
            Generated salutation
        """
        # Implement salutation generation based on tone
        if tone == "formal":
            return f"Dear {recipient},"
        elif tone == "friendly" or tone == "casual":
            return f"Hi {recipient},"
        elif tone == "urgent":
            return f"Attention {recipient},"
        else:  # professional (default)
            return f"Hello {recipient},"
    
    def _generate_body(self, topic: str, key_points: List[str], tone: str) -> str:
        """
        Generate the email body based on the topic, key points, and tone.
        
        Args:
            topic: Main topic of the email
            key_points: List of key points to include
            tone: Tone of the email
            
        Returns:
            Generated email body
        """
        # Generate introduction
        if tone == "formal":
            intro = f"I am writing to you regarding {topic}."
        elif tone == "friendly" or tone == "casual":
            intro = f"I wanted to reach out about {topic}."
        elif tone == "urgent":
            intro = f"This is an urgent message regarding {topic}."
        else:  # professional (default)
            intro = f"I'm reaching out regarding {topic}."
        
        # Format key points
        formatted_points = ""
        if len(key_points) == 1:
            # Single point, no need for bullets
            formatted_points = key_points[0]
        else:
            # Multiple points, use bullets
            points_text = "\n".join([f"- {point}" for point in key_points])
            formatted_points = f"Here are the key points:\n\n{points_text}"
        
        # Combine introduction and key points
        body = f"{intro}\n\n{formatted_points}"
        
        return body
    
    def _generate_closing(self, tone: str) -> str:
        """
        Generate an appropriate closing based on the tone.
        
        Args:
            tone: Tone of the email
            
        Returns:
            Generated closing
        """
        # Implement closing generation based on tone
        if tone == "formal":
            return "Yours sincerely,"
        elif tone == "friendly" or tone == "casual":
            return "Cheers,"
        elif tone == "urgent":
            return "Please respond as soon as possible."
        else:  # professional (default)
            return "Best regards,"
    
    def _generate_signature(self, sender_name: Optional[str] = None) -> str:
        """
        Generate a signature based on the sender name.
        
        Args:
            sender_name: Name to use in the signature
            
        Returns:
            Generated signature
        """
        if sender_name:
            return f"\n{sender_name}"
        else:
            return "\n[Your Name]"
