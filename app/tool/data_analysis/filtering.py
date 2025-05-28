"""
Filtering Tool for OpenManus.

This tool provides functionality for filtering and transforming data,
enabling focused analysis and data preparation.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union

from app.tool.base import BaseTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FilteringTool(BaseTool):
    """
    Tool for filtering and transforming data.
    
    This tool provides methods for filtering data based on various criteria,
    transforming data structures, and preparing data for analysis.
    """
    
    name = "filtering_tool"
    description = "Filter and transform data based on various criteria"
    
    def __init__(self):
        """Initialize the FilteringTool."""
        super().__init__()
        logger.info("FilteringTool initialized")
    
    async def _arun(
        self,
        data: List[Dict[str, Any]],
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = "asc",
        limit: Optional[int] = None,
        group_by: Optional[str] = None,
        aggregate: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Filter and transform the provided data.
        
        Args:
            data: Data to filter and transform
            filters: Dictionary of field-value pairs to filter by
            sort_by: Field to sort by
            sort_order: Sort order (asc or desc)
            limit: Maximum number of results to return
            group_by: Field to group by
            aggregate: Dictionary of field-aggregation pairs for grouped data
            
        Returns:
            Dictionary containing the filtered and transformed data
        """
        logger.info("Filtering and transforming data")
        
        # Validate inputs
        if not data:
            return {"error": "Data is required"}
        
        # Convert data to pandas DataFrame for easier processing
        try:
            df = pd.DataFrame(data)
        except Exception as e:
            logger.error(f"Error converting data to DataFrame: {e}")
            return {"error": f"Invalid data format: {str(e)}"}
        
        # Apply filters if specified
        if filters:
            df = self._apply_filters(df, filters)
        
        # Group by if specified
        if group_by and group_by in df.columns:
            df = self._apply_grouping(df, group_by, aggregate)
        
        # Sort if specified
        if sort_by and sort_by in df.columns:
            ascending = sort_order.lower() != "desc"
            df = df.sort_values(by=sort_by, ascending=ascending)
        
        # Apply limit if specified
        if limit and limit > 0:
            df = df.head(limit)
        
        # Convert back to list of dictionaries
        try:
            result_data = df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error converting DataFrame to records: {e}")
            return {"error": f"Error formatting results: {str(e)}"}
        
        # Prepare result
        result = {
            "success": True,
            "filtered_data": result_data,
            "count": len(result_data),
            "filters_applied": filters is not None,
            "grouping_applied": group_by is not None,
            "sorting_applied": sort_by is not None,
            "limit_applied": limit is not None
        }
        
        return result
    
    def _apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply filters to the DataFrame.
        
        Args:
            df: DataFrame to filter
            filters: Dictionary of field-value pairs to filter by
            
        Returns:
            Filtered DataFrame
        """
        filtered_df = df.copy()
        
        for field, value in filters.items():
            if field in filtered_df.columns:
                if isinstance(value, dict):
                    # Complex filter with operators
                    for operator, op_value in value.items():
                        if operator == "eq":
                            filtered_df = filtered_df[filtered_df[field] == op_value]
                        elif operator == "neq":
                            filtered_df = filtered_df[filtered_df[field] != op_value]
                        elif operator == "gt":
                            filtered_df = filtered_df[filtered_df[field] > op_value]
                        elif operator == "gte":
                            filtered_df = filtered_df[filtered_df[field] >= op_value]
                        elif operator == "lt":
                            filtered_df = filtered_df[filtered_df[field] < op_value]
                        elif operator == "lte":
                            filtered_df = filtered_df[filtered_df[field] <= op_value]
                        elif operator == "in":
                            if isinstance(op_value, list):
                                filtered_df = filtered_df[filtered_df[field].isin(op_value)]
                        elif operator == "nin":
                            if isinstance(op_value, list):
                                filtered_df = filtered_df[~filtered_df[field].isin(op_value)]
                        elif operator == "contains":
                            if isinstance(op_value, str):
                                filtered_df = filtered_df[filtered_df[field].astype(str).str.contains(op_value)]
                        elif operator == "starts_with":
                            if isinstance(op_value, str):
                                filtered_df = filtered_df[filtered_df[field].astype(str).str.startswith(op_value)]
                        elif operator == "ends_with":
                            if isinstance(op_value, str):
                                filtered_df = filtered_df[filtered_df[field].astype(str).str.endswith(op_value)]
                else:
                    # Simple equality filter
                    filtered_df = filtered_df[filtered_df[field] == value]
        
        return filtered_df
    
    def _apply_grouping(
        self,
        df: pd.DataFrame,
        group_by: str,
        aggregate: Optional[Dict[str, str]] = None
    ) -> pd.DataFrame:
        """
        Apply grouping and aggregation to the DataFrame.
        
        Args:
            df: DataFrame to group
            group_by: Field to group by
            aggregate: Dictionary of field-aggregation pairs
            
        Returns:
            Grouped and aggregated DataFrame
        """
        if not aggregate:
            # Default aggregation: count rows per group
            return df.groupby(group_by).size().reset_index(name="count")
        
        # Build aggregation dictionary
        agg_dict = {}
        for field, agg_func in aggregate.items():
            if field in df.columns:
                if agg_func.lower() in ["sum", "min", "max", "mean", "median", "count", "std"]:
                    agg_dict[field] = agg_func.lower()
                else:
                    # Default to sum for invalid aggregation functions
                    agg_dict[field] = "sum"
        
        if not agg_dict:
            # No valid aggregations, default to count
            return df.groupby(group_by).size().reset_index(name="count")
        
        # Apply grouping and aggregation
        grouped_df = df.groupby(group_by).agg(agg_dict)
        
        # Reset index to make group_by field a column again
        return grouped_df.reset_index()
    
    async def filter_transactions_by_category(
        self,
        data: List[Dict[str, Any]],
        category: str,
        category_field: Optional[str] = "category",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Filter transactions by category.
        
        This is a convenience method that wraps the main _arun method
        for the specific use case of filtering by category.
        
        Args:
            data: Transaction data to filter
            category: Category to filter by
            category_field: Field name for category values
            
        Returns:
            Dictionary containing the filtered transactions
        """
        filters = {category_field: category}
        return await self._arun(data=data, filters=filters, **kwargs)
    
    async def get_top_items(
        self,
        data: List[Dict[str, Any]],
        value_field: str,
        count: Optional[int] = 5,
        filters: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get the top items by value.
        
        This is a convenience method that wraps the main _arun method
        for the specific use case of getting top items.
        
        Args:
            data: Data to analyze
            value_field: Field to sort by
            count: Number of top items to return
            filters: Additional filters to apply
            
        Returns:
            Dictionary containing the top items
        """
        return await self._arun(
            data=data,
            filters=filters,
            sort_by=value_field,
            sort_order="desc",
            limit=count,
            **kwargs
        )
    
    async def summarize_by_field(
        self,
        data: List[Dict[str, Any]],
        group_field: str,
        value_field: Optional[str] = None,
        agg_function: Optional[str] = "sum",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Summarize data by grouping and aggregating.
        
        This is a convenience method that wraps the main _arun method
        for the specific use case of summarizing by field.
        
        Args:
            data: Data to summarize
            group_field: Field to group by
            value_field: Field to aggregate
            agg_function: Aggregation function to apply
            
        Returns:
            Dictionary containing the summarized data
        """
        aggregate = None
        if value_field:
            aggregate = {value_field: agg_function}
        
        return await self._arun(
            data=data,
            group_by=group_field,
            aggregate=aggregate,
            **kwargs
        )
