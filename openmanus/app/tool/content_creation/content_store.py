"""
Content store module for the Content Creation agent.

This module provides a simple persistence mechanism for storing and retrieving
generated content such as email drafts and social media posts.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Union


class Content:
    """
    Represents a piece of generated content.
    
    Attributes:
        id: Unique identifier for the content
        content_type: Type of content (email, social_post, etc.)
        title: Title or subject of the content
        body: Main body of the content
        metadata: Additional metadata about the content
        created_at: Timestamp when the content was created
        updated_at: Timestamp when the content was last updated
    """
    
    def __init__(
        self,
        content_type: str,
        title: str,
        body: str,
        metadata: Optional[Dict[str, Any]] = None,
        content_id: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None
    ):
        """
        Initialize a Content object.
        
        Args:
            content_type: Type of content (email, social_post, etc.)
            title: Title or subject of the content
            body: Main body of the content
            metadata: Additional metadata about the content
            content_id: Unique identifier for the content (generated if not provided)
            created_at: Timestamp when the content was created (current time if not provided)
            updated_at: Timestamp when the content was last updated (same as created_at if not provided)
        """
        self.content_type = content_type
        self.title = title
        self.body = body
        self.metadata = metadata or {}
        
        # Generate a unique ID if not provided
        self.id = content_id or self._generate_id()
        
        # Set timestamps
        current_time = datetime.now().isoformat()
        self.created_at = created_at or current_time
        self.updated_at = updated_at or self.created_at
    
    def _generate_id(self) -> str:
        """
        Generate a unique ID for the content.
        
        Returns:
            A unique ID string
        """
        import uuid
        return f"{self.content_type}-{uuid.uuid4().hex[:8]}"
    
    def update(self, title: Optional[str] = None, body: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Update the content with new values.
        
        Args:
            title: New title (if provided)
            body: New body (if provided)
            metadata: New metadata (if provided)
        """
        if title is not None:
            self.title = title
        
        if body is not None:
            self.body = body
        
        if metadata is not None:
            self.metadata.update(metadata)
        
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the content to a dictionary.
        
        Returns:
            Dictionary representation of the content
        """
        return {
            "id": self.id,
            "content_type": self.content_type,
            "title": self.title,
            "body": self.body,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Content':
        """
        Create a Content object from a dictionary.
        
        Args:
            data: Dictionary containing content data
            
        Returns:
            A Content object
        """
        return cls(
            content_type=data["content_type"],
            title=data["title"],
            body=data["body"],
            metadata=data.get("metadata", {}),
            content_id=data["id"],
            created_at=data["created_at"],
            updated_at=data["updated_at"]
        )


class ContentStore:
    """
    Store for managing generated content.
    
    This class provides methods for creating, retrieving, updating, and deleting
    content, with persistence to a JSON file.
    """
    
    def __init__(self, storage_path: str = "content.json"):
        """
        Initialize the ContentStore.
        
        Args:
            storage_path: Path to the JSON file for content storage
        """
        self.storage_path = storage_path
        self.contents: Dict[str, Content] = {}
        self._load_contents()
    
    def _load_contents(self) -> None:
        """
        Load contents from the storage file.
        
        If the file doesn't exist or is corrupted, starts with an empty store.
        """
        if not os.path.exists(self.storage_path):
            return
        
        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)
                
                for content_data in data.values():
                    content = Content.from_dict(content_data)
                    self.contents[content.id] = content
                    
        except (json.JSONDecodeError, KeyError) as e:
            # If the file is corrupted, create a backup and start fresh
            if os.path.exists(self.storage_path):
                backup_path = f"{self.storage_path}.bak"
                os.rename(self.storage_path, backup_path)
                print(f"Warning: Content store file corrupted. Backup created at {backup_path}")
    
    def _save_contents(self) -> None:
        """
        Save contents to the storage file.
        """
        data = {content.id: content.to_dict() for content in self.contents.values()}
        
        with open(self.storage_path, "w") as f:
            json.dump(data, f, indent=2)
    
    def create_content(
        self,
        content_type: str,
        title: str,
        body: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Content:
        """
        Create a new content item.
        
        Args:
            content_type: Type of content (email, social_post, etc.)
            title: Title or subject of the content
            body: Main body of the content
            metadata: Additional metadata about the content
            
        Returns:
            The created Content object
        """
        content = Content(
            content_type=content_type,
            title=title,
            body=body,
            metadata=metadata
        )
        
        self.contents[content.id] = content
        self._save_contents()
        
        return content
    
    def get_content(self, content_id: Optional[str] = None, title: Optional[str] = None) -> Optional[Content]:
        """
        Get a specific content item by ID or title.
        
        Args:
            content_id: ID of the content to retrieve
            title: Title of the content to retrieve (exact match)
            
        Returns:
            The Content object if found, None otherwise
        """
        if content_id and content_id in self.contents:
            return self.contents[content_id]
        
        if title:
            for content in self.contents.values():
                if content.title == title:
                    return content
        
        return None
    
    def get_contents(
        self,
        content_type: Optional[str] = None,
        search_term: Optional[str] = None
    ) -> List[Content]:
        """
        Get content items filtered by type and/or search term.
        
        Args:
            content_type: Filter by content type
            search_term: Filter by search term in title or body
            
        Returns:
            List of matching Content objects
        """
        results = []
        
        for content in self.contents.values():
            # Filter by content type if specified
            if content_type and content.content_type != content_type:
                continue
            
            # Filter by search term if specified
            if search_term:
                search_term_lower = search_term.lower()
                if (search_term_lower not in content.title.lower() and
                    search_term_lower not in content.body.lower()):
                    continue
            
            results.append(content)
        
        # Sort by creation date (newest first)
        results.sort(key=lambda x: x.created_at, reverse=True)
        
        return results
    
    def update_content(
        self,
        content_id: str,
        title: Optional[str] = None,
        body: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Content]:
        """
        Update an existing content item.
        
        Args:
            content_id: ID of the content to update
            title: New title (if provided)
            body: New body (if provided)
            metadata: New metadata (if provided)
            
        Returns:
            The updated Content object if found, None otherwise
        """
        if content_id not in self.contents:
            return None
        
        content = self.contents[content_id]
        content.update(title, body, metadata)
        
        self._save_contents()
        
        return content
    
    def delete_content(self, content_id: str) -> bool:
        """
        Delete a content item.
        
        Args:
            content_id: ID of the content to delete
            
        Returns:
            True if the content was deleted, False otherwise
        """
        if content_id not in self.contents:
            return False
        
        del self.contents[content_id]
        self._save_contents()
        
        return True
