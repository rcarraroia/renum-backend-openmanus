"""
Mecanismos de fallback e tratamento de erros para LLMs e serviços de embedding.

Este módulo implementa estratégias robustas para lidar com falhas em serviços
externos, garantindo resiliência e experiência consistente para os usuários.
"""

from typing import Dict, List, Any, Optional, Callable, Tuple
import time
import random
import functools
import os
import sys
from loguru import logger

# Configuração de tentativas e timeouts
DEFAULT_MAX_RETRIES = 3
DEFAULT_BASE_DELAY = 1.0  # segundos
DEFAULT_MAX_DELAY = 10.0  # segundos
DEFAULT_TIMEOUT = 30.0  # segundos

class FallbackStrategy:
    """Estratégia de fallback para serviços externos."""
    
    def __init__(self, config: Dict[str, Any] = {}):
        """
        Inicializa a estratégia de fallback.
        
        Args:
            config: Configuração da estratégia de fallback
        """
        self.config = config
        self.max_retries = config.get("max_retries", DEFAULT_MAX_RETRIES)
        self.base_delay = config.get("base_delay", DEFAULT_BASE_DELAY)
        self.max_delay = config.get("max_delay", DEFAULT_MAX_DELAY)
        self.jitter = config.get("jitter", True)
    
    def execute_with_fallback(self, primary_func: Callable, fallback_func: Optional[Callable] = None, *args, **kwargs) -> Any:
        """
        Executa uma função com retry e fallback.
        
        Args:
            primary_func: Função primária a ser executada
            fallback_func: Função de fallback em caso de falha
            *args, **kwargs: Argumentos para as funções
            
        Returns:
            Resultado da função primária ou de fallback
        """
        last_exception = None
        
        # Tentativas com a função primária
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Tentativa {attempt + 1}/{self.max_retries} para função primária")
                return primary_func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logger.warning(f"Falha na tentativa {attempt + 1}/{self.max_retries}: {str(e)}")
                
                # Calcular delay com exponential backoff e jitter opcional
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                if self.jitter:
                    delay = delay * (0.5 + random.random())
                
                logger.debug(f"Aguardando {delay:.2f}s antes da próxima tentativa")
                time.sleep(delay)
        
        # Se todas as tentativas falharem e houver função de fallback
        if fallback_func:
            try:
                logger.info("Executando função de fallback")
                return fallback_func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Falha na função de fallback: {str(e)}")
                raise e
        
        # Se não houver fallback ou ele falhar
        logger.error(f"Todas as tentativas falharam sem fallback disponível: {str(last_exception)}")
        raise last_exception


def with_fallback(fallback_func: Optional[Callable] = None, max_retries: int = DEFAULT_MAX_RETRIES, 
                 base_delay: float = DEFAULT_BASE_DELAY, max_delay: float = DEFAULT_MAX_DELAY,
                 jitter: bool = True):
    """
    Decorador para adicionar retry e fallback a uma função.
    
    Args:
        fallback_func: Função de fallback em caso de falha
        max_retries: Número máximo de tentativas
        base_delay: Delay base entre tentativas (segundos)
        max_delay: Delay máximo entre tentativas (segundos)
        jitter: Se deve adicionar variação aleatória ao delay
        
    Returns:
        Função decorada com retry e fallback
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            strategy = FallbackStrategy({
                "max_retries": max_retries,
                "base_delay": base_delay,
                "max_delay": max_delay,
                "jitter": jitter
            })
            return strategy.execute_with_fallback(func, fallback_func, *args, **kwargs)
        return wrapper
    return decorator


class LLMFallbackManager:
    """Gerenciador de fallback para provedores de LLM."""
    
    def __init__(self, config: Dict[str, Any] = {}):
        """
        Inicializa o gerenciador de fallback para LLMs.
        
        Args:
            config: Configuração do gerenciador
        """
        self.config = config
        self.providers = config.get("providers", [])
        self.strategy = FallbackStrategy(config.get("fallback_strategy", {}))
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Gera texto usando LLMs com fallback entre provedores.
        
        Args:
            prompt: Prompt para geração de texto
            **kwargs: Argumentos adicionais para o provedor
            
        Returns:
            Texto gerado
        """
        if not self.providers:
            raise ValueError("Nenhum provedor LLM configurado")
        
        last_exception = None
        
        # Tentar cada provedor em sequência
        for provider_config in self.providers:
            try:
                # Importar dinamicamente o provedor
                from app.llm.providers import get_llm_provider
                provider = get_llm_provider(provider_config)
                
                # Usar a estratégia de fallback para este provedor
                return self.strategy.execute_with_fallback(
                    provider.generate_text,
                    None,  # Sem fallback interno, vamos para o próximo provedor
                    prompt,
                    **kwargs
                )
            except Exception as e:
                last_exception = e
                logger.warning(f"Falha no provedor {provider_config.get('provider')}: {str(e)}")
        
        # Se todos os provedores falharem
        logger.error(f"Todos os provedores LLM falharam: {str(last_exception)}")
        raise last_exception


class EmbeddingFallbackManager:
    """Gerenciador de fallback para provedores de embedding."""
    
    def __init__(self, config: Dict[str, Any] = {}):
        """
        Inicializa o gerenciador de fallback para embeddings.
        
        Args:
            config: Configuração do gerenciador
        """
        self.config = config
        self.providers = config.get("providers", [])
        self.strategy = FallbackStrategy(config.get("fallback_strategy", {}))
        self.dummy_dimension = config.get("dummy_dimension", 384)
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Obtém embedding com fallback entre provedores.
        
        Args:
            text: Texto para gerar embedding
            
        Returns:
            Vetor de embedding
        """
        if not self.providers:
            # Fallback para dummy provider se nenhum estiver configurado
            from app.knowledge.embedding_providers import DummyEmbeddingProvider
            dummy = DummyEmbeddingProvider({"dimension": self.dummy_dimension})
            return dummy.get_embedding(text)
        
        last_exception = None
        
        # Tentar cada provedor em sequência
        for provider_config in self.providers:
            try:
                # Importar dinamicamente o provedor
                from app.knowledge.embedding_providers import get_embedding_provider
                provider = get_embedding_provider(provider_config)
                
                # Usar a estratégia de fallback para este provedor
                return self.strategy.execute_with_fallback(
                    provider.get_embedding,
                    None,  # Sem fallback interno, vamos para o próximo provedor
                    text
                )
            except Exception as e:
                last_exception = e
                logger.warning(f"Falha no provedor de embedding {provider_config.get('provider')}: {str(e)}")
        
        # Se todos os provedores falharem, usar dummy como último recurso
        logger.warning(f"Todos os provedores de embedding falharam, usando dummy: {str(last_exception)}")
        from app.knowledge.embedding_providers import DummyEmbeddingProvider
        dummy = DummyEmbeddingProvider({"dimension": self.dummy_dimension})
        return dummy.get_embedding(text)


def update_factory_for_fallback():
    """
    Atualiza o factory de agentes para suportar fallback.
    
    Esta função modifica o factory para usar os gerenciadores de fallback
    ao criar instâncias de LLM e embedding providers.
    """
    try:
        # Importar o factory
        from app.process.factory import AgentFactory
        
        # Guardar as funções originais
        original_create_llm = AgentFactory._create_llm
        
        # Definir a nova função com suporte a fallback para LLM
        def _create_llm_with_fallback(self, config: Dict[str, Any] = {}) -> Any:
            """
            Cria um LLM com suporte a fallback.
            
            Args:
                config: Configuração do LLM
                
            Returns:
                Instância do LLM
            """
            # Se configuração de fallback estiver presente
            if "fallback_providers" in config:
                fallback_config = {
                    "providers": [config] + config.get("fallback_providers", []),
                    "fallback_strategy": config.get("fallback_strategy", {})
                }
                return LLMFallbackManager(fallback_config)
            
            # Caso contrário, usar a função original
            return original_create_llm(self, config)
        
        # Substituir a função no factory
        AgentFactory._create_llm = _create_llm_with_fallback
        
        # Atualizar também a integração de embeddings para usar fallback
        from app.knowledge.embedding_integration import integrate_embedding_provider
        
        # Definir nova função de integração com fallback
        def integrate_embedding_provider_with_fallback(knowledge_base, config: Dict[str, Any] = {}) -> bool:
            """
            Integra um provedor de embedding com fallback ao VectorKnowledgeBase.
            
            Args:
                knowledge_base: Instância de VectorKnowledgeBase
                config: Configuração do provedor de embedding
                
            Returns:
                Sucesso da integração
            """
            try:
                # Se configuração de fallback estiver presente
                if "fallback_providers" in config:
                    fallback_config = {
                        "providers": [config] + config.get("fallback_providers", []),
                        "fallback_strategy": config.get("fallback_strategy", {}),
                        "dummy_dimension": config.get("dimension", 384)
                    }
                    embedding_provider = EmbeddingFallbackManager(fallback_config)
                else:
                    # Usar o provedor normal
                    from app.knowledge.embedding_providers import get_embedding_provider
                    embedding_provider = get_embedding_provider(config)
                
                # Configurar o provedor no knowledge base
                knowledge_base.set_embedding_provider(embedding_provider)
                
                logger.info(f"Provedor de embedding {config.get('provider', 'dummy')} integrado com sucesso (com fallback)")
                return True
            except Exception as e:
                logger.error(f"Erro ao integrar provedor de embedding: {str(e)}")
                return False
        
        # Substituir a função de integração
        import app.knowledge.embedding_integration
        app.knowledge.embedding_integration.integrate_embedding_provider = integrate_embedding_provider_with_fallback
        
        logger.info("Factory de agentes atualizado para suportar fallback")
        return True
    except Exception as e:
        logger.error(f"Erro ao atualizar factory para fallback: {str(e)}")
        return False


if __name__ == "__main__":
    # Configurar logger
    logger.remove()
    logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{function}</cyan> - <level>{message}</level>")
    
    # Testar fallback
    logger.info("Testando mecanismos de fallback...")
    
    # Exemplo de função com fallback
    @with_fallback(fallback_func=lambda x: f"Fallback para {x}", max_retries=2)
    def test_function(text):
        if random.random() < 0.8:  # 80% de chance de falhar
            raise Exception("Erro simulado")
        return f"Sucesso: {text}"
    
    # Testar função com fallback
    try:
        result = test_function("teste")
        logger.info(f"Resultado: {result}")
    except Exception as e:
        logger.error(f"Erro final: {str(e)}")
    
    # Atualizar factory para fallback
    success = update_factory_for_fallback()
    logger.info(f"Atualização do factory para fallback: {'sucesso' if success else 'falha'}")
