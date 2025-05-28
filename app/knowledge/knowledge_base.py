"""
Knowledge Base module for OpenManus agents.

This module provides knowledge base capabilities for agents,
including document retrieval and prompt enrichment.
"""

from typing import Dict, List, Any, Optional
import json
from loguru import logger

class BaseKnowledgeBase:
    """Base class for knowledge base implementations."""
    
    def __init__(self, config: Dict[str, Any] = {}):
        """
        Initialize knowledge base with configuration.
        
        Args:
            config: Configuration dictionary for knowledge base
        """
        self.config = config
        self.enabled = config.get("enabled", False)
    
    def enrich_prompt(self, prompt: str) -> str:
        """
        Enrich a prompt with relevant knowledge.
        
        Args:
            prompt: Original prompt
            
        Returns:
            Enriched prompt
        """
        if not self.enabled:
            return prompt
        
        # Implement in subclasses
        return prompt
    
    def add_document(self, document: Dict[str, Any]) -> bool:
        """
        Add a document to the knowledge base.
        
        Args:
            document: Document to add
            
        Returns:
            Success status
        """
        # Implement in subclasses
        return False
    
    def remove_document(self, document_id: str) -> bool:
        """
        Remove a document from the knowledge base.
        
        Args:
            document_id: ID of document to remove
            
        Returns:
            Success status
        """
        # Implement in subclasses
        return False
    
    def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant documents.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of relevant documents
        """
        # Implement in subclasses
        return []


class SimpleKnowledgeBase(BaseKnowledgeBase):
    """Simple knowledge base implementation with keyword matching."""
    
    def __init__(self, config: Dict[str, Any] = {}):
        """
        Initialize simple knowledge base.
        
        Args:
            config: Configuration dictionary for knowledge base
        """
        super().__init__(config)
        self.documents = []
        self.max_documents = config.get("max_documents", 100)
        self.max_context_length = config.get("max_context_length", 2000)
    
    def add_document(self, document: Dict[str, Any]) -> bool:
        """
        Add a document to the knowledge base.
        
        Args:
            document: Document to add
            
        Returns:
            Success status
        """
        if len(self.documents) >= self.max_documents:
            return False
        
        self.documents.append(document)
        return True
    
    def remove_document(self, document_id: str) -> bool:
        """
        Remove a document from the knowledge base.
        
        Args:
            document_id: ID of document to remove
            
        Returns:
            Success status
        """
        initial_count = len(self.documents)
        self.documents = [d for d in self.documents if d.get("id") != document_id]
        return len(self.documents) < initial_count
    
    def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant documents using simple keyword matching.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of relevant documents
        """
        if not self.enabled or not self.documents:
            return []
        
        # Simple keyword matching
        query_terms = query.lower().split()
        results = []
        
        for document in self.documents:
            content = document.get("content", "").lower()
            title = document.get("title", "").lower()
            
            # Calculate a simple relevance score
            score = 0
            for term in query_terms:
                if term in title:
                    score += 3  # Title matches are more important
                if term in content:
                    score += 1
            
            if score > 0:
                results.append({
                    "document": document,
                    "score": score
                })
        
        # Sort by relevance score
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top results
        return [r["document"] for r in results[:limit]]
    
    def enrich_prompt(self, prompt: str) -> str:
        """
        Enrich a prompt with relevant knowledge.
        
        Args:
            prompt: Original prompt
            
        Returns:
            Enriched prompt
        """
        if not self.enabled:
            return prompt
        
        # Search for relevant documents
        relevant_docs = self.search_documents(prompt)
        
        if not relevant_docs:
            return prompt
        
        # Create context from relevant documents
        context_parts = []
        
        for doc in relevant_docs:
            title = doc.get("title", "Untitled Document")
            content = doc.get("content", "")
            source = doc.get("source_url", "")
            
            # Add document to context
            doc_context = f"Title: {title}\n"
            if source:
                doc_context += f"Source: {source}\n"
            doc_context += f"Content: {content}\n\n"
            
            context_parts.append(doc_context)
        
        # Combine context parts, respecting max length
        combined_context = ""
        for part in context_parts:
            if len(combined_context) + len(part) <= self.max_context_length:
                combined_context += part
            else:
                break
        
        # Create enriched prompt
        if combined_context:
            enriched_prompt = f"""Relevant information:
{combined_context}

Using the information above if relevant, please respond to the following:
{prompt}"""
            return enriched_prompt
        
        return prompt


class VectorKnowledgeBase(BaseKnowledgeBase):
    """Knowledge base implementation using vector embeddings for semantic search."""
    
    def __init__(self, config: Dict[str, Any] = {}):
        """
        Initialize vector knowledge base.
        
        Args:
            config: Configuration dictionary for knowledge base
        """
        super().__init__(config)
        self.documents = []
        self.embeddings = []
        self.embedding_provider = None  # Will be set by the agent factory
        self.max_documents = config.get("max_documents", 1000)
        self.max_context_length = config.get("max_context_length", 2000)
    
    def set_embedding_provider(self, embedding_provider: Any) -> None:
        """
        Set the embedding provider for vector search.
        
        Args:
            embedding_provider: Embedding provider instance
        """
        self.embedding_provider = embedding_provider
    
    def add_document(self, document: Dict[str, Any]) -> bool:
        """
        Add a document to the knowledge base and generate its embedding.
        
        Args:
            document: Document to add
            
        Returns:
            Success status
        """
        if len(self.documents) >= self.max_documents or not self.embedding_provider:
            return False
        
        try:
            content = document.get("content", "")
            title = document.get("title", "")
            
            # Generate embedding for document
            text_to_embed = f"{title} {content}"
            embedding = self.embedding_provider.get_embedding(text_to_embed)
            
            # Store document and its embedding
            self.documents.append(document)
            self.embeddings.append(embedding)
            
            return True
        except Exception as e:
            logger.error(f"Error adding document to vector knowledge base: {str(e)}")
            return False
    
    def remove_document(self, document_id: str) -> bool:
        """
        Remove a document from the knowledge base.
        
        Args:
            document_id: ID of document to remove
            
        Returns:
            Success status
        """
        for i, document in enumerate(self.documents):
            if document.get("id") == document_id:
                self.documents.pop(i)
                self.embeddings.pop(i)
                return True
        
        return False
    
    def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant documents using vector similarity.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of relevant documents
        """
        if not self.enabled or not self.documents or not self.embedding_provider:
            return []
        
        try:
            # Generate embedding for query
            query_embedding = self.embedding_provider.get_embedding(query)
            
            # Calculate similarity scores
            results = []
            for i, doc_embedding in enumerate(self.embeddings):
                # Calculate cosine similarity
                similarity = self.embedding_provider.calculate_similarity(query_embedding, doc_embedding)
                
                if similarity > 0.7:  # Threshold for relevance
                    results.append({
                        "document": self.documents[i],
                        "score": similarity
                    })
            
            # Sort by similarity score
            results.sort(key=lambda x: x["score"], reverse=True)
            
            # Return top results
            return [r["document"] for r in results[:limit]]
        except Exception as e:
            logger.error(f"Error searching vector knowledge base: {str(e)}")
            return []
    
    def enrich_prompt(self, prompt: str) -> str:
        """
        Enrich a prompt with relevant knowledge using vector search.
        
        Args:
            prompt: Original prompt
            
        Returns:
            Enriched prompt
        """
        if not self.enabled or not self.embedding_provider:
            return prompt
        
        # Search for relevant documents
        relevant_docs = self.search_documents(prompt)
        
        if not relevant_docs:
            return prompt
        
        # Create context from relevant documents
        context_parts = []
        
        for doc in relevant_docs:
            title = doc.get("title", "Untitled Document")
            content = doc.get("content", "")
            source = doc.get("source_url", "")
            
            # Add document to context
            doc_context = f"Title: {title}\n"
            if source:
                doc_context += f"Source: {source}\n"
            doc_context += f"Content: {content}\n\n"
            
            context_parts.append(doc_context)
        
        # Combine context parts, respecting max length
        combined_context = ""
        for part in context_parts:
            if len(combined_context) + len(part) <= self.max_context_length:
                combined_context += part
            else:
                break
        
        # Create enriched prompt
        if combined_context:
            enriched_prompt = f"""Relevant information:
{combined_context}

Using the information above if relevant, please respond to the following:
{prompt}"""
            return enriched_prompt
        
        return prompt


class NoKnowledgeBase(BaseKnowledgeBase):
    """Dummy knowledge base implementation that does nothing."""
    
    def __init__(self, config: Dict[str, Any] = {}):
        """
        Initialize dummy knowledge base.
        
        Args:
            config: Configuration dictionary for knowledge base
        """
        super().__init__(config)
        self.enabled = False
    
    def enrich_prompt(self, prompt: str) -> str:
        """
        Return the original prompt unchanged.
        
        Args:
            prompt: Original prompt
            
        Returns:
            Original prompt
        """
        return prompt
    
    def add_document(self, document: Dict[str, Any]) -> bool:
        """
        Dummy implementation that always fails.
        
        Args:
            document: Document to add
            
        Returns:
            Always False
        """
        return False
    
    def remove_document(self, document_id: str) -> bool:
        """
        Dummy implementation that always fails.
        
        Args:
            document_id: ID of document to remove
            
        Returns:
            Always False
        """
        return False
    
    def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Dummy implementation that always returns empty list.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Empty list
        """
        return []


def get_knowledge_base(config: Dict[str, Any] = {}) -> BaseKnowledgeBase:
    """
    Factory function to create a knowledge base based on configuration.
    
    Args:
        config: Knowledge base configuration dictionary
        
    Returns:
        Knowledge base instance
    """
    if not config.get("enabled", False):
        return NoKnowledgeBase(config)
    
    kb_type = config.get("type", "simple")
    
    if kb_type == "vector":
        return VectorKnowledgeBase(config)
    elif kb_type == "simple":
        return SimpleKnowledgeBase(config)
    else:
        return NoKnowledgeBase(config)
