"""
Data analysis tools for the Renum project.

This module provides tools for analyzing sales and financial data.
"""

from typing import Dict, List, Any, Optional
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

from app.tool.base import BaseTool
from app.tool.data_analysis.data_simulation import SalesDataStore


class DataQueryTool(BaseTool):
    """
    Tool for querying sales and financial data.
    
    This tool allows querying and filtering data based on various criteria
    such as time period, category, region, etc.
    """
    
    def __init__(self, data_store: SalesDataStore):
        """
        Initialize the DataQueryTool.
        
        Args:
            data_store: SalesDataStore instance containing the data
        """
        super().__init__(
            name="data_query",
            description="Query sales and financial data based on various criteria",
            parameters={
                "query_type": {
                    "type": "string",
                    "description": "Type of query to perform",
                    "enum": [
                        "total_sales",
                        "sales_by_category",
                        "sales_by_product",
                        "sales_by_region",
                        "sales_by_channel",
                        "product_with_highest_growth",
                        "filter_by_category",
                        "filter_by_date_range",
                        "sales_summary"
                    ]
                },
                "period": {
                    "type": "string",
                    "description": "Time period for filtering",
                    "enum": [
                        "last_7_days",
                        "last_30_days",
                        "last_90_days",
                        "last_year",
                        "previous_30_days",
                        "previous_90_days",
                        "previous_year"
                    ],
                    "required": False
                },
                "category": {
                    "type": "string",
                    "description": "Product category for filtering",
                    "required": False
                },
                "start_date": {
                    "type": "string",
                    "description": "Start date for filtering (YYYY-MM-DD format)",
                    "required": False
                },
                "end_date": {
                    "type": "string",
                    "description": "End date for filtering (YYYY-MM-DD format)",
                    "required": False
                },
                "compare_periods": {
                    "type": "string",
                    "description": "How to compare periods for growth calculations",
                    "enum": [
                        "month_over_month",
                        "quarter_over_quarter",
                        "year_over_year"
                    ],
                    "required": False
                }
            }
        )
        self.data_store = data_store
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the data query tool.
        
        Args:
            query_type: Type of query to perform
            period: Time period for filtering (optional)
            category: Product category for filtering (optional)
            start_date: Start date for filtering (optional)
            end_date: End date for filtering (optional)
            compare_periods: How to compare periods for growth calculations (optional)
            
        Returns:
            Dictionary with query results
        """
        query_type = kwargs.get("query_type")
        period = kwargs.get("period")
        category = kwargs.get("category")
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")
        compare_periods = kwargs.get("compare_periods", "month_over_month")
        
        try:
            if query_type == "total_sales":
                result = self.data_store.get_total_sales(period)
                return {"success": True, "total_sales": result}
            
            elif query_type == "sales_by_category":
                result = self.data_store.get_sales_by_category(period)
                return {"success": True, "sales_by_category": result}
            
            elif query_type == "sales_by_product":
                result = self.data_store.get_sales_by_product(category, period)
                return {"success": True, "sales_by_product": result}
            
            elif query_type == "sales_by_region":
                result = self.data_store.get_sales_by_region(period)
                return {"success": True, "sales_by_region": result}
            
            elif query_type == "sales_by_channel":
                result = self.data_store.get_sales_by_channel(period)
                return {"success": True, "sales_by_channel": result}
            
            elif query_type == "product_with_highest_growth":
                result = self.data_store.get_product_with_highest_growth(compare_periods)
                return {"success": True, "product_with_highest_growth": result}
            
            elif query_type == "filter_by_category":
                if not category:
                    return {"success": False, "error": "Category parameter is required"}
                
                result = self.data_store.filter_transactions_by_category(category)
                return {"success": True, "transactions": result}
            
            elif query_type == "filter_by_date_range":
                if not start_date or not end_date:
                    return {"success": False, "error": "Start date and end date parameters are required"}
                
                result = self.data_store.filter_transactions_by_date_range(start_date, end_date)
                return {"success": True, "transactions": result}
            
            elif query_type == "sales_summary":
                result = self.data_store.get_sales_summary(period)
                return {"success": True, "summary": result}
            
            else:
                return {"success": False, "error": f"Unknown query type: {query_type}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}


class DataVisualizationTool(BaseTool):
    """
    Tool for creating visualizations of sales and financial data.
    
    This tool generates various types of charts and graphs to visualize
    sales trends, comparisons, and distributions.
    """
    
    def __init__(self, data_store: SalesDataStore, output_dir: str = "/tmp"):
        """
        Initialize the DataVisualizationTool.
        
        Args:
            data_store: SalesDataStore instance containing the data
            output_dir: Directory to save generated visualizations
        """
        super().__init__(
            name="data_visualization",
            description="Create visualizations of sales and financial data",
            parameters={
                "visualization_type": {
                    "type": "string",
                    "description": "Type of visualization to create",
                    "enum": [
                        "sales_by_category_pie",
                        "sales_by_category_bar",
                        "sales_by_region_bar",
                        "sales_by_channel_pie",
                        "sales_trend_line",
                        "product_comparison_bar",
                        "category_growth_bar"
                    ]
                },
                "period": {
                    "type": "string",
                    "description": "Time period for filtering",
                    "enum": [
                        "last_7_days",
                        "last_30_days",
                        "last_90_days",
                        "last_year"
                    ],
                    "required": False
                },
                "category": {
                    "type": "string",
                    "description": "Product category for filtering",
                    "required": False
                },
                "top_n": {
                    "type": "integer",
                    "description": "Number of top items to include",
                    "required": False
                },
                "output_format": {
                    "type": "string",
                    "description": "Output format for the visualization",
                    "enum": ["png", "jpg", "svg", "pdf"],
                    "required": False
                },
                "title": {
                    "type": "string",
                    "description": "Custom title for the visualization",
                    "required": False
                }
            }
        )
        self.data_store = data_store
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the data visualization tool.
        
        Args:
            visualization_type: Type of visualization to create
            period: Time period for filtering (optional)
            category: Product category for filtering (optional)
            top_n: Number of top items to include (optional)
            output_format: Output format for the visualization (optional)
            title: Custom title for the visualization (optional)
            
        Returns:
            Dictionary with visualization results, including file path
        """
        visualization_type = kwargs.get("visualization_type")
        period = kwargs.get("period")
        category = kwargs.get("category")
        top_n = kwargs.get("top_n", 5)
        output_format = kwargs.get("output_format", "png")
        title = kwargs.get("title")
        
        try:
            # Set up the figure
            plt.figure(figsize=(10, 6))
            sns.set_style("whitegrid")
            
            # Generate timestamp for unique filename
            import time
            timestamp = int(time.time())
            
            # Create visualization based on type
            if visualization_type == "sales_by_category_pie":
                file_path = self._create_sales_by_category_pie(period, title, timestamp, output_format)
            
            elif visualization_type == "sales_by_category_bar":
                file_path = self._create_sales_by_category_bar(period, top_n, title, timestamp, output_format)
            
            elif visualization_type == "sales_by_region_bar":
                file_path = self._create_sales_by_region_bar(period, title, timestamp, output_format)
            
            elif visualization_type == "sales_by_channel_pie":
                file_path = self._create_sales_by_channel_pie(period, title, timestamp, output_format)
            
            elif visualization_type == "sales_trend_line":
                file_path = self._create_sales_trend_line(period, title, timestamp, output_format)
            
            elif visualization_type == "product_comparison_bar":
                if not category:
                    return {"success": False, "error": "Category parameter is required for product comparison"}
                
                file_path = self._create_product_comparison_bar(category, period, top_n, title, timestamp, output_format)
            
            elif visualization_type == "category_growth_bar":
                file_path = self._create_category_growth_bar(title, timestamp, output_format)
            
            else:
                return {"success": False, "error": f"Unknown visualization type: {visualization_type}"}
            
            # Generate base64 encoded image for inline display
            with open(file_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            
            return {
                "success": True,
                "file_path": file_path,
                "visualization_type": visualization_type,
                "encoded_image": encoded_image
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _create_sales_by_category_pie(self, period, title, timestamp, output_format):
        """Create a pie chart of sales by category."""
        sales_by_category = self.data_store.get_sales_by_category(period)
        
        # Sort data by value
        sorted_data = dict(sorted(sales_by_category.items(), key=lambda x: x[1], reverse=True))
        
        # Create pie chart
        plt.pie(
            sorted_data.values(),
            labels=sorted_data.keys(),
            autopct='%1.1f%%',
            startangle=90,
            shadow=True
        )
        
        # Set title
        if title:
            plt.title(title)
        else:
            period_text = f" ({period.replace('_', ' ')})" if period else ""
            plt.title(f"Sales by Category{period_text}")
        
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        # Save and return file path
        file_path = os.path.join(self.output_dir, f"sales_by_category_pie_{timestamp}.{output_format}")
        plt.savefig(file_path, bbox_inches='tight')
        plt.close()
        
        return file_path
    
    def _create_sales_by_category_bar(self, period, top_n, title, timestamp, output_format):
        """Create a bar chart of sales by category."""
        sales_by_category = self.data_store.get_sales_by_category(period)
        
        # Sort data by value and take top N
        sorted_data = dict(sorted(sales_by_category.items(), key=lambda x: x[1], reverse=True)[:top_n])
        
        # Create bar chart
        plt.bar(sorted_data.keys(), sorted_data.values(), color=sns.color_palette("viridis", len(sorted_data)))
        
        # Set title and labels
        if title:
            plt.title(title)
        else:
            period_text = f" ({period.replace('_', ' ')})" if period else ""
            plt.title(f"Top {len(sorted_data)} Categories by Sales{period_text}")
        
        plt.xlabel("Category")
        plt.ylabel("Sales Amount ($)")
        plt.xticks(rotation=45, ha="right")
        
        # Add value labels on top of bars
        for i, (category, value) in enumerate(sorted_data.items()):
            plt.text(i, value + (max(sorted_data.values()) * 0.02), f"${value:,.2f}", 
                     ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        # Save and return file path
        file_path = os.path.join(self.output_dir, f"sales_by_category_bar_{timestamp}.{output_format}")
        plt.savefig(file_path, bbox_inches='tight')
        plt.close()
        
        return file_path
    
    def _create_sales_by_region_bar(self, period, title, timestamp, output_format):
        """Create a bar chart of sales by region."""
        sales_by_region = self.data_store.get_sales_by_region(period)
        
        # Sort data by value
        sorted_data = dict(sorted(sales_by_region.items(), key=lambda x: x[1], reverse=True))
        
        # Create bar chart
        plt.bar(sorted_data.keys(), sorted_data.values(), color=sns.color_palette("muted", len(sorted_data)))
        
        # Set title and labels
        if title:
            plt.title(title)
        else:
            period_text = f" ({period.replace('_', ' ')})" if period else ""
            plt.title(f"Sales by Region{period_text}")
        
        plt.xlabel("Region")
        plt.ylabel("Sales Amount ($)")
        
        # Add value labels on top of bars
        for i, (region, value) in enumerate(sorted_data.items()):
            plt.text(i, value + (max(sorted_data.values()) * 0.02), f"${value:,.2f}", 
                     ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        # Save and return file path
        file_path = os.path.join(self.output_dir, f"sales_by_region_bar_{timestamp}.{output_format}")
        plt.savefig(file_path, bbox_inches='tight')
        plt.close()
        
        return file_path
    
    def _create_sales_by_channel_pie(self, period, title, timestamp, output_format):
        """Create a pie chart of sales by channel."""
        sales_by_channel = self.data_store.get_sales_by_channel(period)
        
        # Create pie chart
        plt.pie(
            sales_by_channel.values(),
            labels=sales_by_channel.keys(),
            autopct='%1.1f%%',
            startangle=90,
            shadow=True,
            colors=sns.color_palette("pastel", len(sales_by_channel))
        )
        
        # Set title
        if title:
            plt.title(title)
        else:
            period_text = f" ({period.replace('_', ' ')})" if period else ""
            plt.title(f"Sales by Channel{period_text}")
        
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        # Save and return file path
        file_path = os.path.join(self.output_dir, f"sales_by_channel_pie_{timestamp}.{output_format}")
        plt.savefig(file_path, bbox_inches='tight')
        plt.close()
        
        return file_path
    
    def _create_sales_trend_line(self, period, title, timestamp, output_format):
        """Create a line chart of sales trend over time."""
        # Get all transactions for the period
        if period:
            transactions = self.data_store._filter_by_period(period)
        else:
            transactions = self.data_store.data
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(transactions)
        
        # Ensure date column is datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Group by date and sum sales
        daily_sales = df.groupby('date')['final_amount'].sum().reset_index()
        
        # Sort by date
        daily_sales = daily_sales.sort_values('date')
        
        # Create line chart
        plt.plot(daily_sales['date'], daily_sales['final_amount'], marker='o', linestyle='-', color='#1f77b4')
        
        # Set title and labels
        if title:
            plt.title(title)
        else:
            period_text = f" ({period.replace('_', ' ')})" if period else ""
            plt.title(f"Sales Trend{period_text}")
        
        plt.xlabel("Date")
        plt.ylabel("Sales Amount ($)")
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Format x-axis dates
        plt.gcf().autofmt_xdate()
        
        # Add trend line
        from scipy import stats
        if len(daily_sales) > 1:
            x = range(len(daily_sales))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, daily_sales['final_amount'])
            plt.plot(daily_sales['date'], intercept + slope * x, 'r--', label=f'Trend (r²={r_value**2:.2f})')
            plt.legend()
        
        plt.tight_layout()
        
        # Save and return file path
        file_path = os.path.join(self.output_dir, f"sales_trend_line_{timestamp}.{output_format}")
        plt.savefig(file_path, bbox_inches='tight')
        plt.close()
        
        return file_path
    
    def _create_product_comparison_bar(self, category, period, top_n, title, timestamp, output_format):
        """Create a bar chart comparing products within a category."""
        sales_by_product = self.data_store.get_sales_by_product(category, period)
        
        # Sort data by value and take top N
        sorted_data = dict(sorted(sales_by_product.items(), key=lambda x: x[1], reverse=True)[:top_n])
        
        # Create bar chart
        plt.bar(sorted_data.keys(), sorted_data.values(), color=sns.color_palette("deep", len(sorted_data)))
        
        # Set title and labels
        if title:
            plt.title(title)
        else:
            period_text = f" ({period.replace('_', ' ')})" if period else ""
            plt.title(f"Top {len(sorted_data)} Products in {category} Category{period_text}")
        
        plt.xlabel("Product")
        plt.ylabel("Sales Amount ($)")
        plt.xticks(rotation=45, ha="right")
        
        # Add value labels on top of bars
        for i, (product, value) in enumerate(sorted_data.items()):
            plt.text(i, value + (max(sorted_data.values()) * 0.02), f"${value:,.2f}", 
                     ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        # Save and return file path
        file_path = os.path.join(self.output_dir, f"product_comparison_bar_{timestamp}.{output_format}")
        plt.savefig(file_path, bbox_inches='tight')
        plt.close()
        
        return file_path
    
    def _create_category_growth_bar(self, title, timestamp, output_format):
        """Create a bar chart showing growth by category."""
        # Get current period sales
        current_sales = self.data_store.get_sales_by_category("last_30_days")
        
        # Get previous period sales
        previous_sales = self.data_store.get_sales_by_category("previous_30_days")
        
        # Calculate growth for each category
        growth_by_category = {}
        for category, current_amount in current_sales.items():
            previous_amount = previous_sales.get(category, 0)
            
            if previous_amount > 0:
                growth_percent = ((current_amount - previous_amount) / previous_amount) * 100
            else:
                growth_percent = 100  # If no previous sales, consider it 100% growth
            
            growth_by_category[category] = growth_percent
        
        # Sort by growth percentage and take top categories
        sorted_data = dict(sorted(growth_by_category.items(), key=lambda x: x[1], reverse=True))
        
        # Create bar chart
        bars = plt.bar(sorted_data.keys(), sorted_data.values())
        
        # Color bars based on growth (positive = green, negative = red)
        for i, (category, value) in enumerate(sorted_data.items()):
            if value >= 0:
                bars[i].set_color('green')
            else:
                bars[i].set_color('red')
        
        # Set title and labels
        if title:
            plt.title(title)
        else:
            plt.title("Category Growth (Month over Month)")
        
        plt.xlabel("Category")
        plt.ylabel("Growth Percentage (%)")
        plt.xticks(rotation=45, ha="right")
        
        # Add value labels on top of bars
        for i, (category, value) in enumerate(sorted_data.items()):
            va = 'bottom' if value >= 0 else 'top'
            offset = max(sorted_data.values()) * 0.02 if value >= 0 else -max(sorted_data.values()) * 0.02
            plt.text(i, value + offset, f"{value:.1f}%", 
                     ha='center', va=va, fontsize=9)
        
        # Add horizontal line at y=0
        plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        plt.tight_layout()
        
        # Save and return file path
        file_path = os.path.join(self.output_dir, f"category_growth_bar_{timestamp}.{output_format}")
        plt.savefig(file_path, bbox_inches='tight')
        plt.close()
        
        return file_path


class DataReportTool(BaseTool):
    """
    Tool for generating comprehensive data reports.
    
    This tool creates detailed reports combining multiple analyses and visualizations.
    """
    
    def __init__(self, data_store: SalesDataStore, visualization_tool: DataVisualizationTool, output_dir: str = "/tmp"):
        """
        Initialize the DataReportTool.
        
        Args:
            data_store: SalesDataStore instance containing the data
            visualization_tool: DataVisualizationTool instance for creating visualizations
            output_dir: Directory to save generated reports
        """
        super().__init__(
            name="data_report",
            description="Generate comprehensive data reports",
            parameters={
                "report_type": {
                    "type": "string",
                    "description": "Type of report to generate",
                    "enum": [
                        "sales_summary",
                        "category_analysis",
                        "product_performance",
                        "regional_analysis",
                        "channel_performance",
                        "growth_analysis"
                    ]
                },
                "period": {
                    "type": "string",
                    "description": "Time period for the report",
                    "enum": [
                        "last_7_days",
                        "last_30_days",
                        "last_90_days",
                        "last_year"
                    ],
                    "required": False
                },
                "category": {
                    "type": "string",
                    "description": "Product category for category-specific reports",
                    "required": False
                },
                "output_format": {
                    "type": "string",
                    "description": "Output format for the report",
                    "enum": ["json", "markdown", "html"],
                    "required": False
                }
            }
        )
        self.data_store = data_store
        self.visualization_tool = visualization_tool
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the data report tool.
        
        Args:
            report_type: Type of report to generate
            period: Time period for the report (optional)
            category: Product category for category-specific reports (optional)
            output_format: Output format for the report (optional)
            
        Returns:
            Dictionary with report results, including file path and content
        """
        report_type = kwargs.get("report_type")
        period = kwargs.get("period", "last_30_days")
        category = kwargs.get("category")
        output_format = kwargs.get("output_format", "markdown")
        
        try:
            # Generate timestamp for unique filename
            import time
            timestamp = int(time.time())
            
            # Create report based on type
            if report_type == "sales_summary":
                report_content, visualizations = await self._create_sales_summary_report(period, timestamp)
            
            elif report_type == "category_analysis":
                if not category:
                    return {"success": False, "error": "Category parameter is required for category analysis"}
                
                report_content, visualizations = await self._create_category_analysis_report(category, period, timestamp)
            
            elif report_type == "product_performance":
                report_content, visualizations = await self._create_product_performance_report(period, timestamp)
            
            elif report_type == "regional_analysis":
                report_content, visualizations = await self._create_regional_analysis_report(period, timestamp)
            
            elif report_type == "channel_performance":
                report_content, visualizations = await self._create_channel_performance_report(period, timestamp)
            
            elif report_type == "growth_analysis":
                report_content, visualizations = await self._create_growth_analysis_report(timestamp)
            
            else:
                return {"success": False, "error": f"Unknown report type: {report_type}"}
            
            # Format report based on output format
            if output_format == "json":
                formatted_report = self._format_report_as_json(report_content, visualizations)
                file_extension = "json"
            elif output_format == "html":
                formatted_report = self._format_report_as_html(report_content, visualizations)
                file_extension = "html"
            else:  # Default to markdown
                formatted_report = self._format_report_as_markdown(report_content, visualizations)
                file_extension = "md"
            
            # Save report to file
            file_path = os.path.join(self.output_dir, f"{report_type}_{timestamp}.{file_extension}")
            with open(file_path, "w") as f:
                f.write(formatted_report)
            
            return {
                "success": True,
                "file_path": file_path,
                "report_type": report_type,
                "period": period,
                "content": formatted_report
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _create_sales_summary_report(self, period, timestamp):
        """Create a sales summary report."""
        # Get sales summary data
        summary = self.data_store.get_sales_summary(period)
        
        # Generate visualizations
        viz1 = await self.visualization_tool.execute(
            visualization_type="sales_by_category_pie",
            period=period,
            title=f"Sales by Category ({period.replace('_', ' ')})"
        )
        
        viz2 = await self.visualization_tool.execute(
            visualization_type="sales_trend_line",
            period=period,
            title=f"Sales Trend ({period.replace('_', ' ')})"
        )
        
        # Prepare report content
        report_content = {
            "title": f"Sales Summary Report - {period.replace('_', ' ').title()}",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "period": period,
            "summary": summary,
            "sections": [
                {
                    "title": "Overview",
                    "content": f"This report provides a summary of sales performance for the {period.replace('_', ' ')} period. The total sales for this period were ${summary['total_sales']:,.2f} across {summary['total_transactions']} transactions, with an average transaction value of ${summary['average_transaction']:,.2f}."
                },
                {
                    "title": "Top Categories",
                    "content": "The following categories were the top performers during this period:",
                    "data": [
                        {"category": item["category"], "amount": item["amount"]}
                        for item in summary["top_categories"]
                    ]
                },
                {
                    "title": "Top Products",
                    "content": "The following products were the top sellers during this period:",
                    "data": [
                        {"product": item["product"], "amount": item["amount"]}
                        for item in summary["top_products"]
                    ]
                },
                {
                    "title": "Sales by Channel",
                    "content": "The distribution of sales across different channels:",
                    "data": [
                        {"channel": item["channel"], "amount": item["amount"]}
                        for item in summary["sales_by_channel"]
                    ]
                }
            ]
        }
        
        visualizations = [viz1, viz2]
        
        return report_content, visualizations
    
    async def _create_category_analysis_report(self, category, period, timestamp):
        """Create a category analysis report."""
        # Get category data
        category_sales = self.data_store.get_sales_by_product(category, period)
        
        # Generate visualizations
        viz1 = await self.visualization_tool.execute(
            visualization_type="product_comparison_bar",
            category=category,
            period=period,
            title=f"Product Sales in {category} Category ({period.replace('_', ' ')})"
        )
        
        # Prepare report content
        total_category_sales = sum(category_sales.values())
        top_products = sorted(category_sales.items(), key=lambda x: x[1], reverse=True)[:5]
        
        report_content = {
            "title": f"{category} Category Analysis - {period.replace('_', ' ').title()}",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "period": period,
            "category": category,
            "total_sales": total_category_sales,
            "sections": [
                {
                    "title": "Overview",
                    "content": f"This report provides an analysis of the {category} category for the {period.replace('_', ' ')} period. The total sales for this category were ${total_category_sales:,.2f}."
                },
                {
                    "title": "Top Products",
                    "content": f"The following products were the top performers in the {category} category:",
                    "data": [
                        {"product": product, "amount": amount, "percentage": (amount / total_category_sales) * 100}
                        for product, amount in top_products
                    ]
                },
                {
                    "title": "Product Distribution",
                    "content": f"The {category} category contains {len(category_sales)} products. The top 5 products account for {sum(amount for _, amount in top_products) / total_category_sales * 100:.1f}% of the category's sales."
                }
            ]
        }
        
        visualizations = [viz1]
        
        return report_content, visualizations
    
    async def _create_product_performance_report(self, period, timestamp):
        """Create a product performance report."""
        # Get product data
        product_growth = self.data_store.get_product_with_highest_growth("month_over_month")
        
        # Get sales summary
        summary = self.data_store.get_sales_summary(period)
        
        # Generate visualizations
        viz1 = await self.visualization_tool.execute(
            visualization_type="sales_by_category_bar",
            period=period,
            title=f"Top Categories by Sales ({period.replace('_', ' ')})"
        )
        
        # Prepare report content
        report_content = {
            "title": f"Product Performance Report - {period.replace('_', ' ').title()}",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "period": period,
            "sections": [
                {
                    "title": "Overview",
                    "content": f"This report analyzes product performance for the {period.replace('_', ' ')} period. The total sales for this period were ${summary['total_sales']:,.2f}."
                },
                {
                    "title": "Top Performing Products",
                    "content": "The following products were the top performers during this period:",
                    "data": [
                        {"product": item["product"], "amount": item["amount"]}
                        for item in summary["top_products"]
                    ]
                },
                {
                    "title": "Highest Growth Product",
                    "content": f"The product with the highest growth was {product_growth['product']} with a growth of {product_growth['metrics']['growth_percent']}% compared to the previous period. Sales increased from ${product_growth['metrics']['previous_sales']:,.2f} to ${product_growth['metrics']['current_sales']:,.2f}."
                }
            ]
        }
        
        visualizations = [viz1]
        
        return report_content, visualizations
    
    async def _create_regional_analysis_report(self, period, timestamp):
        """Create a regional analysis report."""
        # Get regional data
        sales_by_region = self.data_store.get_sales_by_region(period)
        
        # Generate visualizations
        viz1 = await self.visualization_tool.execute(
            visualization_type="sales_by_region_bar",
            period=period,
            title=f"Sales by Region ({period.replace('_', ' ')})"
        )
        
        # Prepare report content
        total_sales = sum(sales_by_region.values())
        regions_sorted = sorted(sales_by_region.items(), key=lambda x: x[1], reverse=True)
        
        report_content = {
            "title": f"Regional Analysis Report - {period.replace('_', ' ').title()}",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "period": period,
            "total_sales": total_sales,
            "sections": [
                {
                    "title": "Overview",
                    "content": f"This report analyzes sales performance by region for the {period.replace('_', ' ')} period. The total sales for this period were ${total_sales:,.2f}."
                },
                {
                    "title": "Regional Performance",
                    "content": "The following shows the sales performance by region:",
                    "data": [
                        {"region": region, "amount": amount, "percentage": (amount / total_sales) * 100}
                        for region, amount in regions_sorted
                    ]
                },
                {
                    "title": "Top Performing Region",
                    "content": f"The top performing region was {regions_sorted[0][0]} with ${regions_sorted[0][1]:,.2f} in sales, representing {(regions_sorted[0][1] / total_sales) * 100:.1f}% of total sales."
                }
            ]
        }
        
        visualizations = [viz1]
        
        return report_content, visualizations
    
    async def _create_channel_performance_report(self, period, timestamp):
        """Create a channel performance report."""
        # Get channel data
        sales_by_channel = self.data_store.get_sales_by_channel(period)
        
        # Generate visualizations
        viz1 = await self.visualization_tool.execute(
            visualization_type="sales_by_channel_pie",
            period=period,
            title=f"Sales by Channel ({period.replace('_', ' ')})"
        )
        
        # Prepare report content
        total_sales = sum(sales_by_channel.values())
        channels_sorted = sorted(sales_by_channel.items(), key=lambda x: x[1], reverse=True)
        
        report_content = {
            "title": f"Channel Performance Report - {period.replace('_', ' ').title()}",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "period": period,
            "total_sales": total_sales,
            "sections": [
                {
                    "title": "Overview",
                    "content": f"This report analyzes sales performance by channel for the {period.replace('_', ' ')} period. The total sales for this period were ${total_sales:,.2f}."
                },
                {
                    "title": "Channel Performance",
                    "content": "The following shows the sales performance by channel:",
                    "data": [
                        {"channel": channel, "amount": amount, "percentage": (amount / total_sales) * 100}
                        for channel, amount in channels_sorted
                    ]
                },
                {
                    "title": "Top Performing Channel",
                    "content": f"The top performing channel was {channels_sorted[0][0]} with ${channels_sorted[0][1]:,.2f} in sales, representing {(channels_sorted[0][1] / total_sales) * 100:.1f}% of total sales."
                }
            ]
        }
        
        visualizations = [viz1]
        
        return report_content, visualizations
    
    async def _create_growth_analysis_report(self, timestamp):
        """Create a growth analysis report."""
        # Generate visualizations
        viz1 = await self.visualization_tool.execute(
            visualization_type="category_growth_bar",
            title="Category Growth (Month over Month)"
        )
        
        # Get product with highest growth
        product_growth_mom = self.data_store.get_product_with_highest_growth("month_over_month")
        product_growth_qoq = self.data_store.get_product_with_highest_growth("quarter_over_quarter")
        product_growth_yoy = self.data_store.get_product_with_highest_growth("year_over_year")
        
        # Prepare report content
        report_content = {
            "title": "Growth Analysis Report",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sections": [
                {
                    "title": "Overview",
                    "content": "This report analyzes growth trends across different time periods, highlighting the products and categories with the highest growth rates."
                },
                {
                    "title": "Month-over-Month Growth",
                    "content": f"The product with the highest month-over-month growth was {product_growth_mom['product']} with a growth of {product_growth_mom['metrics']['growth_percent']}%. Sales increased from ${product_growth_mom['metrics']['previous_sales']:,.2f} to ${product_growth_mom['metrics']['current_sales']:,.2f}."
                },
                {
                    "title": "Quarter-over-Quarter Growth",
                    "content": f"The product with the highest quarter-over-quarter growth was {product_growth_qoq['product']} with a growth of {product_growth_qoq['metrics']['growth_percent']}%. Sales increased from ${product_growth_qoq['metrics']['previous_sales']:,.2f} to ${product_growth_qoq['metrics']['current_sales']:,.2f}."
                },
                {
                    "title": "Year-over-Year Growth",
                    "content": f"The product with the highest year-over-year growth was {product_growth_yoy['product']} with a growth of {product_growth_yoy['metrics']['growth_percent']}%. Sales increased from ${product_growth_yoy['metrics']['previous_sales']:,.2f} to ${product_growth_yoy['metrics']['current_sales']:,.2f}."
                }
            ]
        }
        
        visualizations = [viz1]
        
        return report_content, visualizations
    
    def _format_report_as_json(self, report_content, visualizations):
        """Format report as JSON."""
        # Add visualization paths to report content
        report_content["visualizations"] = [
            {"type": viz["visualization_type"], "path": viz["file_path"]}
            for viz in visualizations if viz["success"]
        ]
        
        return json.dumps(report_content, indent=2)
    
    def _format_report_as_markdown(self, report_content, visualizations):
        """Format report as Markdown."""
        md = f"# {report_content['title']}\n\n"
        md += f"*Generated at: {report_content['generated_at']}*\n\n"
        
        # Add sections
        for section in report_content["sections"]:
            md += f"## {section['title']}\n\n"
            md += f"{section['content']}\n\n"
            
            # Add data tables if present
            if "data" in section:
                if section["data"]:
                    # Get column names from first item
                    columns = section["data"][0].keys()
                    
                    # Create table header
                    md += "| " + " | ".join(col.title() for col in columns) + " |\n"
                    md += "| " + " | ".join("---" for _ in columns) + " |\n"
                    
                    # Add table rows
                    for item in section["data"]:
                        row = []
                        for col in columns:
                            value = item[col]
                            if isinstance(value, float):
                                if col.lower() in ["amount", "sales"]:
                                    formatted = f"${value:,.2f}"
                                elif col.lower() in ["percentage", "growth"]:
                                    formatted = f"{value:.1f}%"
                                else:
                                    formatted = f"{value:.2f}"
                            else:
                                formatted = str(value)
                            row.append(formatted)
                        md += "| " + " | ".join(row) + " |\n"
                    
                    md += "\n"
        
        # Add visualizations
        if visualizations:
            md += "## Visualizations\n\n"
            for viz in visualizations:
                if viz["success"]:
                    md += f"### {viz['visualization_type'].replace('_', ' ').title()}\n\n"
                    md += f"![{viz['visualization_type']}]({viz['file_path']})\n\n"
        
        return md
    
    def _format_report_as_html(self, report_content, visualizations):
        """Format report as HTML."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{report_content['title']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #2980b9; margin-top: 30px; }}
        h3 {{ color: #3498db; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ text-align: left; padding: 12px; }}
        th {{ background-color: #3498db; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .visualization {{ margin: 30px 0; text-align: center; }}
        .visualization img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
        .meta {{ font-style: italic; color: #7f8c8d; margin-bottom: 30px; }}
    </style>
</head>
<body>
    <h1>{report_content['title']}</h1>
    <div class="meta">Generated at: {report_content['generated_at']}</div>
"""
        
        # Add sections
        for section in report_content["sections"]:
            html += f"<h2>{section['title']}</h2>\n"
            html += f"<p>{section['content']}</p>\n"
            
            # Add data tables if present
            if "data" in section and section["data"]:
                html += "<table>\n<thead>\n<tr>\n"
                
                # Get column names from first item
                columns = section["data"][0].keys()
                
                # Create table header
                for col in columns:
                    html += f"<th>{col.title()}</th>\n"
                html += "</tr>\n</thead>\n<tbody>\n"
                
                # Add table rows
                for item in section["data"]:
                    html += "<tr>\n"
                    for col in columns:
                        value = item[col]
                        if isinstance(value, float):
                            if col.lower() in ["amount", "sales"]:
                                formatted = f"${value:,.2f}"
                            elif col.lower() in ["percentage", "growth"]:
                                formatted = f"{value:.1f}%"
                            else:
                                formatted = f"{value:.2f}"
                        else:
                            formatted = str(value)
                        html += f"<td>{formatted}</td>\n"
                    html += "</tr>\n"
                
                html += "</tbody>\n</table>\n"
        
        # Add visualizations
        if visualizations:
            html += "<h2>Visualizations</h2>\n"
            for viz in visualizations:
                if viz["success"]:
                    html += f"<div class='visualization'>\n"
                    html += f"<h3>{viz['visualization_type'].replace('_', ' ').title()}</h3>\n"
                    html += f"<img src='data:image/png;base64,{viz['encoded_image']}' alt='{viz['visualization_type']}' />\n"
                    html += "</div>\n"
        
        html += """
</body>
</html>
"""
        
        return html
