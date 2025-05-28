"""
Data Loader Tool for OpenManus.

This tool provides functionality for loading and caching data from various sources,
including CSV files, JSON files, and databases.
"""

import csv
import json
import logging
import os
import pandas as pd
from typing import Dict, Any, List, Optional, Union

from app.tool.base import BaseTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoaderTool(BaseTool):
    """
    Tool for loading and caching data from various sources.
    
    This tool provides methods for loading data from files and databases,
    with support for caching to improve performance for repeated access.
    """
    
    name = "data_loader"
    description = "Load data from various sources including CSV, JSON, and databases"
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the DataLoaderTool.
        
        Args:
            cache_dir: Directory for caching loaded data
        """
        super().__init__()
        
        # Set default cache directory if not provided
        if cache_dir is None:
            cache_dir = os.path.join(os.getcwd(), "data_cache")
        
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Initialize cache
        self.data_cache = {}
        
        logger.info(f"DataLoaderTool initialized with cache at: {cache_dir}")
    
    async def _arun(
        self,
        source: str,
        source_type: Optional[str] = None,
        cache: Optional[bool] = True,
        query_params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Load data from the specified source.
        
        Args:
            source: Path to the data source (file path or connection string)
            source_type: Type of the source (csv, json, database)
            cache: Whether to cache the loaded data
            query_params: Additional parameters for database queries
            
        Returns:
            Dictionary containing the loaded data and metadata
        """
        logger.info(f"Loading data from source: {source}")
        
        # Validate inputs
        if not source:
            return {"error": "Source is required"}
        
        # Check cache if enabled
        if cache and source in self.data_cache:
            logger.info(f"Returning cached data for source: {source}")
            return self.data_cache[source]
        
        # Determine source type if not provided
        if source_type is None:
            source_type = self._infer_source_type(source)
        
        # Load data based on source type
        try:
            if source_type == "csv":
                result = await self._load_csv(source)
            elif source_type == "json":
                result = await self._load_json(source)
            elif source_type == "database":
                result = await self._load_database(source, query_params)
            else:
                return {"error": f"Unsupported source type: {source_type}"}
            
            # Cache the result if enabled
            if cache:
                self.data_cache[source] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Error loading data from {source}: {e}")
            return {"error": f"Failed to load data: {str(e)}"}
    
    def _infer_source_type(self, source: str) -> str:
        """
        Infer the source type from the source path.
        
        Args:
            source: Path to the data source
            
        Returns:
            Inferred source type
        """
        if source.endswith(".csv"):
            return "csv"
        elif source.endswith(".json"):
            return "json"
        elif "://" in source:
            return "database"
        else:
            # Default to CSV for unknown types
            return "csv"
    
    async def _load_csv(self, source: str) -> Dict[str, Any]:
        """
        Load data from a CSV file.
        
        Args:
            source: Path to the CSV file
            
        Returns:
            Dictionary containing the loaded data and metadata
        """
        try:
            # Read CSV file into pandas DataFrame
            df = pd.read_csv(source)
            
            # Convert to list of dictionaries for easier processing
            data = df.to_dict(orient="records")
            
            # Extract metadata
            metadata = {
                "source": source,
                "source_type": "csv",
                "row_count": len(data),
                "column_count": len(df.columns),
                "columns": list(df.columns)
            }
            
            return {
                "success": True,
                "data": data,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error loading CSV from {source}: {e}")
            raise
    
    async def _load_json(self, source: str) -> Dict[str, Any]:
        """
        Load data from a JSON file.
        
        Args:
            source: Path to the JSON file
            
        Returns:
            Dictionary containing the loaded data and metadata
        """
        try:
            # Read JSON file
            with open(source, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Extract metadata
            metadata = {
                "source": source,
                "source_type": "json"
            }
            
            # Add additional metadata based on data structure
            if isinstance(data, list):
                metadata["item_count"] = len(data)
                if len(data) > 0 and isinstance(data[0], dict):
                    metadata["fields"] = list(data[0].keys())
            elif isinstance(data, dict):
                metadata["keys"] = list(data.keys())
            
            return {
                "success": True,
                "data": data,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error loading JSON from {source}: {e}")
            raise
    
    async def _load_database(
        self,
        source: str,
        query_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load data from a database.
        
        Args:
            source: Database connection string
            query_params: Query parameters
            
        Returns:
            Dictionary containing the loaded data and metadata
        """
        # For the PoC, we'll simulate database access
        # In a real implementation, this would connect to an actual database
        
        logger.info(f"Simulating database access for: {source}")
        
        # Create simulated data based on query parameters
        simulated_data = []
        
        if query_params and "table" in query_params:
            table_name = query_params["table"]
            
            if table_name == "sales":
                # Simulate sales data
                simulated_data = [
                    {"id": 1, "product": "Product A", "amount": 100, "date": "2023-01-01"},
                    {"id": 2, "product": "Product B", "amount": 200, "date": "2023-01-02"},
                    {"id": 3, "product": "Product A", "amount": 150, "date": "2023-01-03"},
                    {"id": 4, "product": "Product C", "amount": 300, "date": "2023-01-04"},
                    {"id": 5, "product": "Product B", "amount": 250, "date": "2023-01-05"}
                ]
            elif table_name == "customers":
                # Simulate customer data
                simulated_data = [
                    {"id": 1, "name": "Customer 1", "segment": "Enterprise"},
                    {"id": 2, "name": "Customer 2", "segment": "SMB"},
                    {"id": 3, "name": "Customer 3", "segment": "Enterprise"},
                    {"id": 4, "name": "Customer 4", "segment": "Consumer"},
                    {"id": 5, "name": "Customer 5", "segment": "SMB"}
                ]
            else:
                # Default simulated data
                simulated_data = [
                    {"id": 1, "value": "Value 1"},
                    {"id": 2, "value": "Value 2"},
                    {"id": 3, "value": "Value 3"}
                ]
        
        # Extract metadata
        metadata = {
            "source": source,
            "source_type": "database",
            "simulated": True,
            "row_count": len(simulated_data)
        }
        
        if len(simulated_data) > 0:
            metadata["columns"] = list(simulated_data[0].keys())
        
        return {
            "success": True,
            "data": simulated_data,
            "metadata": metadata
        }
    
    def clear_cache(self, source: Optional[str] = None) -> Dict[str, Any]:
        """
        Clear the data cache.
        
        Args:
            source: Specific source to clear from cache (None for all)
            
        Returns:
            Dictionary containing the result of the operation
        """
        if source is None:
            # Clear entire cache
            self.data_cache = {}
            logger.info("Cleared entire data cache")
            return {
                "success": True,
                "message": "Entire data cache cleared"
            }
        elif source in self.data_cache:
            # Clear specific source
            del self.data_cache[source]
            logger.info(f"Cleared cache for source: {source}")
            return {
                "success": True,
                "message": f"Cache cleared for source: {source}"
            }
        else:
            # Source not in cache
            logger.info(f"Source not found in cache: {source}")
            return {
                "success": False,
                "message": f"Source not found in cache: {source}"
            }
    
    def get_cached_sources(self) -> Dict[str, Any]:
        """
        Get a list of sources currently in the cache.
        
        Returns:
            Dictionary containing the list of cached sources
        """
        return {
            "success": True,
            "cached_sources": list(self.data_cache.keys()),
            "count": len(self.data_cache)
        }
