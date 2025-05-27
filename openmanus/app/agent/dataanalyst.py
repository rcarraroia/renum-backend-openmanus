"""
Data Analyst agent implementation for the Renum project.

This agent specializes in analyzing and visualizing sales and financial data
based on user prompts.
"""

from typing import Dict, List, Any, Optional
import os
import json
import asyncio

from app.agent.base import BaseAgent
from app.tool.data_analysis import (
    SalesDataGenerator, 
    SalesDataStore, 
    generate_sample_data,
    DataQueryTool,
    DataVisualizationTool,
    DataReportTool
)


class DataAnalystAgent(BaseAgent):
    """
    Agent specialized in data analysis and visualization.
    
    This agent can analyze sales and financial data, generate visualizations,
    and create comprehensive reports based on natural language prompts.
    """
    
    def __init__(self, model: str = "gpt-4", temperature: float = 0.3, data_dir: str = "/tmp/data"):
        """
        Initialize the DataAnalystAgent.
        
        Args:
            model: LLM model to use
            temperature: Temperature for generation (lower = more precise)
            data_dir: Directory for storing data and visualizations
        """
        super().__init__(model=model, temperature=temperature)
        
        # Create data directory if it doesn't exist
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize data store with sample data
        self._initialize_data_store()
        
        # Register tools
        self._register_tools()
        
        # Set system prompt
        self._set_system_prompt()
    
    def _initialize_data_store(self) -> None:
        """Initialize the data store with sample data."""
        # Generate sample data file
        sample_data_file = os.path.join(self.data_dir, "sample_sales_data.csv")
        
        # Check if sample data already exists
        if not os.path.exists(sample_data_file):
            # Generate sample data
            generate_sample_data(sample_data_file, format="csv", num_records=1000)
        
        # Initialize data store
        self.data_store = SalesDataStore(sample_data_file)
    
    def _register_tools(self) -> None:
        """Register all tools for the data analyst agent."""
        # Data query tool
        query_tool = DataQueryTool(self.data_store)
        self.register_tool(query_tool)
        
        # Data visualization tool
        visualization_tool = DataVisualizationTool(self.data_store, self.data_dir)
        self.register_tool(visualization_tool)
        
        # Data report tool
        report_tool = DataReportTool(self.data_store, visualization_tool, self.data_dir)
        self.register_tool(report_tool)
        
        # Store references to tools for direct access
        self.query_tool = query_tool
        self.visualization_tool = visualization_tool
        self.report_tool = report_tool
    
    def _set_system_prompt(self) -> None:
        """Set the system prompt for the data analyst agent."""
        system_prompt = """
        You are a professional data analyst specializing in sales and financial data analysis.
        Your expertise includes querying data, creating visualizations, and generating comprehensive reports.
        
        When responding to user requests:
        1. Analyze the user's intent and identify the type of analysis they need
        2. Extract key information such as time periods, categories, and metrics of interest
        3. Use the appropriate tool to perform the requested analysis
        4. Provide a clear explanation of your findings and any insights derived from the data
        
        For data queries:
        - Consider the specific metrics the user is interested in
        - Filter data appropriately based on time periods, categories, or other criteria
        - Present results in a clear, structured format
        
        For visualizations:
        - Choose the most appropriate chart type for the data being visualized
        - Ensure visualizations have clear titles, labels, and legends
        - Explain what the visualization shows and any patterns or trends
        
        For reports:
        - Include a comprehensive overview of the data
        - Highlight key metrics and trends
        - Provide actionable insights based on the data
        
        Always aim to be helpful, clear, and responsive to the user's specific needs.
        """
        
        self.set_system_prompt(system_prompt)
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        """
        Process a user message and perform data analysis.
        
        Args:
            message: User message requesting data analysis
            
        Returns:
            Dictionary with the agent's response and any analysis results
        """
        # Process the message using the LLM and tools
        response = await self.generate_response(message)
        
        # Extract any visualization or report paths from the response
        visualization_paths = self._extract_visualization_paths(response)
        report_paths = self._extract_report_paths(response)
        
        # Collect all results
        results = {
            "response": response,
            "visualizations": [],
            "reports": []
        }
        
        # Add visualizations if any were created
        for path in visualization_paths:
            if os.path.exists(path):
                with open(path, "rb") as f:
                    import base64
                    encoded_image = base64.b64encode(f.read()).decode("utf-8")
                    results["visualizations"].append({
                        "path": path,
                        "encoded_image": encoded_image
                    })
        
        # Add reports if any were created
        for path in report_paths:
            if os.path.exists(path):
                with open(path, "r") as f:
                    content = f.read()
                    results["reports"].append({
                        "path": path,
                        "content": content
                    })
        
        return results
    
    def _extract_visualization_paths(self, response: str) -> List[str]:
        """
        Extract visualization file paths from the agent's response.
        
        Args:
            response: Agent's response text
            
        Returns:
            List of visualization file paths mentioned in the response
        """
        import re
        
        # Pattern to match visualization file paths
        pattern = r'(/tmp/.*?\.(png|jpg|svg|pdf))'
        
        # Find all matches
        matches = re.findall(pattern, response)
        
        # Extract just the file paths
        paths = [match[0] for match in matches]
        
        return paths
    
    def _extract_report_paths(self, response: str) -> List[str]:
        """
        Extract report file paths from the agent's response.
        
        Args:
            response: Agent's response text
            
        Returns:
            List of report file paths mentioned in the response
        """
        import re
        
        # Pattern to match report file paths
        pattern = r'(/tmp/.*?\.(md|json|html))'
        
        # Find all matches
        matches = re.findall(pattern, response)
        
        # Extract just the file paths
        paths = [match[0] for match in matches]
        
        return paths
    
    async def generate_sample_data(self, num_records: int = 1000, output_format: str = "csv") -> Dict[str, Any]:
        """
        Generate new sample data.
        
        Args:
            num_records: Number of records to generate
            output_format: Output format ("csv" or "json")
            
        Returns:
            Dictionary with the result of the operation
        """
        try:
            # Generate new sample data file
            sample_data_file = os.path.join(self.data_dir, f"sample_sales_data_{int(time.time())}.{output_format}")
            
            # Generate sample data
            generate_sample_data(sample_data_file, format=output_format, num_records=num_records)
            
            # Initialize new data store
            self.data_store = SalesDataStore(sample_data_file)
            
            # Update tools with new data store
            self._register_tools()
            
            return {
                "success": True,
                "message": f"Generated {num_records} sample records in {output_format} format",
                "file_path": sample_data_file
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
