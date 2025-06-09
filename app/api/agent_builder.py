"""
API endpoints for Agent Builder CRUD operations.

This module provides RESTful API endpoints for managing agents, tools,
agent-tool associations, and credentials in the Renum Agent Builder.
"""

import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4, BaseModel

from app.db.supabase import get_supabase_client
from app.logger import logger
from app.utils.crypto import decrypt_api_key, encrypt_api_key

# Router para o Agent Builder
router = APIRouter(prefix="/agent-builder", tags=["agent-builder"])

# ==================== Modelos Pydantic ====================

# Modelos para Agents
from pydantic import UUID4, BaseModel


class AgentBase(BaseModel):
    project_id: UUID4
    name: str
    description: Optional[str] = None
    system_prompt: str
    llm_config: Dict[str, Any] = {}
    memory_config: Dict[str, Any] = {}
    knowledge_base_config: Dict[str, Any] = {}
    status: str = "draft"  # draft, active, inactive


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    llm_config: Optional[Dict[str, Any]] = None
    memory_config: Optional[Dict[str, Any]] = None
    knowledge_base_config: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class Agent(AgentBase):
    id: UUID4
    created_by: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Modelos para Tools
class ToolBase(BaseModel):
    project_id: UUID4
    name: str
    description: Optional[str] = None
    backend_tool_class_name: str
    parameters_schema: Dict[str, Any] = {}
    category: Optional[str] = None
    requires_credentials: bool = False
    credential_provider: Optional[str] = None


class ToolCreate(ToolBase):
    pass


class ToolUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    backend_tool_class_name: Optional[str] = None
    parameters_schema: Optional[Dict[str, Any]] = None
    category: Optional[str] = None
    requires_credentials: Optional[bool] = None
    credential_provider: Optional[str] = None


class Tool(ToolBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Modelos para Agent-Tool Associations
class AgentToolBase(BaseModel):
    agent_id: UUID4
    tool_id: UUID4
    tool_configuration: Dict[str, Any] = {}
    enabled: bool = True


class AgentToolCreate(AgentToolBase):
    pass


class AgentToolUpdate(BaseModel):
    tool_configuration: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None


class AgentTool(AgentToolBase):
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Modelos para Credentials
class CredentialBase(BaseModel):
    project_id: UUID4
    provider: str
    api_key: str  # Não criptografada na entrada
    name: Optional[str] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = {}


class CredentialCreate(CredentialBase):
    pass


class CredentialUpdate(BaseModel):
    api_key: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Credential(BaseModel):
    id: UUID4
    user_id: UUID4
    provider: str
    name: Optional[str] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# ==================== Endpoints para Agents ====================


@router.post("/agents", response_model=Agent, status_code=status.HTTP_201_CREATED)
async def create_agent(agent: AgentCreate, supabase=Depends(get_supabase_client)):
    """
    Cria um novo agente.
    """
    try:
        # Obter o ID do usuário autenticado
        user_id = supabase.auth.get_user().user.id
        project_id = agent.project_id

        # Validar project_id
        validate_project_id(project_id, user_id)

        # Preparar dados para inserção
        agent_data = agent.dict()
        agent_data["created_by"] = user_id

        # Inserir no Supabase
        response = supabase.table("agents").insert(agent_data).execute()

        if len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Falha ao criar agente",
            )

        return response.data[0]
    except Exception as e:
        logger.error(f"Erro ao criar agente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar agente: {str(e)}",
        )


@router.get("/agents", response_model=List[Agent])
async def list_agents(supabase=Depends(get_supabase_client)):
    """
    Lista todos os agentes do usuário atual.
    """
    try:
        user_id = supabase.auth.get_user().user.id
        project_id = get_current_project_id()

        response = (
            supabase.table("agents").select("*").eq("project_id", project_id).execute()
        )
        return response.data
    except Exception as e:
        logger.error(f"Erro ao listar agentes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar agentes: {str(e)}",
        )


@router.get("/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: UUID4, supabase=Depends(get_supabase_client)):
    """
    Obtém um agente específico pelo ID.
    """
    try:
        project_id = get_current_project_id()
        response = (
            supabase.table("agents")
            .select("*")
            .eq("id", str(agent_id))
            .eq("project_id", project_id)
            .execute()
        )

        if len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agente com ID {agent_id} não encontrado",
            )

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter agente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter agente: {str(e)}",
        )


@router.patch("/agents/{agent_id}", response_model=Agent)
async def update_agent(
    agent_id: UUID4, agent: AgentUpdate, supabase=Depends(get_supabase_client)
):
    """
    Atualiza um agente existente.
    """
    try:
        project_id = get_current_project_id()
        # Verificar se o agente existe e pertence ao project_id
        get_response = (
            supabase.table("agents")
            .select("*")
            .eq("id", str(agent_id))
            .eq("project_id", project_id)
            .execute()
        )

        if len(get_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agente com ID {agent_id} não encontrado",
            )

        # Impedir alteração do project_id
        if agent.project_id is not None and agent.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Alteração do project_id não é permitida",
            )

        # Filtrar campos não nulos para atualização
        update_data = {
            k: v for k, v in agent.dict().items() if v is not None and k != "project_id"
        }

        # Atualizar no Supabase
        response = (
            supabase.table("agents")
            .update(update_data)
            .eq("id", str(agent_id))
            .eq("project_id", project_id)
            .execute()
        )

        if len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Falha ao atualizar agente",
            )

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar agente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar agente: {str(e)}",
        )


@router.delete("/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: UUID4, supabase=Depends(get_supabase_client)):
    """
    Remove um agente.
    """
    try:
        # Verificar se o agente existe
        get_response = (
            supabase.table("agents").select("*").eq("id", str(agent_id)).execute()
        )

        if len(get_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agente com ID {agent_id} não encontrado",
            )

        # Remover do Supabase
        supabase.table("agents").delete().eq("id", str(agent_id)).execute()

        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao remover agente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover agente: {str(e)}",
        )


# ==================== Endpoints para Tools ====================


@router.post("/tools", response_model=Tool, status_code=status.HTTP_201_CREATED)
async def create_tool(tool: ToolCreate, supabase=Depends(get_supabase_client)):
    """
    Cria uma nova ferramenta.
    """
    try:
        # Preparar dados para inserção
        tool_data = tool.dict()

        # Inserir no Supabase
        response = supabase.table("tools").insert(tool_data).execute()

        if len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Falha ao criar ferramenta",
            )

        return response.data[0]
    except Exception as e:
        logger.error(f"Erro ao criar ferramenta: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar ferramenta: {str(e)}",
        )


@router.get("/tools", response_model=List[Tool])
async def list_tools(
    category: Optional[str] = None, supabase=Depends(get_supabase_client)
):
    """
    Lista todas as ferramentas disponíveis, opcionalmente filtradas por categoria.
    """
    try:
        query = supabase.table("tools").select("*")

        if category:
            query = query.eq("category", category)

        response = query.execute()
        return response.data
    except Exception as e:
        logger.error(f"Erro ao listar ferramentas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar ferramentas: {str(e)}",
        )


@router.get("/tools/{tool_id}", response_model=Tool)
async def get_tool(tool_id: UUID4, supabase=Depends(get_supabase_client)):
    """
    Obtém uma ferramenta específica pelo ID.
    """
    try:
        response = supabase.table("tools").select("*").eq("id", str(tool_id)).execute()

        if len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ferramenta com ID {tool_id} não encontrada",
            )

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter ferramenta: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter ferramenta: {str(e)}",
        )


@router.patch("/tools/{tool_id}", response_model=Tool)
async def update_tool(
    tool_id: UUID4, tool: ToolUpdate, supabase=Depends(get_supabase_client)
):
    """
    Atualiza uma ferramenta existente.
    """
    try:
        # Verificar se a ferramenta existe
        get_response = (
            supabase.table("tools").select("*").eq("id", str(tool_id)).execute()
        )

        if len(get_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ferramenta com ID {tool_id} não encontrada",
            )

        # Filtrar campos não nulos para atualização
        update_data = {k: v for k, v in tool.dict().items() if v is not None}

        # Atualizar no Supabase
        response = (
            supabase.table("tools").update(update_data).eq("id", str(tool_id)).execute()
        )

        if len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Falha ao atualizar ferramenta",
            )

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar ferramenta: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar ferramenta: {str(e)}",
        )


@router.delete("/tools/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool(tool_id: UUID4, supabase=Depends(get_supabase_client)):
    """
    Remove uma ferramenta.
    """
    try:
        # Verificar se a ferramenta existe
        get_response = (
            supabase.table("tools").select("*").eq("id", str(tool_id)).execute()
        )

        if len(get_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ferramenta com ID {tool_id} não encontrada",
            )

        # Remover do Supabase
        supabase.table("tools").delete().eq("id", str(tool_id)).execute()

        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao remover ferramenta: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover ferramenta: {str(e)}",
        )


# ==================== Endpoints para Agent-Tool Associations ====================


@router.post(
    "/agent-tools", response_model=AgentTool, status_code=status.HTTP_201_CREATED
)
async def create_agent_tool(
    agent_tool: AgentToolCreate, supabase=Depends(get_supabase_client)
):
    """
    Associa uma ferramenta a um agente.
    """
    try:
        # Verificar se o agente existe
        agent_response = (
            supabase.table("agents")
            .select("*")
            .eq("id", str(agent_tool.agent_id))
            .execute()
        )

        if len(agent_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agente com ID {agent_tool.agent_id} não encontrado",
            )

        # Verificar se a ferramenta existe
        tool_response = (
            supabase.table("tools")
            .select("*")
            .eq("id", str(agent_tool.tool_id))
            .execute()
        )

        if len(tool_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ferramenta com ID {agent_tool.tool_id} não encontrada",
            )

        # Preparar dados para inserção
        agent_tool_data = agent_tool.dict()

        # Inserir no Supabase
        response = supabase.table("agent_tools").insert(agent_tool_data).execute()

        if len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Falha ao associar ferramenta ao agente",
            )

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao associar ferramenta ao agente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao associar ferramenta ao agente: {str(e)}",
        )


@router.get("/agent-tools", response_model=List[AgentTool])
async def list_agent_tools(
    agent_id: Optional[UUID4] = None, supabase=Depends(get_supabase_client)
):
    """
    Lista todas as associações entre agentes e ferramentas, opcionalmente filtradas por agente.
    """
    try:
        query = supabase.table("agent_tools").select("*")

        if agent_id:
            query = query.eq("agent_id", str(agent_id))

        response = query.execute()
        return response.data
    except Exception as e:
        logger.error(
            f"Erro ao listar associações entre agentes e ferramentas: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar associações entre agentes e ferramentas: {str(e)}",
        )


@router.get("/agent-tools/{agent_id}/{tool_id}", response_model=AgentTool)
async def get_agent_tool(
    agent_id: UUID4, tool_id: UUID4, supabase=Depends(get_supabase_client)
):
    """
    Obtém uma associação específica entre agente e ferramenta.
    """
    try:
        response = (
            supabase.table("agent_tools")
            .select("*")
            .eq("agent_id", str(agent_id))
            .eq("tool_id", str(tool_id))
            .execute()
        )

        if len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Associação entre agente {agent_id} e ferramenta {tool_id} não encontrada",
            )

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter associação entre agente e ferramenta: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter associação entre agente e ferramenta: {str(e)}",
        )


@router.patch("/agent-tools/{agent_id}/{tool_id}", response_model=AgentTool)
async def update_agent_tool(
    agent_id: UUID4,
    tool_id: UUID4,
    agent_tool: AgentToolUpdate,
    supabase=Depends(get_supabase_client),
):
    """
    Atualiza uma associação existente entre agente e ferramenta.
    """
    try:
        # Verificar se a associação existe
        get_response = (
            supabase.table("agent_tools")
            .select("*")
            .eq("agent_id", str(agent_id))
            .eq("tool_id", str(tool_id))
            .execute()
        )

        if len(get_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Associação entre agente {agent_id} e ferramenta {tool_id} não encontrada",
            )

        # Filtrar campos não nulos para atualização
        update_data = {k: v for k, v in agent_tool.dict().items() if v is not None}

        # Atualizar no Supabase
        response = (
            supabase.table("agent_tools")
            .update(update_data)
            .eq("agent_id", str(agent_id))
            .eq("tool_id", str(tool_id))
            .execute()
        )

        if len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Falha ao atualizar associação entre agente e ferramenta",
            )

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Erro ao atualizar associação entre agente e ferramenta: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar associação entre agente e ferramenta: {str(e)}",
        )


@router.delete(
    "/agent-tools/{agent_id}/{tool_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_agent_tool(
    agent_id: UUID4, tool_id: UUID4, supabase=Depends(get_supabase_client)
):
    """
    Remove uma associação entre agente e ferramenta.
    """
    try:
        # Verificar se a associação existe
        get_response = (
            supabase.table("agent_tools")
            .select("*")
            .eq("agent_id", str(agent_id))
            .eq("tool_id", str(tool_id))
            .execute()
        )

        if len(get_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Associação entre agente {agent_id} e ferramenta {tool_id} não encontrada",
            )

        # Remover do Supabase
        supabase.table("agent_tools").delete().eq("agent_id", str(agent_id)).eq(
            "tool_id", str(tool_id)
        ).execute()

        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao remover associação entre agente e ferramenta: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover associação entre agente e ferramenta: {str(e)}",
        )


# ==================== Endpoints para Credentials ====================


@router.post(
    "/credentials", response_model=Credential, status_code=status.HTTP_201_CREATED
)
async def create_credential(
    credential: CredentialCreate, supabase=Depends(get_supabase_client)
):
    """
    Cria uma nova credencial.
    """
    try:
        # Obter o ID do usuário autenticado
        user_id = supabase.auth.get_user().user.id

        # Criptografar a chave de API
        api_key_encrypted = encrypt_api_key(credential.api_key)

        # Preparar dados para inserção
        credential_data = credential.dict()
        credential_data["user_id"] = user_id
        credential_data["api_key_encrypted"] = api_key_encrypted

        # Remover a chave não criptografada
        del credential_data["api_key"]

        # Inserir no Supabase
        response = supabase.table("credentials").insert(credential_data).execute()

        if len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Falha ao criar credencial",
            )

        return response.data[0]
    except Exception as e:
        logger.error(f"Erro ao criar credencial: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar credencial: {str(e)}",
        )


@router.get("/credentials", response_model=List[Credential])
async def list_credentials(
    provider: Optional[str] = None, supabase=Depends(get_supabase_client)
):
    """
    Lista todas as credenciais do usuário atual, opcionalmente filtradas por provedor.
    """
    try:
        # Obter o ID do usuário autenticado
        user_id = supabase.auth.get_user().user.id

        query = supabase.table("credentials").select("*").eq("user_id", user_id)

        if provider:
            query = query.eq("provider", provider)

        response = query.execute()
        return response.data
    except Exception as e:
        logger.error(f"Erro ao listar credenciais: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar credenciais: {str(e)}",
        )


@router.get("/credentials/{credential_id}", response_model=Credential)
async def get_credential(credential_id: UUID4, supabase=Depends(get_supabase_client)):
    """
    Obtém uma credencial específica pelo ID.
    """
    try:
        # Obter o ID do usuário autenticado
        user_id = supabase.auth.get_user().user.id

        response = (
            supabase.table("credentials")
            .select("*")
            .eq("id", str(credential_id))
            .eq("user_id", user_id)
            .execute()
        )

        if len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Credencial com ID {credential_id} não encontrada",
            )

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter credencial: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter credencial: {str(e)}",
        )


@router.patch("/credentials/{credential_id}", response_model=Credential)
async def update_credential(
    credential_id: UUID4,
    credential: CredentialUpdate,
    supabase=Depends(get_supabase_client),
):
    """
    Atualiza uma credencial existente.
    """
    try:
        # Obter o ID do usuário autenticado
        user_id = supabase.auth.get_user().user.id

        # Verificar se a credencial existe e pertence ao usuário
        get_response = (
            supabase.table("credentials")
            .select("*")
            .eq("id", str(credential_id))
            .eq("user_id", user_id)
            .execute()
        )

        if len(get_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Credencial com ID {credential_id} não encontrada",
            )

        # Filtrar campos não nulos para atualização
        update_data = {k: v for k, v in credential.dict().items() if v is not None}

        # Se a chave de API foi fornecida, criptografá-la
        if "api_key" in update_data:
            update_data["api_key_encrypted"] = encrypt_api_key(update_data["api_key"])
            del update_data["api_key"]

        # Atualizar no Supabase
        response = (
            supabase.table("credentials")
            .update(update_data)
            .eq("id", str(credential_id))
            .eq("user_id", user_id)
            .execute()
        )

        if len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Falha ao atualizar credencial",
            )

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar credencial: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar credencial: {str(e)}",
        )


@router.delete("/credentials/{credential_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_credential(
    credential_id: UUID4, supabase=Depends(get_supabase_client)
):
    """
    Remove uma credencial.
    """
    try:
        # Obter o ID do usuário autenticado
        user_id = supabase.auth.get_user().user.id

        # Verificar se a credencial existe e pertence ao usuário
        get_response = (
            supabase.table("credentials")
            .select("*")
            .eq("id", str(credential_id))
            .eq("user_id", user_id)
            .execute()
        )

        if len(get_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Credencial com ID {credential_id} não encontrada",
            )

        # Remover do Supabase
        supabase.table("credentials").delete().eq("id", str(credential_id)).eq(
            "user_id", user_id
        ).execute()

        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao remover credencial: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover credencial: {str(e)}",
        )


# ==================== Endpoints para Operações Avançadas ====================


@router.get("/agents/{agent_id}/tools", response_model=List[Tool])
async def get_agent_tools(agent_id: UUID4, supabase=Depends(get_supabase_client)):
    """
    Obtém todas as ferramentas associadas a um agente específico.
    """
    try:
        # Verificar se o agente existe
        agent_response = (
            supabase.table("agents").select("*").eq("id", str(agent_id)).execute()
        )

        if len(agent_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agente com ID {agent_id} não encontrado",
            )

        # Obter as associações entre o agente e ferramentas
        agent_tools_response = (
            supabase.table("agent_tools")
            .select("tool_id")
            .eq("agent_id", str(agent_id))
            .execute()
        )

        if len(agent_tools_response.data) == 0:
            return []

        # Extrair os IDs das ferramentas
        tool_ids = [item["tool_id"] for item in agent_tools_response.data]

        # Obter as ferramentas
        tools = []
        for tool_id in tool_ids:
            tool_response = (
                supabase.table("tools").select("*").eq("id", tool_id).execute()
            )
            if len(tool_response.data) > 0:
                tools.append(tool_response.data[0])

        return tools
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter ferramentas do agente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter ferramentas do agente: {str(e)}",
        )


@router.post(
    "/agents/{agent_id}/tools/{tool_id}",
    response_model=AgentTool,
    status_code=status.HTTP_201_CREATED,
)
async def add_tool_to_agent(
    agent_id: UUID4,
    tool_id: UUID4,
    tool_configuration: Dict[str, Any] = {},
    supabase=Depends(get_supabase_client),
):
    """
    Adiciona uma ferramenta a um agente com configuração opcional.
    """
    try:
        # Verificar se o agente existe
        agent_response = (
            supabase.table("agents").select("*").eq("id", str(agent_id)).execute()
        )

        if len(agent_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agente com ID {agent_id} não encontrado",
            )

        # Verificar se a ferramenta existe
        tool_response = (
            supabase.table("tools").select("*").eq("id", str(tool_id)).execute()
        )

        if len(tool_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ferramenta com ID {tool_id} não encontrada",
            )

        # Verificar se a associação já existe
        existing_response = (
            supabase.table("agent_tools")
            .select("*")
            .eq("agent_id", str(agent_id))
            .eq("tool_id", str(tool_id))
            .execute()
        )

        if len(existing_response.data) > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ferramenta {tool_id} já está associada ao agente {agent_id}",
            )

        # Preparar dados para inserção
        agent_tool_data = {
            "agent_id": str(agent_id),
            "tool_id": str(tool_id),
            "tool_configuration": tool_configuration,
            "enabled": True,
        }

        # Inserir no Supabase
        response = supabase.table("agent_tools").insert(agent_tool_data).execute()

        if len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Falha ao adicionar ferramenta ao agente",
            )

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao adicionar ferramenta ao agente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao adicionar ferramenta ao agente: {str(e)}",
        )


@router.delete(
    "/agents/{agent_id}/tools/{tool_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_tool_from_agent(
    agent_id: UUID4, tool_id: UUID4, supabase=Depends(get_supabase_client)
):
    """
    Remove uma ferramenta de um agente.
    """
    try:
        # Verificar se a associação existe
        existing_response = (
            supabase.table("agent_tools")
            .select("*")
            .eq("agent_id", str(agent_id))
            .eq("tool_id", str(tool_id))
            .execute()
        )

        if len(existing_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ferramenta {tool_id} não está associada ao agente {agent_id}",
            )

        # Remover do Supabase
        supabase.table("agent_tools").delete().eq("agent_id", str(agent_id)).eq(
            "tool_id", str(tool_id)
        ).execute()

        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao remover ferramenta do agente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover ferramenta do agente: {str(e)}",
        )
