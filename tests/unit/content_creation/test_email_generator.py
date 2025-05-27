"""
Unit tests for the EmailGeneratorTool.

This module contains tests for the EmailGeneratorTool class and its methods.
"""

import unittest
from unittest.mock import patch, MagicMock

from app.tool.content_creation.email_generator import EmailGeneratorTool
from app.tool.content_creation.content_store import ContentStore, Content


class TestEmailGeneratorTool(unittest.TestCase):
    """Tests for the EmailGeneratorTool class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock ContentStore
        self.mock_content_store = MagicMock(spec=ContentStore)
        
        # Create an EmailGeneratorTool with the mock store
        self.email_tool = EmailGeneratorTool(self.mock_content_store)
    
    async def test_execute_valid_inputs(self):
        """Test executing the tool with valid inputs."""
        # Set up the mock to return a specific content
        mock_content = MagicMock(spec=Content)
        mock_content.id = "email-12345678"
        mock_content.title = "Test Subject"
        mock_content.body = "Test email body"
        mock_content.created_at = "2023-01-01T00:00:00"
        self.mock_content_store.create_content.return_value = mock_content
        
        # Execute the tool
        result = await self.email_tool.execute(
            recipient="test@example.com",
            topic="Test Topic",
            key_points=["Point 1", "Point 2"],
            tone="professional",
            include_greeting=True,
            include_signature=True
        )
        
        # Check the result
        self.assertTrue(result["success"])
        self.assertEqual(result["email"]["id"], "email-12345678")
        self.assertEqual(result["email"]["recipient"], "test@example.com")
        
        # Check that create_content was called with the right arguments
        self.mock_content_store.create_content.assert_called_once()
        call_args = self.mock_content_store.create_content.call_args[1]
        self.assertEqual(call_args["content_type"], "email")
        self.assertIsNotNone(call_args["title"])
        self.assertIsNotNone(call_args["body"])
        self.assertEqual(call_args["metadata"]["recipient"], "test@example.com")
        self.assertEqual(call_args["metadata"]["tone"], "professional")
        self.assertEqual(call_args["metadata"]["key_points"], ["Point 1", "Point 2"])
    
    async def test_execute_missing_recipient(self):
        """Test executing the tool with a missing recipient."""
        result = await self.email_tool.execute(
            recipient="",
            topic="Test Topic",
            key_points=["Point 1", "Point 2"]
        )
        
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Recipient cannot be empty.")
        self.mock_content_store.create_content.assert_not_called()
    
    async def test_execute_missing_topic(self):
        """Test executing the tool with a missing topic."""
        result = await self.email_tool.execute(
            recipient="test@example.com",
            topic="",
            key_points=["Point 1", "Point 2"]
        )
        
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Topic cannot be empty.")
        self.mock_content_store.create_content.assert_not_called()
    
    async def test_execute_missing_key_points(self):
        """Test executing the tool with missing key points."""
        result = await self.email_tool.execute(
            recipient="test@example.com",
            topic="Test Topic",
            key_points=[]
        )
        
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "At least one key point must be provided.")
        self.mock_content_store.create_content.assert_not_called()
    
    async def test_execute_invalid_tone(self):
        """Test executing the tool with an invalid tone."""
        # Set up the mock to return a specific content
        mock_content = MagicMock(spec=Content)
        mock_content.id = "email-12345678"
        self.mock_content_store.create_content.return_value = mock_content
        
        # Execute the tool with an invalid tone
        result = await self.email_tool.execute(
            recipient="test@example.com",
            topic="Test Topic",
            key_points=["Point 1", "Point 2"],
            tone="invalid_tone"
        )
        
        # Check that the tool defaulted to "professional" tone
        self.assertTrue(result["success"])
        self.mock_content_store.create_content.assert_called_once()
        call_args = self.mock_content_store.create_content.call_args[1]
        self.assertEqual(call_args["metadata"]["tone"], "professional")
    
    def test_generate_email_subject(self):
        """Test generating email subjects with different tones."""
        # Test urgent tone
        subject = self.email_tool._generate_email_subject("Test Topic", "urgent")
        self.assertEqual(subject, "URGENT: Test Topic")
        
        # Test formal tone
        subject = self.email_tool._generate_email_subject("Test Topic", "formal")
        self.assertEqual(subject, "Test Topic")
        
        # Test professional tone
        subject = self.email_tool._generate_email_subject("Test Topic", "professional")
        self.assertEqual(subject, "Test Topic")
        
        # Test friendly tone
        subject = self.email_tool._generate_email_subject("Test Topic", "friendly")
        self.assertEqual(subject, "Test Topic - let's discuss")
        
        # Test casual tone
        subject = self.email_tool._generate_email_subject("Test Topic", "casual")
        self.assertEqual(subject, "Test Topic - let's discuss")
        
        # Test with punctuation
        subject = self.email_tool._generate_email_subject("Test Topic!", "friendly")
        self.assertEqual(subject, "Test Topic - let's discuss")
    
    def test_generate_greeting(self):
        """Test generating greetings with different tones."""
        # Test formal tone
        greeting = self.email_tool._generate_greeting("John", "formal")
        self.assertEqual(greeting, "Dear John,")
        
        # Test professional tone
        greeting = self.email_tool._generate_greeting("John", "professional")
        self.assertEqual(greeting, "Hello John,")
        
        # Test urgent tone
        greeting = self.email_tool._generate_greeting("John", "urgent")
        self.assertEqual(greeting, "Attention John,")
        
        # Test friendly tone
        greeting = self.email_tool._generate_greeting("John", "friendly")
        self.assertEqual(greeting, "Hi John,")
        
        # Test casual tone
        greeting = self.email_tool._generate_greeting("John", "casual")
        self.assertEqual(greeting, "Hi John,")
        
        # Test default
        greeting = self.email_tool._generate_greeting("John", "unknown")
        self.assertEqual(greeting, "Hello John,")
    
    def test_format_key_points(self):
        """Test formatting key points with different tones."""
        key_points = ["Point 1", "Point 2", "Point 3"]
        
        # Test urgent tone
        formatted = self.email_tool._format_key_points(key_points, "urgent")
        self.assertIn("• IMPORTANT: Point 1", formatted)
        self.assertIn("• IMPORTANT: Point 2", formatted)
        self.assertIn("• IMPORTANT: Point 3", formatted)
        
        # Test formal tone
        formatted = self.email_tool._format_key_points(key_points, "formal")
        self.assertIn("Here are the key points:", formatted)
        self.assertIn("1. Point 1", formatted)
        self.assertIn("2. Point 2", formatted)
        self.assertIn("3. Point 3", formatted)
        
        # Test professional tone
        formatted = self.email_tool._format_key_points(key_points, "professional")
        self.assertIn("Here are the key points:", formatted)
        self.assertIn("1. Point 1", formatted)
        self.assertIn("2. Point 2", formatted)
        self.assertIn("3. Point 3", formatted)
        
        # Test friendly tone
        formatted = self.email_tool._format_key_points(key_points, "friendly")
        self.assertIn("I wanted to highlight a few things:", formatted)
        self.assertIn("• Point 1", formatted)
        self.assertIn("• Point 2", formatted)
        self.assertIn("• Point 3", formatted)
        
        # Test casual tone
        formatted = self.email_tool._format_key_points(key_points, "casual")
        self.assertIn("I wanted to highlight a few things:", formatted)
        self.assertIn("• Point 1", formatted)
        self.assertIn("• Point 2", formatted)
        self.assertIn("• Point 3", formatted)
        
        # Test default
        formatted = self.email_tool._format_key_points(key_points, "unknown")
        self.assertIn("- Point 1", formatted)
        self.assertIn("- Point 2", formatted)
        self.assertIn("- Point 3", formatted)


if __name__ == "__main__":
    unittest.main()
