"""
Unit tests for the SocialMediaPostTool.

This module contains tests for the SocialMediaPostTool class and its methods.
"""

import unittest
from unittest.mock import patch, MagicMock

from app.tool.content_creation.social_media_post import SocialMediaPostTool
from app.tool.content_creation.content_store import ContentStore, Content


class TestSocialMediaPostTool(unittest.TestCase):
    """Tests for the SocialMediaPostTool class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock ContentStore
        self.mock_content_store = MagicMock(spec=ContentStore)
        
        # Create a SocialMediaPostTool with the mock store
        self.social_tool = SocialMediaPostTool(self.mock_content_store)
    
    async def test_execute_valid_inputs(self):
        """Test executing the tool with valid inputs."""
        # Set up the mock to return a specific content
        mock_content = MagicMock(spec=Content)
        mock_content.id = "social_post-12345678"
        mock_content.title = "LinkedIn Post: Test Theme"
        mock_content.body = "Test post body"
        mock_content.created_at = "2023-01-01T00:00:00"
        self.mock_content_store.create_content.return_value = mock_content
        
        # Execute the tool
        result = await self.social_tool.execute(
            theme="Test Theme",
            keywords=["keyword1", "keyword2"],
            platform="linkedin",
            tone="professional",
            include_hashtags=True,
            include_call_to_action=True
        )
        
        # Check the result
        self.assertTrue(result["success"])
        self.assertEqual(result["post"]["id"], "social_post-12345678")
        self.assertEqual(result["post"]["platform"], "linkedin")
        
        # Check that create_content was called with the right arguments
        self.mock_content_store.create_content.assert_called_once()
        call_args = self.mock_content_store.create_content.call_args[1]
        self.assertEqual(call_args["content_type"], "social_post")
        self.assertIsNotNone(call_args["title"])
        self.assertIsNotNone(call_args["body"])
        self.assertEqual(call_args["metadata"]["platform"], "linkedin")
        self.assertEqual(call_args["metadata"]["tone"], "professional")
        self.assertEqual(call_args["metadata"]["keywords"], ["keyword1", "keyword2"])
        self.assertIsNotNone(call_args["metadata"]["hashtags"])
    
    async def test_execute_missing_theme(self):
        """Test executing the tool with a missing theme."""
        result = await self.social_tool.execute(
            theme="",
            keywords=["keyword1", "keyword2"],
            platform="linkedin"
        )
        
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Theme cannot be empty.")
        self.mock_content_store.create_content.assert_not_called()
    
    async def test_execute_missing_keywords(self):
        """Test executing the tool with missing keywords."""
        result = await self.social_tool.execute(
            theme="Test Theme",
            keywords=[],
            platform="linkedin"
        )
        
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "At least one keyword must be provided.")
        self.mock_content_store.create_content.assert_not_called()
    
    async def test_execute_invalid_platform(self):
        """Test executing the tool with an invalid platform."""
        # Set up the mock to return a specific content
        mock_content = MagicMock(spec=Content)
        mock_content.id = "social_post-12345678"
        self.mock_content_store.create_content.return_value = mock_content
        
        # Execute the tool with an invalid platform
        result = await self.social_tool.execute(
            theme="Test Theme",
            keywords=["keyword1", "keyword2"],
            platform="invalid_platform"
        )
        
        # Check that the tool defaulted to "linkedin" platform
        self.assertTrue(result["success"])
        self.mock_content_store.create_content.assert_called_once()
        call_args = self.mock_content_store.create_content.call_args[1]
        self.assertEqual(call_args["metadata"]["platform"], "linkedin")
    
    async def test_execute_invalid_tone(self):
        """Test executing the tool with an invalid tone."""
        # Set up the mock to return a specific content
        mock_content = MagicMock(spec=Content)
        mock_content.id = "social_post-12345678"
        self.mock_content_store.create_content.return_value = mock_content
        
        # Execute the tool with an invalid tone
        result = await self.social_tool.execute(
            theme="Test Theme",
            keywords=["keyword1", "keyword2"],
            platform="linkedin",
            tone="invalid_tone"
        )
        
        # Check that the tool defaulted to "professional" tone
        self.assertTrue(result["success"])
        self.mock_content_store.create_content.assert_called_once()
        call_args = self.mock_content_store.create_content.call_args[1]
        self.assertEqual(call_args["metadata"]["tone"], "professional")
    
    def test_generate_post_title(self):
        """Test generating post titles with different platforms and tones."""
        # Test LinkedIn with professional tone
        title = self.social_tool._generate_post_title("Test Theme", "linkedin", "professional")
        self.assertEqual(title, "Professional LinkedIn Post: Test Theme")
        
        # Test Twitter
        title = self.social_tool._generate_post_title("Test Theme", "twitter", "casual")
        self.assertEqual(title, "Tweet: Test Theme")
        
        # Test Instagram
        title = self.social_tool._generate_post_title("Test Theme", "instagram", "inspirational")
        self.assertEqual(title, "Instagram Post: Test Theme")
        
        # Test Facebook
        title = self.social_tool._generate_post_title("Test Theme", "facebook", "informative")
        self.assertEqual(title, "Facebook Post: Test Theme")
        
        # Test default
        title = self.social_tool._generate_post_title("Test Theme", "unknown", "unknown")
        self.assertEqual(title, "Unknown Post: Test Theme")
    
    def test_generate_introduction(self):
        """Test generating introductions with different tones and platforms."""
        # Test professional tone
        intro = self.social_tool._generate_introduction("Test Theme", "professional", "linkedin")
        self.assertIn("Test Theme", intro)
        
        # Test casual tone
        intro = self.social_tool._generate_introduction("Test Theme", "casual", "twitter")
        self.assertIn("Test Theme", intro)
        self.assertTrue("!" in intro or "😊" in intro)
        
        # Test inspirational tone
        intro = self.social_tool._generate_introduction("Test Theme", "inspirational", "instagram")
        self.assertIn("Test Theme", intro)
        
        # Test informative tone
        intro = self.social_tool._generate_introduction("Test Theme", "informative", "facebook")
        self.assertIn("Test Theme", intro)
        
        # Test default
        intro = self.social_tool._generate_introduction("Test Theme", "unknown", "unknown")
        self.assertEqual(intro, "Let's talk about Test Theme.")
    
    def test_generate_call_to_action(self):
        """Test generating calls to action with different tones and platforms."""
        # Test professional tone
        cta = self.social_tool._generate_call_to_action("professional", "linkedin")
        self.assertTrue("comments" in cta or "connect" in cta or "share" in cta)
        
        # Test casual tone
        cta = self.social_tool._generate_call_to_action("casual", "twitter")
        self.assertTrue("comment" in cta or "tag" in cta or "like" in cta)
        
        # Test inspirational tone
        cta = self.social_tool._generate_call_to_action("inspirational", "instagram")
        self.assertTrue("journey" in cta or "inspire" in cta or "tag" in cta)
        
        # Test informative tone
        cta = self.social_tool._generate_call_to_action("informative", "facebook")
        self.assertTrue("information" in cta or "learn" in cta or "share" in cta)
        
        # Test default
        cta = self.social_tool._generate_call_to_action("unknown", "unknown")
        self.assertEqual(cta, "Let me know what you think in the comments!")
    
    def test_generate_hashtags(self):
        """Test generating hashtags based on keywords and platform constraints."""
        # Test LinkedIn (limit: 5)
        keywords = ["keyword1", "keyword2", "keyword3", "keyword with spaces"]
        hashtags = self.social_tool._generate_hashtags(keywords, "linkedin")
        
        self.assertLessEqual(len(hashtags), 5)  # LinkedIn limit
        self.assertIn("#Keyword1", hashtags)
        self.assertIn("#Keyword2", hashtags)
        self.assertIn("#Keyword3", hashtags)
        self.assertIn("#KeywordWithSpaces", hashtags)
        
        # Test Twitter (limit: 3)
        hashtags = self.social_tool._generate_hashtags(keywords, "twitter")
        self.assertLessEqual(len(hashtags), 3)  # Twitter limit
        
        # Test Instagram (limit: 10)
        hashtags = self.social_tool._generate_hashtags(keywords, "instagram")
        self.assertLessEqual(len(hashtags), 10)  # Instagram limit
        
        # Test Facebook (limit: 3)
        hashtags = self.social_tool._generate_hashtags(keywords, "facebook")
        self.assertLessEqual(len(hashtags), 3)  # Facebook limit
        
        # Test with special characters
        keywords = ["keyword!", "keyword@", "keyword#"]
        hashtags = self.social_tool._generate_hashtags(keywords, "linkedin")
        self.assertIn("#Keyword", hashtags[0])
        self.assertIn("#Keyword", hashtags[1])
        self.assertIn("#Keyword", hashtags[2])


if __name__ == "__main__":
    unittest.main()
