"""
Unit tests for the ContentStore module.

This module contains tests for the ContentStore class and its methods.
"""

import os
import json
import unittest
from unittest.mock import patch, mock_open

from app.tool.content_creation.content_store import ContentStore, Content


class TestContent(unittest.TestCase):
    """Tests for the Content class."""
    
    def test_content_initialization(self):
        """Test that Content objects are initialized correctly."""
        content = Content(
            content_type="email",
            title="Test Email",
            body="This is a test email body",
            metadata={"recipient": "test@example.com"}
        )
        
        self.assertEqual(content.content_type, "email")
        self.assertEqual(content.title, "Test Email")
        self.assertEqual(content.body, "This is a test email body")
        self.assertEqual(content.metadata, {"recipient": "test@example.com"})
        self.assertTrue(content.id.startswith("email-"))
        self.assertIsNotNone(content.created_at)
        self.assertEqual(content.created_at, content.updated_at)
    
    def test_content_update(self):
        """Test that Content objects can be updated correctly."""
        content = Content(
            content_type="email",
            title="Test Email",
            body="This is a test email body",
            metadata={"recipient": "test@example.com"}
        )
        
        original_created_at = content.created_at
        original_updated_at = content.updated_at
        
        # Update the content
        content.update(
            title="Updated Email",
            body="This is an updated email body",
            metadata={"recipient": "updated@example.com"}
        )
        
        self.assertEqual(content.title, "Updated Email")
        self.assertEqual(content.body, "This is an updated email body")
        self.assertEqual(content.metadata, {"recipient": "updated@example.com"})
        self.assertEqual(content.created_at, original_created_at)
        self.assertNotEqual(content.updated_at, original_updated_at)
    
    def test_content_to_dict(self):
        """Test that Content objects can be converted to dictionaries."""
        content = Content(
            content_type="email",
            title="Test Email",
            body="This is a test email body",
            metadata={"recipient": "test@example.com"},
            content_id="email-12345678",
            created_at="2023-01-01T00:00:00",
            updated_at="2023-01-01T00:00:00"
        )
        
        content_dict = content.to_dict()
        
        self.assertEqual(content_dict["id"], "email-12345678")
        self.assertEqual(content_dict["content_type"], "email")
        self.assertEqual(content_dict["title"], "Test Email")
        self.assertEqual(content_dict["body"], "This is a test email body")
        self.assertEqual(content_dict["metadata"], {"recipient": "test@example.com"})
        self.assertEqual(content_dict["created_at"], "2023-01-01T00:00:00")
        self.assertEqual(content_dict["updated_at"], "2023-01-01T00:00:00")
    
    def test_content_from_dict(self):
        """Test that Content objects can be created from dictionaries."""
        content_dict = {
            "id": "email-12345678",
            "content_type": "email",
            "title": "Test Email",
            "body": "This is a test email body",
            "metadata": {"recipient": "test@example.com"},
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        
        content = Content.from_dict(content_dict)
        
        self.assertEqual(content.id, "email-12345678")
        self.assertEqual(content.content_type, "email")
        self.assertEqual(content.title, "Test Email")
        self.assertEqual(content.body, "This is a test email body")
        self.assertEqual(content.metadata, {"recipient": "test@example.com"})
        self.assertEqual(content.created_at, "2023-01-01T00:00:00")
        self.assertEqual(content.updated_at, "2023-01-01T00:00:00")


class TestContentStore(unittest.TestCase):
    """Tests for the ContentStore class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use a temporary file for testing
        self.test_file = "test_content.json"
        
        # Create a ContentStore with the test file
        self.content_store = ContentStore(self.test_file)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove the test file if it exists
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    @patch("builtins.open", new_callable=mock_open, read_data='{}')
    @patch("os.path.exists", return_value=True)
    def test_load_contents_empty_file(self, mock_exists, mock_file):
        """Test loading contents from an empty file."""
        content_store = ContentStore(self.test_file)
        self.assertEqual(len(content_store.contents), 0)
    
    @patch("builtins.open", new_callable=mock_open, read_data='{"email-12345678": {"id": "email-12345678", "content_type": "email", "title": "Test Email", "body": "This is a test email body", "metadata": {"recipient": "test@example.com"}, "created_at": "2023-01-01T00:00:00", "updated_at": "2023-01-01T00:00:00"}}')
    @patch("os.path.exists", return_value=True)
    def test_load_contents_with_data(self, mock_exists, mock_file):
        """Test loading contents from a file with data."""
        content_store = ContentStore(self.test_file)
        self.assertEqual(len(content_store.contents), 1)
        self.assertIn("email-12345678", content_store.contents)
    
    @patch("builtins.open", new_callable=mock_open, read_data='invalid json')
    @patch("os.path.exists", return_value=True)
    @patch("os.rename")
    def test_load_contents_corrupted_file(self, mock_rename, mock_exists, mock_file):
        """Test loading contents from a corrupted file."""
        content_store = ContentStore(self.test_file)
        self.assertEqual(len(content_store.contents), 0)
        mock_rename.assert_called_once_with(self.test_file, f"{self.test_file}.bak")
    
    def test_create_content(self):
        """Test creating a new content item."""
        content = self.content_store.create_content(
            content_type="email",
            title="Test Email",
            body="This is a test email body",
            metadata={"recipient": "test@example.com"}
        )
        
        self.assertEqual(content.content_type, "email")
        self.assertEqual(content.title, "Test Email")
        self.assertEqual(content.body, "This is a test email body")
        self.assertEqual(content.metadata, {"recipient": "test@example.com"})
        self.assertIn(content.id, self.content_store.contents)
    
    def test_get_content_by_id(self):
        """Test getting a content item by ID."""
        content = self.content_store.create_content(
            content_type="email",
            title="Test Email",
            body="This is a test email body",
            metadata={"recipient": "test@example.com"}
        )
        
        retrieved_content = self.content_store.get_content(content_id=content.id)
        
        self.assertEqual(retrieved_content.id, content.id)
        self.assertEqual(retrieved_content.title, content.title)
    
    def test_get_content_by_title(self):
        """Test getting a content item by title."""
        content = self.content_store.create_content(
            content_type="email",
            title="Test Email",
            body="This is a test email body",
            metadata={"recipient": "test@example.com"}
        )
        
        retrieved_content = self.content_store.get_content(title="Test Email")
        
        self.assertEqual(retrieved_content.id, content.id)
        self.assertEqual(retrieved_content.title, content.title)
    
    def test_get_content_not_found(self):
        """Test getting a content item that doesn't exist."""
        retrieved_content = self.content_store.get_content(content_id="nonexistent")
        self.assertIsNone(retrieved_content)
        
        retrieved_content = self.content_store.get_content(title="Nonexistent")
        self.assertIsNone(retrieved_content)
    
    def test_get_contents_all(self):
        """Test getting all content items."""
        self.content_store.create_content(
            content_type="email",
            title="Test Email 1",
            body="This is test email 1",
            metadata={"recipient": "test1@example.com"}
        )
        
        self.content_store.create_content(
            content_type="email",
            title="Test Email 2",
            body="This is test email 2",
            metadata={"recipient": "test2@example.com"}
        )
        
        self.content_store.create_content(
            content_type="social_post",
            title="Test Post",
            body="This is a test post",
            metadata={"platform": "twitter"}
        )
        
        contents = self.content_store.get_contents()
        
        self.assertEqual(len(contents), 3)
    
    def test_get_contents_by_type(self):
        """Test getting content items filtered by type."""
        self.content_store.create_content(
            content_type="email",
            title="Test Email 1",
            body="This is test email 1",
            metadata={"recipient": "test1@example.com"}
        )
        
        self.content_store.create_content(
            content_type="email",
            title="Test Email 2",
            body="This is test email 2",
            metadata={"recipient": "test2@example.com"}
        )
        
        self.content_store.create_content(
            content_type="social_post",
            title="Test Post",
            body="This is a test post",
            metadata={"platform": "twitter"}
        )
        
        email_contents = self.content_store.get_contents(content_type="email")
        social_contents = self.content_store.get_contents(content_type="social_post")
        
        self.assertEqual(len(email_contents), 2)
        self.assertEqual(len(social_contents), 1)
    
    def test_get_contents_by_search_term(self):
        """Test getting content items filtered by search term."""
        self.content_store.create_content(
            content_type="email",
            title="Meeting Agenda",
            body="This is the agenda for our meeting",
            metadata={"recipient": "team@example.com"}
        )
        
        self.content_store.create_content(
            content_type="email",
            title="Project Update",
            body="This is an update on our project",
            metadata={"recipient": "manager@example.com"}
        )
        
        meeting_contents = self.content_store.get_contents(search_term="meeting")
        project_contents = self.content_store.get_contents(search_term="project")
        
        self.assertEqual(len(meeting_contents), 1)
        self.assertEqual(len(project_contents), 1)
    
    def test_update_content(self):
        """Test updating a content item."""
        content = self.content_store.create_content(
            content_type="email",
            title="Test Email",
            body="This is a test email body",
            metadata={"recipient": "test@example.com"}
        )
        
        updated_content = self.content_store.update_content(
            content_id=content.id,
            title="Updated Email",
            body="This is an updated email body",
            metadata={"recipient": "updated@example.com"}
        )
        
        self.assertEqual(updated_content.title, "Updated Email")
        self.assertEqual(updated_content.body, "This is an updated email body")
        self.assertEqual(updated_content.metadata, {"recipient": "updated@example.com"})
        
        # Check that the content was updated in the store
        retrieved_content = self.content_store.get_content(content_id=content.id)
        self.assertEqual(retrieved_content.title, "Updated Email")
    
    def test_update_content_not_found(self):
        """Test updating a content item that doesn't exist."""
        updated_content = self.content_store.update_content(
            content_id="nonexistent",
            title="Updated Email"
        )
        
        self.assertIsNone(updated_content)
    
    def test_delete_content(self):
        """Test deleting a content item."""
        content = self.content_store.create_content(
            content_type="email",
            title="Test Email",
            body="This is a test email body",
            metadata={"recipient": "test@example.com"}
        )
        
        result = self.content_store.delete_content(content_id=content.id)
        
        self.assertTrue(result)
        self.assertNotIn(content.id, self.content_store.contents)
    
    def test_delete_content_not_found(self):
        """Test deleting a content item that doesn't exist."""
        result = self.content_store.delete_content(content_id="nonexistent")
        
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
