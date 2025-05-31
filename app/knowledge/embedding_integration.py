"""
Integração do VectorKnowledgeBase com provedores de embedding.

Este módulo atualiza o VectorKnowledgeBase para utilizar os provedores
de embedding implementados, permitindo busca semântica avançada.
"""

from typing import Dict, List, Any, Optional
import os
import sys
from loguru import logger

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar módulos necessários
from app.knowledge.knowledge_base import VectorKnowledgeBase
from app.knowledge.embedding_providers import get_embedding_provider

def integrate_embedding_provider(knowledge_base: VectorKnowledgeBase, config: Dict[str, Any] = {}) -> bool:
    """
    Integra um provedor de embedding ao VectorKnowledgeBase.
    
    Args:
        knowledge_base: Instância de VectorKnowledgeBase
        config: Configuração do provedor de embedding
        
    Returns:
        Sucesso da integração
    """
    try:
        # Obter provedor de embedding
        embedding_provider = get_embedding_provider(config)
        
        # Configurar o provedor no knowledge base
        knowledge_base.set_embedding_provider(embedding_provider)
        
        logger.info(f"Provedor de embedding {config.get('provider', 'dummy')} integrado com sucesso")
        return True
    except Exception as e:
        logger.error(f"Erro ao integrar provedor de embedding: {str(e)}")
        return False

def update_factory_for_embeddings():
    """
    Atualiza o factory de agentes para suportar embeddings.
    
    Esta função modifica o factory para configurar automaticamente
    o provedor de embedding ao criar um VectorKnowledgeBase.
    """
    try:
        # Importar o factory
        from app.process.factory import AgentFactory
        
        # Guardar a função original
        original_create_knowledge_base = AgentFactory._create_knowledge_base
        
        # Definir a nova função com suporte a embeddings
        def _create_knowledge_base_with_embeddings(self, config: Dict[str, Any] = {}) -> Any:
            """
            Cria uma base de conhecimento com suporte a embeddings.
            
            Args:
                config: Configuração da base de conhecimento
                
            Returns:
                Instância da base de conhecimento
            """
            # Chamar a função original
            kb = original_create_knowledge_base(self, config)
            
            # Se for um VectorKnowledgeBase, configurar o provedor de embedding
            if isinstance(kb, VectorKnowledgeBase):
                # Obter configuração de embedding do agente ou usar padrão
                embedding_config = config.get("embedding_config", {
                    "provider": "dummy",
                    "dimension": 384
                })
                
                # Integrar provedor de embedding
                integrate_embedding_provider(kb, embedding_config)
            
            return kb
        
        # Substituir a função no factory
        AgentFactory._create_knowledge_base = _create_knowledge_base_with_embeddings
        
        logger.info("Factory de agentes atualizado para suportar embeddings")
        return True
    except Exception as e:
        logger.error(f"Erro ao atualizar factory para embeddings: {str(e)}")
        return False

if __name__ == "__main__":
    # Configurar logger
    logger.remove()
    logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{function}</cyan> - <level>{message}</level>")
    
    # Testar integração
    logger.info("Testando integração de embeddings...")
    
    # Criar VectorKnowledgeBase
    from app.knowledge.knowledge_base import VectorKnowledgeBase
    kb = VectorKnowledgeBase({"enabled": True, "type": "vector"})
    
    # Integrar provedor de embedding
    success = integrate_embedding_provider(kb, {"provider": "dummy", "dimension": 384})
    
    if success:
        logger.info("Integração de embeddings bem-sucedida")
    else:
        logger.error("Falha na integração de embeddings")
