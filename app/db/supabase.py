"""
Supabase client module for database operations.

This module provides a client for interacting with Supabase,
including connection management and dependency injection.
"""

import os
from functools import lru_cache
from supabase import create_client, Client
from fastapi import Depends, HTTPException, status
from loguru import logger

# Obter credenciais do ambiente
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("SUPABASE_URL and SUPABASE_KEY environment variables must be set")
    raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")

@lru_cache()
def get_supabase_client() -> Client:
    """
    Cria e retorna um cliente Supabase.
    
    Utiliza cache para evitar múltiplas conexões desnecessárias.
    
    Returns:
        Client: Cliente Supabase configurado
    """
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return client
    except Exception as e:
        logger.error(f"Erro ao conectar ao Supabase: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao conectar ao Supabase: {str(e)}"
        )

def get_authenticated_user_id(supabase: Client = Depends(get_supabase_client)) -> str:
    """
    Obtém o ID do usuário autenticado.
    
    Args:
        supabase (Client): Cliente Supabase
        
    Returns:
        str: ID do usuário autenticado
        
    Raises:
        HTTPException: Se o usuário não estiver autenticado
    """
    try:
        user = supabase.auth.get_user()
        if not user or not user.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não autenticado"
            )
        return user.user.id
    except Exception as e:
        logger.error(f"Erro ao obter usuário autenticado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado"
        )
