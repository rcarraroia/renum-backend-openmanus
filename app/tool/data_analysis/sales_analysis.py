"""
Sales Analysis Tool for OpenManus.

This tool provides functionality for analyzing sales data,
including total calculations, growth analysis, and trend identification.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta

from app.tool.base import BaseTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SalesAnalysisTool(BaseTool):
    """
    Tool for analyzing sales data and extracting insights.
    
    This tool provides methods for calculating sales totals, identifying
    growth trends, and performing other sales-related analyses.
    """
    
    name = "sales_analysis"
    description = "Analyze sales data to extract insights and trends"
    
    def __init__(self):
        """Initialize the SalesAnalysisTool."""
        super().__init__()
        logger.info("SalesAnalysisTool initialized")
    
    async def _arun(
        self,
        action: str,
        data: List[Dict[str, Any]],
        period: Optional[str] = None,
        product: Optional[str] = None,
        category: Optional[str] = None,
        date_field: Optional[str] = "date",
        amount_field: Optional[str] = "amount",
        product_field: Optional[str] = "product",
        category_field: Optional[str] = "category",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform sales analysis on the provided data.
        
        Args:
            action: Analysis action to perform (total, growth, highest_growth, etc.)
            data: Sales data to analyze
            period: Time period for analysis (day, week, month, quarter, year)
            product: Filter for specific product
            category: Filter for specific category
            date_field: Field name for date values
            amount_field: Field name for amount values
            product_field: Field name for product values
            category_field: Field name for category values
            
        Returns:
            Dictionary containing the analysis results
        """
        logger.info(f"Performing {action} analysis on sales data")
        
        # Validate inputs
        if not data:
            return {"error": "Data is required for analysis"}
        
        if not action:
            return {"error": "Action is required"}
        
        # Convert data to pandas DataFrame for easier analysis
        try:
            df = pd.DataFrame(data)
        except Exception as e:
            logger.error(f"Error converting data to DataFrame: {e}")
            return {"error": f"Invalid data format: {str(e)}"}
        
        # Check if required fields exist
        if action != "metadata" and amount_field not in df.columns:
            return {"error": f"Amount field '{amount_field}' not found in data"}
        
        # Perform the requested analysis
        if action.lower() == "total":
            return await self._get_sales_total(df, period, product, category, 
                                              date_field, amount_field, 
                                              product_field, category_field)
        elif action.lower() == "growth":
            return await self._get_sales_growth(df, period, product, category, 
                                               date_field, amount_field, 
                                               product_field, category_field)
        elif action.lower() == "highest_growth":
            return await self._get_product_with_highest_growth(df, period, category, 
                                                              date_field, amount_field, 
                                                              product_field, category_field)
        elif action.lower() == "metadata":
            return await self._get_metadata(df)
        else:
            return {"error": f"Invalid action. Choose from: total, growth, highest_growth, metadata"}
    
    async def _get_sales_total(
        self,
        df: pd.DataFrame,
        period: Optional[str],
        product: Optional[str],
        category: Optional[str],
        date_field: str,
        amount_field: str,
        product_field: str,
        category_field: str
    ) -> Dict[str, Any]:
        """
        Calculate total sales for the specified parameters.
        
        Args:
            df: Sales data as DataFrame
            period: Time period for analysis
            product: Filter for specific product
            category: Filter for specific category
            date_field: Field name for date values
            amount_field: Field name for amount values
            product_field: Field name for product values
            category_field: Field name for category values
            
        Returns:
            Dictionary containing the total sales
        """
        # Apply filters
        filtered_df = self._apply_filters(df, product, category, product_field, category_field)
        
        # Convert date field to datetime if it exists
        if date_field in filtered_df.columns:
            try:
                filtered_df[date_field] = pd.to_datetime(filtered_df[date_field])
            except Exception as e:
                logger.warning(f"Could not convert {date_field} to datetime: {e}")
        
        # Calculate total
        total_sales = filtered_df[amount_field].sum()
        
        # If period is specified and date field exists, group by period
        period_totals = {}
        if period and date_field in filtered_df.columns:
            try:
                # Group by period
                if period.lower() == "day":
                    period_df = filtered_df.groupby(filtered_df[date_field].dt.date)[amount_field].sum()
                elif period.lower() == "week":
                    period_df = filtered_df.groupby(filtered_df[date_field].dt.isocalendar().week)[amount_field].sum()
                elif period.lower() == "month":
                    period_df = filtered_df.groupby(filtered_df[date_field].dt.month)[amount_field].sum()
                elif period.lower() == "quarter":
                    period_df = filtered_df.groupby(filtered_df[date_field].dt.quarter)[amount_field].sum()
                elif period.lower() == "year":
                    period_df = filtered_df.groupby(filtered_df[date_field].dt.year)[amount_field].sum()
                else:
                    period_df = None
                
                # Convert to dictionary if grouping was successful
                if period_df is not None:
                    period_totals = period_df.to_dict()
            except Exception as e:
                logger.warning(f"Error grouping by period: {e}")
        
        # Prepare result
        result = {
            "success": True,
            "total_sales": float(total_sales),
            "currency": "USD",  # Assuming USD as default currency
            "filters": {
                "product": product,
                "category": category
            }
        }
        
        # Add period totals if available
        if period_totals:
            # Convert keys to strings for JSON serialization
            period_totals_str = {str(k): float(v) for k, v in period_totals.items()}
            result["period"] = period.lower()
            result["period_totals"] = period_totals_str
        
        return result
    
    async def _get_sales_growth(
        self,
        df: pd.DataFrame,
        period: Optional[str],
        product: Optional[str],
        category: Optional[str],
        date_field: str,
        amount_field: str,
        product_field: str,
        category_field: str
    ) -> Dict[str, Any]:
        """
        Calculate sales growth for the specified parameters.
        
        Args:
            df: Sales data as DataFrame
            period: Time period for analysis
            product: Filter for specific product
            category: Filter for specific category
            date_field: Field name for date values
            amount_field: Field name for amount values
            product_field: Field name for product values
            category_field: Field name for category values
            
        Returns:
            Dictionary containing the sales growth
        """
        # Apply filters
        filtered_df = self._apply_filters(df, product, category, product_field, category_field)
        
        # Check if date field exists
        if date_field not in filtered_df.columns:
            return {"error": f"Date field '{date_field}' not found in data"}
        
        # Convert date field to datetime
        try:
            filtered_df[date_field] = pd.to_datetime(filtered_df[date_field])
        except Exception as e:
            logger.error(f"Could not convert {date_field} to datetime: {e}")
            return {"error": f"Invalid date format in '{date_field}': {str(e)}"}
        
        # Sort by date
        filtered_df = filtered_df.sort_values(by=date_field)
        
        # Default to monthly if period not specified
        if not period:
            period = "month"
        
        # Group by period
        try:
            if period.lower() == "day":
                period_df = filtered_df.groupby(filtered_df[date_field].dt.date)[amount_field].sum()
            elif period.lower() == "week":
                period_df = filtered_df.groupby(filtered_df[date_field].dt.isocalendar().week)[amount_field].sum()
            elif period.lower() == "month":
                period_df = filtered_df.groupby(filtered_df[date_field].dt.month)[amount_field].sum()
            elif period.lower() == "quarter":
                period_df = filtered_df.groupby(filtered_df[date_field].dt.quarter)[amount_field].sum()
            elif period.lower() == "year":
                period_df = filtered_df.groupby(filtered_df[date_field].dt.year)[amount_field].sum()
            else:
                return {"error": f"Invalid period. Choose from: day, week, month, quarter, year"}
        except Exception as e:
            logger.error(f"Error grouping by period: {e}")
            return {"error": f"Error calculating growth: {str(e)}"}
        
        # Calculate growth
        if len(period_df) < 2:
            return {
                "success": True,
                "growth": None,
                "message": "Insufficient data to calculate growth (need at least 2 periods)",
                "period": period.lower(),
                "data_points": len(period_df)
            }
        
        # Calculate period-over-period growth
        period_values = period_df.values
        growth_rates = []
        
        for i in range(1, len(period_values)):
            previous = period_values[i-1]
            current = period_values[i]
            
            if previous == 0:
                # Avoid division by zero
                growth = float('inf') if current > 0 else 0
            else:
                growth = (current - previous) / previous
            
            growth_rates.append(growth)
        
        # Calculate average growth
        avg_growth = sum(growth_rates) / len(growth_rates)
        
        # Prepare result
        result = {
            "success": True,
            "period": period.lower(),
            "average_growth_rate": float(avg_growth),
            "growth_percentage": f"{avg_growth * 100:.2f}%",
            "period_count": len(period_df),
            "filters": {
                "product": product,
                "category": category
            }
        }
        
        # Add period-by-period growth if there are not too many periods
        if len(growth_rates) <= 20:
            period_keys = list(period_df.index)[1:]
            period_growth = {str(period_keys[i]): float(growth_rates[i]) for i in range(len(growth_rates))}
            result["period_growth"] = period_growth
        
        return result
    
    async def _get_product_with_highest_growth(
        self,
        df: pd.DataFrame,
        period: Optional[str],
        category: Optional[str],
        date_field: str,
        amount_field: str,
        product_field: str,
        category_field: str
    ) -> Dict[str, Any]:
        """
        Identify the product with the highest growth rate.
        
        Args:
            df: Sales data as DataFrame
            period: Time period for analysis
            category: Filter for specific category
            date_field: Field name for date values
            amount_field: Field name for amount values
            product_field: Field name for product values
            category_field: Field name for category values
            
        Returns:
            Dictionary containing the product with highest growth
        """
        # Check if required fields exist
        if product_field not in df.columns:
            return {"error": f"Product field '{product_field}' not found in data"}
        
        if date_field not in df.columns:
            return {"error": f"Date field '{date_field}' not found in data"}
        
        # Apply category filter if specified
        if category and category_field in df.columns:
            df = df[df[category_field] == category]
        
        # Convert date field to datetime
        try:
            df[date_field] = pd.to_datetime(df[date_field])
        except Exception as e:
            logger.error(f"Could not convert {date_field} to datetime: {e}")
            return {"error": f"Invalid date format in '{date_field}': {str(e)}"}
        
        # Default to monthly if period not specified
        if not period:
            period = "month"
        
        # Get unique products
        products = df[product_field].unique()
        
        if len(products) == 0:
            return {
                "success": True,
                "message": "No products found in the data",
                "highest_growth_product": None,
                "growth_rate": None
            }
        
        # Calculate growth for each product
        product_growth = {}
        
        for product in products:
            # Filter data for this product
            product_df = df[df[product_field] == product]
            
            # Group by period
            try:
                if period.lower() == "day":
                    period_df = product_df.groupby(product_df[date_field].dt.date)[amount_field].sum()
                elif period.lower() == "week":
                    period_df = product_df.groupby(product_df[date_field].dt.isocalendar().week)[amount_field].sum()
                elif period.lower() == "month":
                    period_df = product_df.groupby(product_df[date_field].dt.month)[amount_field].sum()
                elif period.lower() == "quarter":
                    period_df = product_df.groupby(product_df[date_field].dt.quarter)[amount_field].sum()
                elif period.lower() == "year":
                    period_df = product_df.groupby(product_df[date_field].dt.year)[amount_field].sum()
                else:
                    return {"error": f"Invalid period. Choose from: day, week, month, quarter, year"}
            except Exception as e:
                logger.warning(f"Error grouping by period for product {product}: {e}")
                continue
            
            # Calculate growth if enough data points
            if len(period_df) >= 2:
                # Calculate period-over-period growth
                period_values = period_df.values
                growth_rates = []
                
                for i in range(1, len(period_values)):
                    previous = period_values[i-1]
                    current = period_values[i]
                    
                    if previous == 0:
                        # Avoid division by zero
                        growth = float('inf') if current > 0 else 0
                    else:
                        growth = (current - previous) / previous
                    
                    growth_rates.append(growth)
                
                # Calculate average growth
                if growth_rates:
                    avg_growth = sum(growth_rates) / len(growth_rates)
                    product_growth[product] = avg_growth
        
        # Find product with highest growth
        if not product_growth:
            return {
                "success": True,
                "message": "Insufficient data to calculate growth for any product",
                "highest_growth_product": None,
                "growth_rate": None
            }
        
        highest_growth_product = max(product_growth.items(), key=lambda x: x[1])
        
        # Prepare result
        result = {
            "success": True,
            "highest_growth_product": highest_growth_product[0],
            "growth_rate": float(highest_growth_product[1]),
            "growth_percentage": f"{highest_growth_product[1] * 100:.2f}%",
            "period": period.lower(),
            "filters": {
                "category": category
            }
        }
        
        # Add top 5 products by growth if there are at least 5
        if len(product_growth) >= 5:
            top_products = sorted(product_growth.items(), key=lambda x: x[1], reverse=True)[:5]
            result["top_5_products"] = [
                {"product": p[0], "growth_rate": float(p[1]), "growth_percentage": f"{p[1] * 100:.2f}%"}
                for p in top_products
            ]
        
        return result
    
    async def _get_metadata(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get metadata about the sales data.
        
        Args:
            df: Sales data as DataFrame
            
        Returns:
            Dictionary containing metadata about the sales data
        """
        metadata = {
            "success": True,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns)
        }
        
        # Add summary statistics for numeric columns
        numeric_columns = df.select_dtypes(include=['number']).columns
        if len(numeric_columns) > 0:
            stats = {}
            for col in numeric_columns:
                col_stats = {
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "std": float(df[col].std())
                }
                stats[col] = col_stats
            
            metadata["numeric_stats"] = stats
        
        # Add unique value counts for categorical columns (limit to columns with few unique values)
        categorical_columns = df.select_dtypes(include=['object']).columns
        if len(categorical_columns) > 0:
            unique_values = {}
            for col in categorical_columns:
                unique_count = df[col].nunique()
                if unique_count <= 20:  # Only include if not too many unique values
                    value_counts = df[col].value_counts().to_dict()
                    # Convert keys to strings for JSON serialization
                    value_counts = {str(k): int(v) for k, v in value_counts.items()}
                    unique_values[col] = {
                        "unique_count": unique_count,
                        "value_counts": value_counts
                    }
                else:
                    unique_values[col] = {
                        "unique_count": unique_count
                    }
            
            metadata["categorical_stats"] = unique_values
        
        return metadata
    
    def _apply_filters(
        self,
        df: pd.DataFrame,
        product: Optional[str],
        category: Optional[str],
        product_field: str,
        category_field: str
    ) -> pd.DataFrame:
        """
        Apply filters to the DataFrame.
        
        Args:
            df: DataFrame to filter
            product: Filter for specific product
            category: Filter for specific category
            product_field: Field name for product values
            category_field: Field name for category values
            
        Returns:
            Filtered DataFrame
        """
        filtered_df = df.copy()
        
        # Apply product filter if specified and field exists
        if product and product_field in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[product_field] == product]
        
        # Apply category filter if specified and field exists
        if category and category_field in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[category_field] == category]
        
        return filtered_df
