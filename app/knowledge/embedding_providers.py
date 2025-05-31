"""
Embedding providers for knowledge base vector search.

This module provides interfaces and implementations for embedding providers
that can be used with the VectorKnowledgeBase.
"""

from typing import Dict, List, Any, Optional
import os
import numpy as np
from loguru import logger
import requests

class BaseEmbeddingProvider:
    """Base class for embedding providers."""
    
    def __init__(self, config: Dict[str, Any] = {}):
        """
        Initialize embedding provider with configuration.
        
        Args:
            config: Configuration dictionary for embedding provider
        """
        self.config = config
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding vector for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        # Implement in subclasses
        raise NotImplementedError("Subclasses must implement get_embedding")
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        # Convert to numpy arrays for efficient calculation
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """Embedding provider using OpenAI's embedding API."""
    
    def __init__(self, config: Dict[str, Any] = {}):
        """
        Initialize OpenAI embedding provider.
        
        Args:
            config: Configuration dictionary with OpenAI API key and model
        """
        super().__init__(config)
        self.api_key = config.get("api_key", os.environ.get("OPENAI_API_KEY"))
        self.model = config.get("model", "text-embedding-3-small")
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding vector from OpenAI API.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "input": text,
                "model": self.model
            }
            
            response = requests.post(
                "https://api.openai.com/v1/embeddings",
                headers=headers,
                json=payload
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract embedding from response
            embedding = result["data"][0]["embedding"]
            
            return embedding
        except Exception as e:
            logger.error(f"Error getting embedding from OpenAI: {str(e)}")
            # Return zero vector as fallback
            return [0.0] * 1536  # Default dimension for OpenAI embeddings


class GroqEmbeddingProvider(BaseEmbeddingProvider):
    """Embedding provider using Groq's embedding API."""
    
    def __init__(self, config: Dict[str, Any] = {}):
        """
        Initialize Groq embedding provider.
        
        Args:
            config: Configuration dictionary with Groq API key and model
        """
        super().__init__(config)
        self.api_key = config.get("api_key", os.environ.get("GROQ_API_KEY"))
        self.model = config.get("model", "llama3-embedding-v1")
        
        if not self.api_key:
            raise ValueError("Groq API key is required")
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding vector from Groq API.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "input": text,
                "model": self.model
            }
            
            response = requests.post(
                "https://api.groq.com/v1/embeddings",
                headers=headers,
                json=payload
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract embedding from response
            embedding = result["data"][0]["embedding"]
            
            return embedding
        except Exception as e:
            logger.error(f"Error getting embedding from Groq: {str(e)}")
            # Return zero vector as fallback
            return [0.0] * 4096  # Default dimension for Groq embeddings


class DummyEmbeddingProvider(BaseEmbeddingProvider):
    """Dummy embedding provider for testing."""
    
    def __init__(self, config: Dict[str, Any] = {}):
        """
        Initialize dummy embedding provider.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        self.dimension = config.get("dimension", 384)
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Generate a deterministic but dummy embedding based on text.
        
        Args:
            text: Text to embed
            
        Returns:
            Dummy embedding vector
        """
        # Generate a deterministic embedding based on text hash
        import hashlib
        
        # Get hash of text
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert hash to list of floats
        embedding = []
        for i in range(self.dimension):
            # Use different parts of hash for different dimensions
            hash_part = text_hash[(i % len(text_hash))]
            # Convert hex to float between -1 and 1
            value = (int(hash_part, 16) / 15.0) * 2 - 1
            embedding.append(value)
        
        # Normalize to unit length
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = [x / norm for x in embedding]
        
        return embedding


def get_embedding_provider(config: Dict[str, Any] = {}) -> BaseEmbeddingProvider:
    """
    Factory function to create an embedding provider based on configuration.
    
    Args:
        config: Embedding provider configuration dictionary
        
    Returns:
        Embedding provider instance
    """
    provider_type = config.get("provider", "dummy")
    
    if provider_type == "openai":
        return OpenAIEmbeddingProvider(config)
    elif provider_type == "groq":
        return GroqEmbeddingProvider(config)
    else:
        return DummyEmbeddingProvider(config)
