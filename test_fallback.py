#!/usr/bin/env python3
"""
Script para testar os mecanismos de fallback sem dependência do Supabase.
"""

import os
import sys
import random
from loguru import logger

# Configurar logger
logger.remove()
logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{function}</cyan> - <level>{message}</level>")

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar mecanismos de fallback
from app.utils.fallback import with_fallback, FallbackStrategy, LLMFallbackManager, EmbeddingFallbackManager

def test_decorator_fallback():
    """Testa o decorador with_fallback."""
    logger.info("Testando decorador with_fallback...")
    
    # Função que falha aleatoriamente
    @with_fallback(fallback_func=lambda x: f"Fallback para {x}", max_retries=2)
    def test_function(text):
        if random.random() < 0.8:  # 80% de chance de falhar
            raise Exception("Erro simulado")
        return f"Sucesso: {text}"
    
    # Testar várias vezes para garantir que o fallback funcione
    results = []
    for i in range(5):
        try:
            result = test_function(f"teste_{i}")
            results.append(result)
        except Exception as e:
            results.append(f"Erro: {str(e)}")
    
    logger.info(f"Resultados do decorador: {results}")
    return "Fallback" in str(results)  # Verifica se o fallback foi acionado

def test_llm_fallback():
    """Testa o fallback entre provedores de LLM."""
    logger.info("Testando fallback entre provedores de LLM...")
    
    # Criar provedores simulados
    class MockLLMProvider:
        def __init__(self, name, fail_rate=0.0):
            self.name = name
            self.fail_rate = fail_rate
        
        def generate_text(self, prompt):
            if random.random() < self.fail_rate:
                raise Exception(f"Erro simulado no provedor {self.name}")
            return f"Resposta do provedor {self.name}: {prompt}"
    
    # Configurar gerenciador de fallback
    providers = [
        {"provider": "mock1", "mock_provider": MockLLMProvider("mock1", 0.9)},  # Alta taxa de falha
        {"provider": "mock2", "mock_provider": MockLLMProvider("mock2", 0.5)},  # Taxa média de falha
        {"provider": "mock3", "mock_provider": MockLLMProvider("mock3", 0.1)}   # Baixa taxa de falha
    ]
    
    # Substituir get_llm_provider para usar os mocks
    def mock_get_llm_provider(config):
        return config.get("mock_provider")
    
    # Salvar função original
    import app.llm.providers
    original_get_llm_provider = getattr(app.llm.providers, "get_llm_provider", None)
    
    try:
        # Substituir temporariamente
        app.llm.providers.get_llm_provider = mock_get_llm_provider
        
        # Criar gerenciador de fallback
        manager = LLMFallbackManager({"providers": providers})
        
        # Testar várias vezes
        results = []
        for i in range(5):
            try:
                result = manager.generate_text(f"prompt_{i}")
                results.append(result)
            except Exception as e:
                results.append(f"Erro final: {str(e)}")
        
        logger.info(f"Resultados do LLM fallback: {results}")
        
        # Verificar se pelo menos um teste teve sucesso
        success = any("Resposta do provedor" in str(result) for result in results)
        return success
    finally:
        # Restaurar função original
        if original_get_llm_provider:
            app.llm.providers.get_llm_provider = original_get_llm_provider

def test_embedding_fallback():
    """Testa o fallback entre provedores de embedding."""
    logger.info("Testando fallback entre provedores de embedding...")
    
    # Criar provedores simulados
    class MockEmbeddingProvider:
        def __init__(self, name, dimension=384, fail_rate=0.0):
            self.name = name
            self.dimension = dimension
            self.fail_rate = fail_rate
        
        def get_embedding(self, text):
            if random.random() < self.fail_rate:
                raise Exception(f"Erro simulado no provedor de embedding {self.name}")
            # Gerar embedding aleatório
            return [random.random() for _ in range(self.dimension)]
    
    # Configurar gerenciador de fallback
    providers = [
        {"provider": "mock1", "mock_provider": MockEmbeddingProvider("mock1", 384, 0.9)},  # Alta taxa de falha
        {"provider": "mock2", "mock_provider": MockEmbeddingProvider("mock2", 384, 0.5)},  # Taxa média de falha
        {"provider": "mock3", "mock_provider": MockEmbeddingProvider("mock3", 384, 0.1)}   # Baixa taxa de falha
    ]
    
    # Substituir get_embedding_provider para usar os mocks
    def mock_get_embedding_provider(config):
        return config.get("mock_provider")
    
    # Salvar função original
    import app.knowledge.embedding_providers
    original_get_embedding_provider = getattr(app.knowledge.embedding_providers, "get_embedding_provider", None)
    
    try:
        # Substituir temporariamente
        app.knowledge.embedding_providers.get_embedding_provider = mock_get_embedding_provider
        
        # Criar gerenciador de fallback
        manager = EmbeddingFallbackManager({"providers": providers, "dummy_dimension": 384})
        
        # Testar várias vezes
        results = []
        for i in range(5):
            try:
                embedding = manager.get_embedding(f"texto_{i}")
                # Verificar se é um embedding válido
                is_valid = isinstance(embedding, list) and len(embedding) == 384
                results.append(is_valid)
            except Exception as e:
                results.append(f"Erro final: {str(e)}")
        
        logger.info(f"Resultados do embedding fallback: {results}")
        
        # Verificar se todos os testes tiveram sucesso (sempre deve ter fallback para dummy)
        success = all(result is True for result in results)
        return success
    finally:
        # Restaurar função original
        if original_get_embedding_provider:
            app.knowledge.embedding_providers.get_embedding_provider = original_get_embedding_provider

if __name__ == "__main__":
    logger.info("Iniciando testes de fallback...")
    
    # Executar testes
    decorator_success = test_decorator_fallback()
    llm_success = test_llm_fallback()
    embedding_success = test_embedding_fallback()
    
    # Exibir resultados
    logger.info("\n=== Resumo dos testes de fallback ===")
    logger.info(f"Decorador with_fallback: {'PASSOU' if decorator_success else 'FALHOU'}")
    logger.info(f"Fallback entre provedores LLM: {'PASSOU' if llm_success else 'FALHOU'}")
    logger.info(f"Fallback entre provedores de embedding: {'PASSOU' if embedding_success else 'FALHOU'}")
    
    # Resultado final
    all_passed = decorator_success and llm_success and embedding_success
    logger.info(f"\nResultado final: {'TODOS OS TESTES PASSARAM' if all_passed else 'ALGUNS TESTES FALHARAM'}")
    
    sys.exit(0 if all_passed else 1)
