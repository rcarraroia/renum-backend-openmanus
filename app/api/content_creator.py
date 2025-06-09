"""
API endpoints for Content Creator Agent.

This module defines the RESTful API endpoints for the Content Creator Agent,
allowing interaction with the agent's tools and capabilities.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel, Field

from app.agent.content_creator_prompt import CONTENT_CREATOR_SYSTEM_PROMPT
from app.process.factory import AgentProcessFactory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from fastapi import Depends, HTTPException, status
from pydantic import UUID4, BaseModel

from app.db.supabase import get_supabase_client
from app.logger import logger

# Create router
router = APIRouter(
    prefix="/api/agents/content-creator",
    tags=["content-creator"],
    responses={404: {"description": "Not found"}},
)


# Define request and response models
class EmailRequest(BaseModel):
    recipient: str = Field(..., description="Name or role of the email recipient")
    topic: str = Field(..., description="Main topic or subject of the email")
    key_points: List[str] = Field(
        ..., description="List of key points to include in the email body"
    )
    tone: Optional[str] = Field(
        "professional",
        description="Tone of the email (professional, friendly, formal, casual, urgent)",
    )
    include_signature: Optional[bool] = Field(
        True, description="Whether to include a signature"
    )
    sender_name: Optional[str] = Field(None, description="Name to use in the signature")


class SocialMediaRequest(BaseModel):
    theme: str = Field(..., description="Main theme or topic of the post")
    keywords: List[str] = Field(..., description="List of keywords to incorporate")
    platform: str = Field(
        ...,
        description="Target social media platform (twitter, linkedin, instagram, facebook)",
    )
    tone: Optional[str] = Field(
        "professional",
        description="Tone of the post (professional, friendly, formal, casual, promotional)",
    )
    include_hashtags: Optional[bool] = Field(
        True, description="Whether to include hashtags"
    )
    include_call_to_action: Optional[bool] = Field(
        True, description="Whether to include a call to action"
    )


class ContentStoreRequest(BaseModel):
    action: str = Field(
        ..., description="The action to perform (save, get, list, delete)"
    )
    content_type: str = Field(
        ..., description="The type of content (email, social_media_post, other)"
    )
    content_data: Optional[Dict[str, Any]] = Field(
        None, description="The content data to save (for save action)"
    )
    content_id: Optional[str] = Field(
        None,
        description="The ID of the content to retrieve/delete (for get/delete actions)",
    )


class PromptRequest(BaseModel):
    prompt: str = Field(..., description="User prompt for the Content Creator Agent")
    conversation_id: Optional[str] = Field(
        None, description="Conversation ID for continuing an existing conversation"
    )


class AgentResponse(BaseModel):
    response: str = Field(..., description="Response from the agent")
    conversation_id: str = Field(
        ..., description="Conversation ID for continuing the conversation"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata about the response"
    )


# Initialize agent factory
agent_factory = AgentProcessFactory()


@router.post("/email", response_model=Dict[str, Any], summary="Generate an email draft")
async def generate_email(request: EmailRequest, supabase=Depends(get_supabase_client)):
    """
    Generate an email draft based on the provided parameters.

    This endpoint uses the EmailGeneratorTool to create a structured email
    with appropriate formatting, salutations, and content organization.
    """
    try:
        user_id = supabase.auth.get_user().user.id
        project_id = get_current_project_id()
        validate_project_id(project_id, user_id)

        # Create agent instance if needed
        agent_id = "content_creator_email"
        if not agent_factory.agent_exists(agent_id):
            agent_factory.create_agent(agent_id, CONTENT_CREATOR_SYSTEM_PROMPT)

        # Prepare tool parameters
        tool_params = {
            "recipient": request.recipient,
            "topic": request.topic,
            "key_points": request.key_points,
            "tone": request.tone,
            "include_signature": request.include_signature,
            "sender_name": request.sender_name,
            "project_id": project_id,
        }

        # Create prompt for the agent
        prompt = f"""
        Please use the EmailGeneratorTool to create an email with the following parameters:
        - Recipient: {request.recipient}
        - Topic: {request.topic}
        - Key Points: {', '.join(request.key_points)}
        - Tone: {request.tone}
        - Include Signature: {request.include_signature}
        - Sender Name: {request.sender_name or '[Not provided]'}
        """

        # Send prompt to agent
        response = await agent_factory.send_prompt_to_agent(agent_id, prompt)

        # Extract email content from response
        # In a real implementation, this would parse the agent's response
        # For now, we'll directly call the tool
        from app.tool.content_creation.email_generator import EmailGeneratorTool

        email_tool = EmailGeneratorTool()
        email_result = await email_tool._arun(**tool_params)

        return email_result

    except Exception as e:
        logger.error(f"Error generating email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/social-media", response_model=Dict[str, Any], summary="Create a social media post"
)
async def create_social_media_post(request: SocialMediaRequest):
    """
    Create a social media post based on the provided parameters.

    This endpoint uses the SocialMediaPostTool to generate platform-specific
    content with appropriate formatting, hashtags, and structure.
    """
    try:
        # Create agent instance if needed
        agent_id = "content_creator_social"
        if not agent_factory.agent_exists(agent_id):
            agent_factory.create_agent(agent_id, CONTENT_CREATOR_SYSTEM_PROMPT)

        # Prepare tool parameters
        tool_params = {
            "theme": request.theme,
            "keywords": request.keywords,
            "platform": request.platform,
            "tone": request.tone,
            "include_hashtags": request.include_hashtags,
            "include_call_to_action": request.include_call_to_action,
        }

        # Create prompt for the agent
        prompt = f"""
        Please use the SocialMediaPostTool to create a post with the following parameters:
        - Theme: {request.theme}
        - Keywords: {', '.join(request.keywords)}
        - Platform: {request.platform}
        - Tone: {request.tone}
        - Include Hashtags: {request.include_hashtags}
        - Include Call to Action: {request.include_call_to_action}
        """

        # Send prompt to agent
        response = await agent_factory.send_prompt_to_agent(agent_id, prompt)

        # Extract post content from response
        # In a real implementation, this would parse the agent's response
        # For now, we'll directly call the tool
        from app.tool.content_creation.social_media_post import SocialMediaPostTool

        social_tool = SocialMediaPostTool()
        social_result = await social_tool._arun(**tool_params)

        return social_result

    except Exception as e:
        logger.error(f"Error creating social media post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/content-store", response_model=Dict[str, Any], summary="Manage stored content"
)
async def manage_content_store(request: ContentStoreRequest):
    """
    Perform operations on the content store.

    This endpoint uses the ContentStoreTool to save, retrieve, list,
    or delete content from the store.
    """
    try:
        # Create agent instance if needed
        agent_id = "content_creator_store"
        if not agent_factory.agent_exists(agent_id):
            agent_factory.create_agent(agent_id, CONTENT_CREATOR_SYSTEM_PROMPT)

        # Prepare tool parameters
        tool_params = {
            "action": request.action,
            "content_type": request.content_type,
            "content_data": request.content_data,
            "content_id": request.content_id,
        }

        # Create prompt for the agent
        prompt = f"""
        Please use the ContentStoreTool to perform the following operation:
        - Action: {request.action}
        - Content Type: {request.content_type}
        - Content ID: {request.content_id or '[Not provided]'}
        """

        # Send prompt to agent
        response = await agent_factory.send_prompt_to_agent(agent_id, prompt)

        # Extract result from response
        # In a real implementation, this would parse the agent's response
        # For now, we'll directly call the tool
        from app.tool.content_creation.content_store import ContentStoreTool

        store_tool = ContentStoreTool()
        store_result = await store_tool._arun(**tool_params)

        return store_result

    except Exception as e:
        logger.error(f"Error managing content store: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/prompt",
    response_model=AgentResponse,
    summary="Send a prompt to the Content Creator Agent",
)
async def send_prompt(request: PromptRequest):
    """
    Send a prompt to the Content Creator Agent and get a response.

    This endpoint allows free-form interaction with the agent, which will
    use its tools and capabilities to respond appropriately.
    """
    try:
        # Create or get agent instance
        agent_id = (
            request.conversation_id
            or "content_creator_" + str(hash(request.prompt))[:8]
        )
        if not agent_factory.agent_exists(agent_id):
            agent_factory.create_agent(agent_id, CONTENT_CREATOR_SYSTEM_PROMPT)

        # Send prompt to agent
        response = await agent_factory.send_prompt_to_agent(agent_id, request.prompt)

        # Return response
        return {
            "response": response,
            "conversation_id": agent_id,
            "metadata": {
                "prompt_length": len(request.prompt),
                "response_length": len(response),
                "timestamp": str(datetime.datetime.now()),
            },
        }

    except Exception as e:
        logger.error(f"Error processing prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/conversation/{conversation_id}",
    response_model=Dict[str, Any],
    summary="End a conversation",
)
async def end_conversation(conversation_id: str):
    """
    End a conversation with the Content Creator Agent.

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
            "message": f"Conversation {conversation_id} ended successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
