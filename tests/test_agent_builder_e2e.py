"""
Test script for validating the Agent Builder end-to-end.

This script tests the complete flow of creating, configuring,
and using agents through the Agent Builder infrastructure.
"""

import os
import sys
import json
import time
import uuid
import asyncio
from loguru import logger

# Configurar variáveis de ambiente diretamente no script
# Isso garante que as variáveis estejam disponíveis mesmo em ambientes sandboxed
os.environ["SUPABASE_URL"] = "https://wvplmbsfxsqfxupeucsd.supabase.co"
os.environ["SUPABASE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind2cGxtYnNmeHNxZnh1cGV1Y3NkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODI4NTk4NSwiZXhwIjoyMDYzODYxOTg1fQ.4HE3NrXVeMSCuzsTdwR9bgSA9UuSuD_tFPbwCmbhF2w"

# Garantir que a ENCRYPTION_KEY esteja definida
if "ENCRYPTION_KEY" not in os.environ:
    # Usar a mesma chave fixa definida em fix_encryption_env.py
    os.environ["ENCRYPTION_KEY"] = "dGVzdGtleTEyMzQ1dGVzdGtleTEyMzQ1dGVzdGtleTEyMzQ1"
    logger.info(f"ENCRYPTION_KEY definida no ambiente: {os.environ['ENCRYPTION_KEY']}")

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar módulos necessários
from app.db.supabase import get_supabase_client
from app.process.factory import get_agent_factory
from app.utils.crypto import encrypt_api_key, test_encryption
from app.llm.providers import get_llm_provider
from app.memory.memory import get_memory_manager
from app.knowledge.knowledge_base import get_knowledge_base

# ID do usuário de teste para uso nos testes
TEST_USER_ID = "5e033ee2-5552-4010-9cec-d8e428099e14"

def ensure_test_user_exists():
    """Garante que o usuário de teste exista na tabela users."""
    logger.info(f"Verificando/criando usuário de teste: {TEST_USER_ID}")
    
    try:
        supabase = get_supabase_client()
        
        # Verificar se o usuário já existe
        response = supabase.table("users").select("id").eq("id", TEST_USER_ID).execute()
        
        if response.data and len(response.data) > 0:
            logger.info("Usuário de teste já existe")
            return True
        
        # Criar usuário de teste se não existir
        user_data = {
            "id": TEST_USER_ID,
            "email": "test@renum.ai",
            "name": "Test User",
            "created_at": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        response = supabase.table("users").insert(user_data).execute()
        
        logger.info(f"Usuário de teste criado: {response}")
        return True
    except Exception as e:
        logger.error(f"Erro ao garantir usuário de teste: {str(e)}")
        return False

def test_supabase_connection():
    """Testa a conexão com o Supabase."""
    logger.info("Testando conexão com o Supabase...")
    
    try:
        supabase = get_supabase_client()
        response = supabase.table("agents").select("count").execute()
        
        logger.info(f"Conexão com o Supabase bem-sucedida: {response}")
        return True
    except Exception as e:
        logger.error(f"Erro ao conectar ao Supabase: {str(e)}")
        return False

def test_encryption():
    """Testa a funcionalidade de criptografia."""
    logger.info("Testando funcionalidade de criptografia...")
    
    try:
        # Verificar se a ENCRYPTION_KEY está definida
        encryption_key = os.environ.get("ENCRYPTION_KEY")
        logger.info(f"ENCRYPTION_KEY está definida: {encryption_key is not None}")
        
        # Testar diretamente a criptografia e descriptografia
        test_value = "test-api-key-12345"
        
        # Importar novamente para garantir que está usando a chave correta
        from app.utils.crypto import encrypt_api_key, decrypt_api_key
        
        encrypted = encrypt_api_key(test_value)
        logger.info(f"Valor criptografado: {encrypted}")
        
        decrypted = decrypt_api_key(encrypted)
        logger.info(f"Valor descriptografado: {decrypted}")
        
        if decrypted == test_value:
            logger.info("Teste de criptografia bem-sucedido")
            return True
        else:
            logger.error(f"Teste de criptografia falhou: valores não correspondem. Original: {test_value}, Descriptografado: {decrypted}")
            return False
    except Exception as e:
        logger.error(f"Erro ao testar criptografia: {str(e)}")
        return False

def test_llm_provider():
    """Testa a integração com provedores de LLM."""
    logger.info("Testando integração com provedores de LLM...")
    
    try:
        # Testar com provedor dummy (não requer API key)
        config = {
            "provider": "dummy",
            "model": "dummy-model",
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        provider = get_llm_provider(config)
        response = provider.generate_text("Hello, world!")
        
        logger.info(f"Resposta do provedor LLM: {response}")
        return True
    except Exception as e:
        logger.error(f"Erro ao testar provedor LLM: {str(e)}")
        return False

def test_memory_manager():
    """Testa o gerenciador de memória."""
    logger.info("Testando gerenciador de memória...")
    
    try:
        # Testar com memória simples
        config = {
            "type": "simple",
            "max_messages": 10,
            "max_tokens": 1000
        }
        
        memory = get_memory_manager(config)
        memory.add_system_message("You are a helpful assistant.")
        memory.add_user_message("Hello, how are you?")
        memory.add_assistant_message("I'm doing well, thank you for asking!")
        
        history = memory.get_conversation_history()
        
        logger.info(f"Histórico de conversa: {json.dumps(history, indent=2)}")
        return True
    except Exception as e:
        logger.error(f"Erro ao testar gerenciador de memória: {str(e)}")
        return False

def test_knowledge_base():
    """Testa a base de conhecimento."""
    logger.info("Testando base de conhecimento...")
    
    try:
        # Testar com base de conhecimento simples
        config = {
            "type": "simple",
            "enabled": True,
            "max_documents": 10,
            "max_context_length": 1000
        }
        
        kb = get_knowledge_base(config)
        
        # Adicionar documento de teste
        document = {
            "id": str(uuid.uuid4()),
            "title": "Test Document",
            "content": "This is a test document about artificial intelligence and machine learning.",
            "source_url": "https://example.com/test"
        }
        
        kb.add_document(document)
        
        # Testar enriquecimento de prompt
        prompt = "Tell me about artificial intelligence."
        enriched_prompt = kb.enrich_prompt(prompt)
        
        logger.info(f"Prompt original: {prompt}")
        logger.info(f"Prompt enriquecido: {enriched_prompt}")
        
        return True
    except Exception as e:
        logger.error(f"Erro ao testar base de conhecimento: {str(e)}")
        return False

async def test_agent_factory():
    """Testa o factory de agentes."""
    logger.info("Testando factory de agentes...")
    
    try:
        # Obter instância do factory
        factory = get_agent_factory()
        
        # Criar agente de teste no Supabase
        supabase = get_supabase_client()
        
        # Gerar ID único para o agente de teste
        agent_id = str(uuid.uuid4())
        
        # Configuração do agente de teste
        agent_config = {
            "id": agent_id,
            "name": "Test Agent",
            "description": "Agent for end-to-end testing",
            "status": "active",
            "created_by": TEST_USER_ID,  # Usar ID do usuário de teste
            "system_prompt": "You are a helpful assistant for testing purposes.",
            "llm_config": {
                "provider": "dummy",
                "model": "dummy-model",
                "temperature": 0.7,
                "max_tokens": 100
            },
            "memory_config": {
                "type": "simple",
                "max_messages": 10,
                "max_tokens": 1000
            },
            "knowledge_base_config": {
                "type": "simple",
                "enabled": False
            }
        }
        
        # Inserir agente no Supabase
        logger.info(f"Criando agente de teste no Supabase: {agent_id}")
        response = supabase.table("agents").insert(agent_config).execute()
        
        # Criar ferramenta de teste no Supabase com nome único
        tool_id = str(uuid.uuid4())
        unique_tool_name = f"echo_{str(uuid.uuid4())[:8]}"  # Nome único para evitar duplicidade
        
        tool_config = {
            "id": tool_id,
            "name": unique_tool_name,  # Nome único
            "description": "Echoes the input text",
            "backend_tool_class_name": "EchoTool",
            "parameters_schema": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to echo"
                    }
                },
                "required": ["text"]
            },
            "requires_credentials": False,
            "credential_provider": None
        }
        
        logger.info(f"Criando ferramenta de teste no Supabase: {tool_id} com nome único: {unique_tool_name}")
        response = supabase.table("tools").insert(tool_config).execute()
        
        # Associar ferramenta ao agente
        agent_tool_id = str(uuid.uuid4())
        
        agent_tool_config = {
            "id": agent_tool_id,
            "agent_id": agent_id,
            "tool_id": tool_id,
            "enabled": True,
            "tool_configuration": {}
        }
        
        logger.info(f"Associando ferramenta ao agente no Supabase: {agent_tool_id}")
        response = supabase.table("agent_tools").insert(agent_tool_config).execute()
        
        # Testar criação de agente
        logger.info(f"Criando agente via factory: {agent_id}")
        process_id = await factory.create_agent(agent_id)
        
        logger.info(f"Agente criado com process_id: {process_id}")
        
        # Testar envio de prompt
        prompt = "Hello, world!"
        logger.info(f"Enviando prompt para o agente: {prompt}")
        
        response = await factory.send_prompt(process_id, prompt)
        
        logger.info(f"Resposta do agente: {json.dumps(response, indent=2)}")
        
        # Testar terminação do agente
        logger.info(f"Terminando agente: {process_id}")
        result = factory.terminate_agent(process_id)
        
        logger.info(f"Agente terminado: {result}")
        
        # Limpar dados de teste
        logger.info("Limpando dados de teste...")
        
        supabase.table("agent_tools").delete().eq("id", agent_tool_id).execute()
        supabase.table("tools").delete().eq("id", tool_id).execute()
        supabase.table("agents").delete().eq("id", agent_id).execute()
        
        return True
    except Exception as e:
        logger.error(f"Erro ao testar factory de agentes: {str(e)}")
        return False

async def run_all_tests():
    """Executa todos os testes end-to-end."""
    logger.info("Iniciando testes end-to-end do Agent Builder...")
    
    # Garantir que o usuário de teste exista
    ensure_test_user_exists()
    
    tests = [
        ("Conexão com o Supabase", test_supabase_connection),
        ("Funcionalidade de criptografia", test_encryption),
        ("Integração com provedores de LLM", test_llm_provider),
        ("Gerenciador de memória", test_memory_manager),
        ("Base de conhecimento", test_knowledge_base),
        ("Factory de agentes", test_agent_factory)
    ]
    
    results = {}
    all_passed = True
    
    for name, test_func in tests:
        logger.info(f"\n{'=' * 50}\nExecutando teste: {name}\n{'=' * 50}")
        
        try:
            # Verificar se a função é assíncrona
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
                
            results[name] = "PASSOU" if result else "FALHOU"
            
            if not result:
                all_passed = False
        except Exception as e:
            logger.error(f"Erro ao executar teste {name}: {str(e)}")
            results[name] = f"ERRO: {str(e)}"
            all_passed = False
    
    # Exibir resumo dos resultados
    logger.info("\n\n" + "=" * 50)
    logger.info("RESUMO DOS TESTES")
    logger.info("=" * 50)
    
    for name, result in results.items():
        logger.info(f"{name}: {result}")
    
    logger.info("\nResultado final: " + ("TODOS OS TESTES PASSARAM" if all_passed else "ALGUNS TESTES FALHARAM"))
    
    return all_passed

if __name__ == "__main__":
    # Verificar se as variáveis de ambiente estão configuradas
    logger.info(f"SUPABASE_URL configurada: {os.environ.get('SUPABASE_URL') is not None}")
    logger.info(f"SUPABASE_KEY configurada: {os.environ.get('SUPABASE_KEY') is not None}")
    logger.info(f"ENCRYPTION_KEY configurada: {os.environ.get('ENCRYPTION_KEY') is not None}")
    
    # Configurar logger
    logger.remove()
    logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    
    # Executar testes usando asyncio
    success = asyncio.run(run_all_tests())
    
    # Sair com código apropriado
    sys.exit(0 if success else 1)
