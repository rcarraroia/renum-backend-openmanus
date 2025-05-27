"""
Social media post generator tool for the Content Creation agent.

This module provides tools for generating social media posts based on user prompts.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Any

from app.tool.base import BaseTool
from app.tool.content_creation.content_store import ContentStore, Content


class SocialMediaPostTool(BaseTool):
    """Tool for generating social media posts."""
    
    name = "create_social_media_post"
    description = "Generate a social media post with the given theme, keywords, and platform."
    parameters = {
        "type": "object",
        "properties": {
            "theme": {
                "type": "string",
                "description": "Main theme or topic of the post"
            },
            "keywords": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "List of keywords to include in the post"
            },
            "platform": {
                "type": "string",
                "description": "Target social media platform (twitter, linkedin, instagram, facebook)",
                "default": "linkedin"
            },
            "tone": {
                "type": "string",
                "description": "Tone of the post (professional, casual, inspirational, informative)",
                "default": "professional"
            },
            "include_hashtags": {
                "type": "boolean",
                "description": "Whether to include hashtags",
                "default": True
            },
            "include_call_to_action": {
                "type": "boolean",
                "description": "Whether to include a call to action",
                "default": True
            }
        },
        "required": ["theme", "keywords", "platform"]
    }
    
    def __init__(self, content_store: ContentStore):
        """
        Initialize the SocialMediaPostTool.
        
        Args:
            content_store: ContentStore instance for persistence
        """
        super().__init__()
        self.content_store = content_store
        
        # Platform-specific constraints
        self.platform_constraints = {
            "twitter": {
                "max_length": 280,
                "hashtag_limit": 3,
                "ideal_length": 240
            },
            "linkedin": {
                "max_length": 3000,
                "hashtag_limit": 5,
                "ideal_length": 1200
            },
            "instagram": {
                "max_length": 2200,
                "hashtag_limit": 10,
                "ideal_length": 1000
            },
            "facebook": {
                "max_length": 5000,
                "hashtag_limit": 3,
                "ideal_length": 1500
            }
        }
    
    async def execute(
        self,
        theme: str,
        keywords: List[str],
        platform: str = "linkedin",
        tone: str = "professional",
        include_hashtags: bool = True,
        include_call_to_action: bool = True
    ) -> Dict[str, Any]:
        """
        Execute the tool to generate a social media post.
        
        Args:
            theme: Main theme or topic of the post
            keywords: List of keywords to include in the post
            platform: Target social media platform
            tone: Tone of the post
            include_hashtags: Whether to include hashtags
            include_call_to_action: Whether to include a call to action
            
        Returns:
            Dictionary with the generated social media post
        """
        # Validate inputs
        if not theme:
            return {
                "success": False,
                "error": "Theme cannot be empty."
            }
        
        if not keywords or len(keywords) == 0:
            return {
                "success": False,
                "error": "At least one keyword must be provided."
            }
        
        # Normalize platform
        platform = platform.lower()
        valid_platforms = ["twitter", "linkedin", "instagram", "facebook"]
        if platform not in valid_platforms:
            platform = "linkedin"
        
        # Normalize tone
        tone = tone.lower()
        valid_tones = ["professional", "casual", "inspirational", "informative"]
        if tone not in valid_tones:
            tone = "professional"
        
        # Generate the post
        post_body = self._generate_post_body(
            theme=theme,
            keywords=keywords,
            platform=platform,
            tone=tone,
            include_hashtags=include_hashtags,
            include_call_to_action=include_call_to_action
        )
        
        # Create a title for the post
        post_title = self._generate_post_title(theme, platform, tone)
        
        # Store the generated post
        metadata = {
            "platform": platform,
            "tone": tone,
            "keywords": keywords,
            "hashtags": self._generate_hashtags(keywords, platform) if include_hashtags else []
        }
        
        content = self.content_store.create_content(
            content_type="social_post",
            title=post_title,
            body=post_body,
            metadata=metadata
        )
        
        return {
            "success": True,
            "post": {
                "id": content.id,
                "title": post_title,
                "body": post_body,
                "platform": platform,
                "created_at": content.created_at,
                "metadata": metadata
            }
        }
    
    def _generate_post_title(self, theme: str, platform: str, tone: str) -> str:
        """
        Generate a title for the post based on the theme, platform, and tone.
        
        Args:
            theme: Main theme of the post
            platform: Target social media platform
            tone: Tone of the post
            
        Returns:
            Generated post title
        """
        # For most platforms, the post itself doesn't have a separate title
        # This is mainly for storage/reference purposes
        
        if platform == "linkedin" and tone == "professional":
            return f"Professional LinkedIn Post: {theme}"
        
        if platform == "twitter":
            return f"Tweet: {theme}"
        
        if platform == "instagram":
            return f"Instagram Post: {theme}"
        
        if platform == "facebook":
            return f"Facebook Post: {theme}"
        
        # Default
        return f"{platform.capitalize()} Post: {theme}"
    
    def _generate_post_body(
        self,
        theme: str,
        keywords: List[str],
        platform: str,
        tone: str,
        include_hashtags: bool,
        include_call_to_action: bool
    ) -> str:
        """
        Generate the post body based on the provided parameters.
        
        Args:
            theme: Main theme of the post
            keywords: List of keywords to include
            platform: Target social media platform
            tone: Tone of the post
            include_hashtags: Whether to include hashtags
            include_call_to_action: Whether to include a call to action
            
        Returns:
            Generated post body
        """
        constraints = self.platform_constraints.get(platform, self.platform_constraints["linkedin"])
        
        # Start building the post
        post_parts = []
        
        # Add introduction based on tone and theme
        intro = self._generate_introduction(theme, tone, platform)
        post_parts.append(intro)
        
        # Add main content incorporating keywords
        main_content = self._generate_main_content(theme, keywords, tone, platform)
        post_parts.append(main_content)
        
        # Add call to action if requested
        if include_call_to_action:
            cta = self._generate_call_to_action(tone, platform)
            post_parts.append(cta)
        
        # Join all parts
        post_body = "\n\n".join(post_parts)
        
        # Add hashtags if requested
        if include_hashtags:
            hashtags = self._generate_hashtags(keywords, platform)
            hashtag_text = " ".join(hashtags)
            
            # For Twitter, we might want to integrate hashtags into the text
            if platform == "twitter":
                # Check if adding hashtags would exceed the limit
                if len(post_body) + len(hashtag_text) + 1 > constraints["max_length"]:
                    # Trim the post body to fit hashtags
                    max_body_length = constraints["max_length"] - len(hashtag_text) - 1
                    post_body = post_body[:max_body_length - 3] + "..."
                
                post_body = f"{post_body}\n\n{hashtag_text}"
            else:
                post_body = f"{post_body}\n\n{hashtag_text}"
        
        # Ensure the post doesn't exceed platform limits
        if len(post_body) > constraints["max_length"]:
            post_body = post_body[:constraints["max_length"] - 3] + "..."
        
        return post_body
    
    def _generate_introduction(self, theme: str, tone: str, platform: str) -> str:
        """
        Generate an introduction for the post based on theme, tone, and platform.
        
        Args:
            theme: Main theme of the post
            tone: Tone of the post
            platform: Target social media platform
            
        Returns:
            Introduction text
        """
        constraints = self.platform_constraints.get(platform, self.platform_constraints["linkedin"])
        
        if tone == "professional":
            intros = [
                f"I'm excited to share some thoughts on {theme}.",
                f"Recently, I've been thinking about {theme} and its implications.",
                f"Let's discuss {theme} and why it matters."
            ]
            return intros[hash(theme) % len(intros)]
        
        if tone == "casual":
            intros = [
                f"Hey everyone! Just wanted to share some thoughts on {theme}! 😊",
                f"So I've been thinking about {theme} lately...",
                f"Anyone else interested in {theme}? Here's my take!"
            ]
            return intros[hash(theme) % len(intros)]
        
        if tone == "inspirational":
            intros = [
                f"There's something truly transformative about {theme}.",
                f"The journey toward understanding {theme} begins with a single step.",
                f"Never underestimate the power of {theme} to change perspectives."
            ]
            return intros[hash(theme) % len(intros)]
        
        if tone == "informative":
            intros = [
                f"Here are some key insights about {theme} you might find valuable:",
                f"Did you know these facts about {theme}?",
                f"Understanding {theme} requires looking at several important factors:"
            ]
            return intros[hash(theme) % len(intros)]
        
        # Default
        return f"Let's talk about {theme}."
    
    def _generate_main_content(self, theme: str, keywords: List[str], tone: str, platform: str) -> str:
        """
        Generate the main content of the post incorporating keywords.
        
        Args:
            theme: Main theme of the post
            keywords: List of keywords to include
            tone: Tone of the post
            platform: Target social media platform
            
        Returns:
            Main content text
        """
        constraints = self.platform_constraints.get(platform, self.platform_constraints["linkedin"])
        
        # For Twitter, keep it very concise
        if platform == "twitter":
            # Just incorporate the keywords into a short sentence or two
            keyword_phrase = ", ".join(keywords[:-1]) + (" and " + keywords[-1] if len(keywords) > 1 else keywords[0])
            
            if tone == "professional":
                return f"When considering {theme}, it's important to focus on {keyword_phrase}. These elements drive success and innovation in this area."
            
            if tone == "casual":
                return f"I'm really into {keyword_phrase} when it comes to {theme}! What about you? 🤔"
            
            if tone == "inspirational":
                return f"{keyword_phrase.title()} - these aren't just words, they're the building blocks of success in {theme}. Embrace them daily!"
            
            if tone == "informative":
                return f"Research shows that {keyword_phrase} are key factors in understanding {theme}. The data supports this connection."
            
            # Default
            return f"{theme} is all about {keyword_phrase}. Keep this in mind!"
        
        # For other platforms, we can be more verbose
        paragraphs = []
        
        # Create a paragraph for each keyword (or group of keywords for longer lists)
        if len(keywords) <= 3 or platform == "linkedin":
            # One paragraph per keyword
            for keyword in keywords:
                if tone == "professional":
                    para = f"{keyword.title()} is a critical aspect of {theme}. It provides structure and direction for strategic decision-making."
                elif tone == "casual":
                    para = f"I really love how {keyword} fits into {theme}! It's such an interesting connection, don't you think? 😃"
                elif tone == "inspirational":
                    para = f"Embrace {keyword} as you journey through {theme}. It will illuminate your path and strengthen your resolve."
                elif tone == "informative":
                    para = f"Studies have shown that {keyword} plays a significant role in {theme}. This correlation has been demonstrated across multiple contexts."
                else:
                    para = f"{keyword} is an important part of {theme}."
                
                paragraphs.append(para)
        else:
            # Group keywords for platforms with shorter ideal lengths
            keyword_groups = [keywords[i:i+3] for i in range(0, len(keywords), 3)]
            
            for group in keyword_groups:
                keyword_phrase = ", ".join(group[:-1]) + (" and " + group[-1] if len(group) > 1 else group[0])
                
                if tone == "professional":
                    para = f"When examining {theme}, consider the impact of {keyword_phrase}. These factors contribute significantly to outcomes and performance metrics."
                elif tone == "casual":
                    para = f"I've been playing around with {keyword_phrase} in relation to {theme}. Such a cool combination of ideas! 🤩"
                elif tone == "inspirational":
                    para = f"The synergy between {keyword_phrase} creates a powerful foundation for growth in {theme}. Let these concepts guide your journey."
                elif tone == "informative":
                    para = f"Analysis reveals that {keyword_phrase} are interconnected elements within {theme}. Understanding these relationships provides valuable insights."
                else:
                    para = f"{keyword_phrase} are key components of {theme}."
                
                paragraphs.append(para)
        
        # Join paragraphs with appropriate spacing
        return "\n\n".join(paragraphs)
    
    def _generate_call_to_action(self, tone: str, platform: str) -> str:
        """
        Generate a call to action based on tone and platform.
        
        Args:
            tone: Tone of the post
            platform: Target social media platform
            
        Returns:
            Call to action text
        """
        if tone == "professional":
            ctas = [
                "What are your thoughts on this topic? Share your perspective in the comments.",
                "I'd love to hear your experiences. Connect with me to continue the conversation.",
                "How has this affected your work? Let me know in the comments below."
            ]
            return ctas[hash(platform) % len(ctas)]
        
        if tone == "casual":
            ctas = [
                "Drop a comment with your thoughts! 👇",
                "Tag someone who needs to see this! 👀",
                "Like if you agree, comment if you don't! 😄"
            ]
            return ctas[hash(platform) % len(ctas)]
        
        if tone == "inspirational":
            ctas = [
                "Take the first step today. Share your journey in the comments.",
                "What inspires you? Let's create a community of inspiration.",
                "Tag someone who needs this message today. Together, we rise."
            ]
            return ctas[hash(platform) % len(ctas)]
        
        if tone == "informative":
            ctas = [
                "For more information, check out the link in my bio/profile.",
                "What other topics would you like to learn about? Let me know below.",
                "Share this with someone who might find it valuable."
            ]
            return ctas[hash(platform) % len(ctas)]
        
        # Default
        return "Let me know what you think in the comments!"
    
    def _generate_hashtags(self, keywords: List[str], platform: str) -> List[str]:
        """
        Generate hashtags based on keywords and platform constraints.
        
        Args:
            keywords: List of keywords to base hashtags on
            platform: Target social media platform
            
        Returns:
            List of hashtags
        """
        constraints = self.platform_constraints.get(platform, self.platform_constraints["linkedin"])
        hashtag_limit = constraints["hashtag_limit"]
        
        # Convert keywords to hashtags
        hashtags = []
        for keyword in keywords:
            # Remove special characters and spaces
            clean_keyword = re.sub(r'[^\w\s]', '', keyword)
            # Replace spaces with nothing (camelCase)
            hashtag = "#" + "".join(word.capitalize() for word in clean_keyword.split())
            hashtags.append(hashtag)
        
        # Add platform-specific popular hashtags
        if platform == "linkedin":
            popular_hashtags = ["#ProfessionalDevelopment", "#Innovation", "#Leadership"]
        elif platform == "twitter":
            popular_hashtags = ["#TrendingNow", "#ThoughtLeadership"]
        elif platform == "instagram":
            popular_hashtags = ["#Instagood", "#Photooftheday", "#Follow"]
        elif platform == "facebook":
            popular_hashtags = ["#Community", "#Share"]
        else:
            popular_hashtags = []
        
        # Combine and limit
        all_hashtags = hashtags + popular_hashtags
        return all_hashtags[:hashtag_limit]
