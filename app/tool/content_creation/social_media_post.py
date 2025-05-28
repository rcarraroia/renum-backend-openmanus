"""
Social Media Post Tool for OpenManus.

This tool provides functionality for creating social media posts based on
theme, keywords, and target platform.
"""

import logging
from typing import Dict, Any, List, Optional

from app.tool.base import BaseTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SocialMediaPostTool(BaseTool):
    """
    Tool for creating social media posts based on specified parameters.
    
    This tool generates platform-specific content with appropriate formatting,
    hashtags, and structure based on the provided parameters.
    """
    
    name = "create_social_media_post"
    description = "Create a social media post based on theme, keywords, and platform"
    
    # Platform-specific constraints
    PLATFORM_CONSTRAINTS = {
        "twitter": {"max_length": 280, "hashtag_limit": 5},
        "linkedin": {"max_length": 3000, "hashtag_limit": 10},
        "instagram": {"max_length": 2200, "hashtag_limit": 30},
        "facebook": {"max_length": 5000, "hashtag_limit": 8}
    }
    
    def __init__(self):
        """Initialize the SocialMediaPostTool."""
        super().__init__()
        logger.info("SocialMediaPostTool initialized")
    
    async def _arun(
        self,
        theme: str,
        keywords: List[str],
        platform: str,
        tone: Optional[str] = "professional",
        include_hashtags: Optional[bool] = True,
        include_call_to_action: Optional[bool] = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a social media post based on the provided parameters.
        
        Args:
            theme: Main theme or topic of the post
            keywords: List of keywords to incorporate
            platform: Target social media platform (twitter, linkedin, instagram, facebook)
            tone: Tone of the post (professional, friendly, formal, casual, promotional)
            include_hashtags: Whether to include hashtags
            include_call_to_action: Whether to include a call to action
            
        Returns:
            Dictionary containing the generated post and metadata
        """
        logger.info(f"Creating social media post for platform: {platform}, theme: {theme}")
        
        # Validate inputs
        if not theme:
            return {"error": "Theme is required"}
        
        if not keywords or len(keywords) == 0:
            return {"error": "At least one keyword is required"}
        
        # Normalize platform
        platform = platform.lower() if platform else "twitter"
        valid_platforms = list(self.PLATFORM_CONSTRAINTS.keys())
        if platform not in valid_platforms:
            return {"error": f"Invalid platform. Choose from: {', '.join(valid_platforms)}"}
        
        # Normalize tone
        tone = tone.lower() if tone else "professional"
        valid_tones = ["professional", "friendly", "formal", "casual", "promotional"]
        if tone not in valid_tones:
            tone = "professional"
        
        # Get platform constraints
        constraints = self.PLATFORM_CONSTRAINTS[platform]
        
        # Generate post content
        content = self._generate_content(theme, keywords, platform, tone, constraints)
        
        # Generate hashtags if requested
        hashtags = ""
        if include_hashtags:
            hashtags = self._generate_hashtags(keywords, platform, constraints["hashtag_limit"])
        
        # Generate call to action if requested
        call_to_action = ""
        if include_call_to_action:
            call_to_action = self._generate_call_to_action(platform, tone)
        
        # Assemble the complete post
        post = content
        if call_to_action:
            post += f"\n\n{call_to_action}"
        if hashtags:
            post += f"\n\n{hashtags}"
        
        # Ensure post is within platform constraints
        if len(post) > constraints["max_length"]:
            # Truncate content to fit within constraints
            available_length = constraints["max_length"] - len(hashtags) - len(call_to_action) - 4  # 4 for newlines
            content = content[:available_length - 3] + "..."
            
            # Reassemble the post
            post = content
            if call_to_action:
                post += f"\n\n{call_to_action}"
            if hashtags:
                post += f"\n\n{hashtags}"
        
        # Return the result
        return {
            "post": post,
            "platform": platform,
            "metadata": {
                "theme": theme,
                "tone": tone,
                "keywords_count": len(keywords),
                "length": len(post),
                "max_length": constraints["max_length"],
                "has_hashtags": bool(hashtags),
                "has_call_to_action": bool(call_to_action)
            }
        }
    
    def _generate_content(
        self,
        theme: str,
        keywords: List[str],
        platform: str,
        tone: str,
        constraints: Dict[str, Any]
    ) -> str:
        """
        Generate the main content of the post based on parameters.
        
        Args:
            theme: Main theme of the post
            keywords: List of keywords to incorporate
            platform: Target social media platform
            tone: Tone of the post
            constraints: Platform-specific constraints
            
        Returns:
            Generated post content
        """
        # Implement platform-specific content generation
        if platform == "twitter":
            return self._generate_twitter_content(theme, keywords, tone)
        elif platform == "linkedin":
            return self._generate_linkedin_content(theme, keywords, tone)
        elif platform == "instagram":
            return self._generate_instagram_content(theme, keywords, tone)
        elif platform == "facebook":
            return self._generate_facebook_content(theme, keywords, tone)
        else:
            # Default to generic content
            return self._generate_generic_content(theme, keywords, tone)
    
    def _generate_twitter_content(self, theme: str, keywords: List[str], tone: str) -> str:
        """Generate Twitter-specific content."""
        # Twitter content is concise and to the point
        if tone == "promotional":
            return f"Excited to share about {theme}! {' '.join(keywords[:2])}"
        elif tone == "friendly" or tone == "casual":
            return f"Just thinking about {theme} today. {' '.join(keywords[:2])}"
        elif tone == "formal":
            return f"An important update regarding {theme}. {' '.join(keywords[:2])}"
        else:  # professional (default)
            return f"Sharing insights on {theme}: {' '.join(keywords[:2])}"
    
    def _generate_linkedin_content(self, theme: str, keywords: List[str], tone: str) -> str:
        """Generate LinkedIn-specific content."""
        # LinkedIn content is professional and detailed
        intro = ""
        if tone == "promotional":
            intro = f"I'm excited to share our latest update on {theme}."
        elif tone == "friendly" or tone == "casual":
            intro = f"I've been thinking about {theme} lately and wanted to share some thoughts."
        elif tone == "formal":
            intro = f"I would like to present an important update regarding {theme}."
        else:  # professional (default)
            intro = f"I'm sharing some professional insights on {theme} today."
        
        # Add a body with keywords
        body = f"\n\nThis topic encompasses {', '.join(keywords[:-1])}"
        if len(keywords) > 1:
            body += f", and {keywords[-1]}."
        else:
            body += "."
        
        return intro + body
    
    def _generate_instagram_content(self, theme: str, keywords: List[str], tone: str) -> str:
        """Generate Instagram-specific content."""
        # Instagram content is visual and emotional
        if tone == "promotional":
            return f"✨ Check out our latest on {theme}! ✨\n\n{' '.join(keywords[:3])}"
        elif tone == "friendly" or tone == "casual":
            return f"Vibes: {theme} 💫\n\n{' '.join(keywords[:3])}"
        elif tone == "formal":
            return f"Presenting: {theme}\n\n{' '.join(keywords[:3])}"
        else:  # professional (default)
            return f"{theme}: A professional perspective\n\n{' '.join(keywords[:3])}"
    
    def _generate_facebook_content(self, theme: str, keywords: List[str], tone: str) -> str:
        """Generate Facebook-specific content."""
        # Facebook content is conversational and community-oriented
        intro = ""
        if tone == "promotional":
            intro = f"Hey everyone! We're excited to share our latest update on {theme}."
        elif tone == "friendly" or tone == "casual":
            intro = f"Hey friends! I've been thinking about {theme} lately."
        elif tone == "formal":
            intro = f"Dear community, I would like to present an important update regarding {theme}."
        else:  # professional (default)
            intro = f"I wanted to share some thoughts on {theme} with this community."
        
        # Add a body with keywords
        body = f"\n\nThis topic relates to {', '.join(keywords[:-1])}"
        if len(keywords) > 1:
            body += f", and {keywords[-1]}."
        else:
            body += "."
        
        return intro + body
    
    def _generate_generic_content(self, theme: str, keywords: List[str], tone: str) -> str:
        """Generate generic content for any platform."""
        intro = f"Sharing thoughts on {theme}."
        body = f"\n\nKey points: {', '.join(keywords)}."
        return intro + body
    
    def _generate_hashtags(self, keywords: List[str], platform: str, hashtag_limit: int) -> str:
        """
        Generate hashtags based on keywords and platform.
        
        Args:
            keywords: List of keywords to convert to hashtags
            platform: Target social media platform
            hashtag_limit: Maximum number of hashtags for the platform
            
        Returns:
            Generated hashtags string
        """
        # Convert keywords to hashtags
        hashtags = []
        for keyword in keywords[:hashtag_limit]:
            # Clean and format the keyword
            clean_keyword = keyword.strip().replace(" ", "").replace("-", "").replace("_", "")
            if clean_keyword:
                hashtags.append(f"#{clean_keyword}")
        
        # Format hashtags based on platform
        if platform == "twitter" or platform == "linkedin":
            # Space-separated hashtags
            return " ".join(hashtags)
        else:
            # Newline-separated hashtags for Instagram and Facebook
            return "\n".join(hashtags)
    
    def _generate_call_to_action(self, platform: str, tone: str) -> str:
        """
        Generate a call to action based on platform and tone.
        
        Args:
            platform: Target social media platform
            tone: Tone of the post
            
        Returns:
            Generated call to action
        """
        # Implement platform-specific calls to action
        if platform == "twitter":
            if tone == "promotional":
                return "RT if you agree!"
            else:
                return "What do you think? Reply below!"
        elif platform == "linkedin":
            if tone == "promotional":
                return "Like and share with your network if you found this valuable."
            else:
                return "I'd love to hear your thoughts in the comments below."
        elif platform == "instagram":
            if tone == "promotional":
                return "Double tap if you agree! 👇"
            else:
                return "Share your thoughts in the comments! 💬"
        elif platform == "facebook":
            if tone == "promotional":
                return "Like and share with friends who might be interested!"
            else:
                return "Let me know what you think in the comments below."
        else:
            return "Let me know your thoughts!"
