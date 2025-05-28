"""
API endpoints for Data Analyst Agent.

This module defines the RESTful API endpoints for the Data Analyst Agent,
allowing interaction with the agent's tools and capabilities.
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import datetime
from app.process.factory import AgentProcessFactory
from app.agent.data_analyst_prompt import DATA_ANALYST_SYSTEM_PROMPT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/agents/data-analyst",
    tags=["data-analyst"],
    responses={404: {"description": "Not found"}},
)

# Define request and response models
class DataLoaderRequest(BaseModel):
    source: str = Field(..., description="Path to the data source (file path or connection string)")
    source_type: Optional[str] = Field(None, description="Type of the source (csv, json, database)")
    cache: Optional[bool] = Field(True, description="Whether to cache the loaded data")
    query_params: Optional[Dict[str, Any]] = Field(None, description="Additional parameters for database queries")

class SalesAnalysisRequest(BaseModel):
    action: str = Field(..., description="Analysis action to perform (total, growth, highest_growth, etc.)")
    data: List[Dict[str, Any]] = Field(..., description="Sales data to analyze")
    period: Optional[str] = Field(None, description="Time period for analysis (day, week, month, quarter, year)")
    product: Optional[str] = Field(None, description="Filter for specific product")
    category: Optional[str] = Field(None, description="Filter for specific category")
    date_field: Optional[str] = Field("date", description="Field name for date values")
    amount_field: Optional[str] = Field("amount", description="Field name for amount values")
    product_field: Optional[str] = Field("product", description="Field name for product values")
    category_field: Optional[str] = Field("category", description="Field name for category values")

class FilteringRequest(BaseModel):
    data: List[Dict[str, Any]] = Field(..., description="Data to filter and transform")
    filters: Optional[Dict[str, Any]] = Field(None, description="Dictionary of field-value pairs to filter by")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: Optional[str] = Field("asc", description="Sort order (asc or desc)")
    limit: Optional[int] = Field(None, description="Maximum number of results to return")
    group_by: Optional[str] = Field(None, description="Field to group by")
    aggregate: Optional[Dict[str, str]] = Field(None, description="Dictionary of field-aggregation pairs for grouped data")

class PromptRequest(BaseModel):
    prompt: str = Field(..., description="User prompt for the Data Analyst Agent")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for continuing an existing conversation")

class AgentResponse(BaseModel):
    response: str = Field(..., description="Response from the agent")
    conversation_id: str = Field(..., description="Conversation ID for continuing the conversation")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata about the response")

# Initialize agent factory
agent_factory = AgentProcessFactory()

@router.post("/data-loader", response_model=Dict[str, Any], summary="Load data from various sources")
async def load_data(request: DataLoaderRequest):
    """
    Load data from the specified source.
    
    This endpoint uses the DataLoaderTool to load and cache data from
    various sources including CSV files, JSON files, and databases.
    """
    try:
        # Create agent instance if needed
        agent_id = "data_analyst_loader"
        if not agent_factory.agent_exists(agent_id):
            agent_factory.create_agent(agent_id, DATA_ANALYST_SYSTEM_PROMPT)
        
        # Prepare tool parameters
        tool_params = {
            "source": request.source,
            "source_type": request.source_type,
            "cache": request.cache,
            "query_params": request.query_params
        }
        
        # Create prompt for the agent
        prompt = f"""
        Please use the DataLoaderTool to load data with the following parameters:
        - Source: {request.source}
        - Source Type: {request.source_type or '[Auto-detect]'}
        - Cache: {request.cache}
        - Query Parameters: {request.query_params or '[None]'}
        """
        
        # Send prompt to agent
        response = await agent_factory.send_prompt_to_agent(agent_id, prompt)
        
        # Extract data from response
        # In a real implementation, this would parse the agent's response
        # For now, we'll directly call the tool
        from app.tool.data_analysis.data_loader import DataLoaderTool
        loader_tool = DataLoaderTool()
        loader_result = await loader_tool._arun(**tool_params)
        
        return loader_result
        
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sales-analysis", response_model=Dict[str, Any], summary="Analyze sales data")
async def analyze_sales(request: SalesAnalysisRequest):
    """
    Perform sales analysis on the provided data.
    
    This endpoint uses the SalesAnalysisTool to calculate sales totals,
    identify growth trends, and perform other sales-related analyses.
    """
    try:
        # Create agent instance if needed
        agent_id = "data_analyst_sales"
        if not agent_factory.agent_exists(agent_id):
            agent_factory.create_agent(agent_id, DATA_ANALYST_SYSTEM_PROMPT)
        
        # Prepare tool parameters
        tool_params = {
            "action": request.action,
            "data": request.data,
            "period": request.period,
            "product": request.product,
            "category": request.category,
            "date_field": request.date_field,
            "amount_field": request.amount_field,
            "product_field": request.product_field,
            "category_field": request.category_field
        }
        
        # Create prompt for the agent
        prompt = f"""
        Please use the SalesAnalysisTool to analyze sales data with the following parameters:
        - Action: {request.action}
        - Period: {request.period or '[Not specified]'}
        - Product: {request.product or '[All products]'}
        - Category: {request.category or '[All categories]'}
        """
        
        # Send prompt to agent
        response = await agent_factory.send_prompt_to_agent(agent_id, prompt)
        
        # Extract analysis from response
        # In a real implementation, this would parse the agent's response
        # For now, we'll directly call the tool
        from app.tool.data_analysis.sales_analysis import SalesAnalysisTool
        sales_tool = SalesAnalysisTool()
        sales_result = await sales_tool._arun(**tool_params)
        
        return sales_result
        
    except Exception as e:
        logger.error(f"Error analyzing sales data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/filtering", response_model=Dict[str, Any], summary="Filter and transform data")
async def filter_data(request: FilteringRequest):
    """
    Filter and transform the provided data.
    
    This endpoint uses the FilteringTool to apply filters, sorting,
    grouping, and aggregation to the data.
    """
    try:
        # Create agent instance if needed
        agent_id = "data_analyst_filter"
        if not agent_factory.agent_exists(agent_id):
            agent_factory.create_agent(agent_id, DATA_ANALYST_SYSTEM_PROMPT)
        
        # Prepare tool parameters
        tool_params = {
            "data": request.data,
            "filters": request.filters,
            "sort_by": request.sort_by,
            "sort_order": request.sort_order,
            "limit": request.limit,
            "group_by": request.group_by,
            "aggregate": request.aggregate
        }
        
        # Create prompt for the agent
        prompt = f"""
        Please use the FilteringTool to filter and transform data with the following parameters:
        - Filters: {request.filters or '[None]'}
        - Sort By: {request.sort_by or '[None]'}
        - Sort Order: {request.sort_order}
        - Limit: {request.limit or '[None]'}
        - Group By: {request.group_by or '[None]'}
        """
        
        # Send prompt to agent
        response = await agent_factory.send_prompt_to_agent(agent_id, prompt)
        
        # Extract filtered data from response
        # In a real implementation, this would parse the agent's response
        # For now, we'll directly call the tool
        from app.tool.data_analysis.filtering import FilteringTool
        filter_tool = FilteringTool()
        filter_result = await filter_tool._arun(**tool_params)
        
        return filter_result
        
    except Exception as e:
        logger.error(f"Error filtering data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/prompt", response_model=AgentResponse, summary="Send a prompt to the Data Analyst Agent")
async def send_prompt(request: PromptRequest):
    """
    Send a prompt to the Data Analyst Agent and get a response.
    
    This endpoint allows free-form interaction with the agent, which will
    use its tools and capabilities to respond appropriately.
    """
    try:
        # Create or get agent instance
        agent_id = request.conversation_id or "data_analyst_" + str(hash(request.prompt))[:8]
        if not agent_factory.agent_exists(agent_id):
            agent_factory.create_agent(agent_id, DATA_ANALYST_SYSTEM_PROMPT)
        
        # Send prompt to agent
        response = await agent_factory.send_prompt_to_agent(agent_id, request.prompt)
        
        # Return response
        return {
            "response": response,
            "conversation_id": agent_id,
            "metadata": {
                "prompt_length": len(request.prompt),
                "response_length": len(response),
                "timestamp": str(datetime.datetime.now())
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/conversation/{conversation_id}", response_model=Dict[str, Any], summary="End a conversation")
async def end_conversation(conversation_id: str):
    """
    End a conversation with the Data Analyst Agent.
    
    This endpoint terminates the specified agent instance and
    cleans up associated resources.
    """
    try:
        # Check if agent exists
        if not agent_factory.agent_exists(conversation_id):
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Terminate agent
        agent_factory.terminate_agent(conversation_id)
        
        return {
            "success": True,
            "message": f"Conversation {conversation_id} ended successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
