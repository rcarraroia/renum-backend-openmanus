"""
Integration tests for the ContentCreatorAgent.

This module contains tests for the ContentCreatorAgent and its interaction
with the content creation tools.
"""

import os
import json
import unittest
from unittest.mock import patch, MagicMock

from app.agent.contentcreator import ContentCreatorAgent
from app.tool.content_creation import ContentStore, Content


class TestContentCreatorAgent(unittest.TestCase):
    """Integration tests for the ContentCreatorAgent."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use a temporary file for content storage
        self.test_file = "test_content.json"
        
        # Create a ContentCreatorAgent with mocked LLM
        with patch('app.agent.base.BaseAgent.generate_response') as self.mock_generate:
            self.agent = ContentCreatorAgent()
            
            # Replace the content store with one using our test file
            self.agent.content_store = ContentStore(self.test_file)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove the test file if it exists
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    async def test_process_message_email_generation(self):
        """Test processing a message requesting email generation."""
        # Set up the mock to return a response mentioning a content ID
        self.mock_generate.return_value = "I've created an email draft for you with ID email-12345678. Let me know if you need any changes!"
        
        # Create a sample content in the store
        self.agent.content_store.create_content(
            content_type="email",
            title="Meeting Agenda",
            body="This is the agenda for our meeting",
            metadata={"recipient": "team@example.com"},
            content_id="email-12345678"
        )
        
        # Process a message
        result = await self.agent.process_message("Can you draft an email about a meeting agenda for my team?")
        
        # Check the result
        self.assertEqual(result["response"], "I've created an email draft for you with ID email-12345678. Let me know if you need any changes!")
        self.assertEqual(len(result["contents"]), 1)
        self.assertEqual(result["contents"][0]["id"], "email-12345678")
        self.assertEqual(result["contents"][0]["title"], "Meeting Agenda")
        
        # Check that generate_response was called with the right message
        self.mock_generate.assert_called_once_with("Can you draft an email about a meeting agenda for my team?")
    
    async def test_process_message_social_post_generation(self):
        """Test processing a message requesting social media post generation."""
        # Set up the mock to return a response mentioning a content ID
        self.mock_generate.return_value = "I've created a LinkedIn post for you with ID social_post-87654321. It's ready to share!"
        
        # Create a sample content in the store
        self.agent.content_store.create_content(
            content_type="social_post",
            title="LinkedIn Post: Product Launch",
            body="Excited to announce our new product launch!",
            metadata={"platform": "linkedin"},
            content_id="social_post-87654321"
        )
        
        # Process a message
        result = await self.agent.process_message("Can you create a LinkedIn post about our product launch?")
        
        # Check the result
        self.assertEqual(result["response"], "I've created a LinkedIn post for you with ID social_post-87654321. It's ready to share!")
        self.assertEqual(len(result["contents"]), 1)
        self.assertEqual(result["contents"][0]["id"], "social_post-87654321")
        self.assertEqual(result["contents"][0]["title"], "LinkedIn Post: Product Launch")
        
        # Check that generate_response was called with the right message
        self.mock_generate.assert_called_once_with("Can you create a LinkedIn post about our product launch?")
    
    async def test_process_message_no_content_ids(self):
        """Test processing a message that doesn't result in content generation."""
        # Set up the mock to return a response with no content IDs
        self.mock_generate.return_value = "I can help you with content creation. What type of content would you like me to generate?"
        
        # Process a message
        result = await self.agent.process_message("Can you help me with content creation?")
        
        # Check the result
        self.assertEqual(result["response"], "I can help you with content creation. What type of content would you like me to generate?")
        self.assertEqual(len(result["contents"]), 0)
        
        # Check that generate_response was called with the right message
        self.mock_generate.assert_called_once_with("Can you help me with content creation?")
    
    async def test_process_message_multiple_content_ids(self):
        """Test processing a message that results in multiple content generations."""
        # Set up the mock to return a response mentioning multiple content IDs
        self.mock_generate.return_value = "I've created two pieces of content for you: an email (email-12345678) and a LinkedIn post (social_post-87654321)."
        
        # Create sample contents in the store
        self.agent.content_store.create_content(
            content_type="email",
            title="Meeting Agenda",
            body="This is the agenda for our meeting",
            metadata={"recipient": "team@example.com"},
            content_id="email-12345678"
        )
        
        self.agent.content_store.create_content(
            content_type="social_post",
            title="LinkedIn Post: Product Launch",
            body="Excited to announce our new product launch!",
            metadata={"platform": "linkedin"},
            content_id="social_post-87654321"
        )
        
        # Process a message
        result = await self.agent.process_message("Can you create an email and a LinkedIn post about our product launch?")
        
        # Check the result
        self.assertEqual(result["response"], "I've created two pieces of content for you: an email (email-12345678) and a LinkedIn post (social_post-87654321).")
        self.assertEqual(len(result["contents"]), 2)
        
        # Check that the contents are in the result
        content_ids = [content["id"] for content in result["contents"]]
        self.assertIn("email-12345678", content_ids)
        self.assertIn("social_post-87654321", content_ids)
        
        # Check that generate_response was called with the right message
        self.mock_generate.assert_called_once_with("Can you create an email and a LinkedIn post about our product launch?")
    
    async def test_get_all_contents(self):
        """Test getting all contents from the store."""
        # Create sample contents in the store
        self.agent.content_store.create_content(
            content_type="email",
            title="Meeting Agenda",
            body="This is the agenda for our meeting",
            metadata={"recipient": "team@example.com"}
        )
        
        self.agent.content_store.create_content(
            content_type="email",
            title="Project Update",
            body="This is an update on our project",
            metadata={"recipient": "manager@example.com"}
        )
        
        self.agent.content_store.create_content(
            content_type="social_post",
            title="LinkedIn Post: Product Launch",
            body="Excited to announce our new product launch!",
            metadata={"platform": "linkedin"}
        )
        
        # Get all contents
        all_contents = await self.agent.get_all_contents()
        self.assertEqual(len(all_contents), 3)
        
        # Get email contents
        email_contents = await self.agent.get_all_contents(content_type="email")
        self.assertEqual(len(email_contents), 2)
        
        # Get social post contents
        social_contents = await self.agent.get_all_contents(content_type="social_post")
        self.assertEqual(len(social_contents), 1)
        
        # Get contents by search term
        meeting_contents = await self.agent.get_all_contents(search_term="meeting")
        self.assertEqual(len(meeting_contents), 1)
        self.assertEqual(meeting_contents[0]["title"], "Meeting Agenda")


if __name__ == "__main__":
    unittest.main()
