import os
import sys
import uuid
from loguru import logger

# Configurar variáveis de ambiente
os.environ["SUPABASE_URL"] = "https://wvplmbsfxsqfxupeucsd.supabase.co"
os.environ["SUPABASE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind2cGxtYnNmeHNxZnh1cGV1Y3NkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODI4NTk4NSwiZXhwIjoyMDYzODYxOTg1fQ.4HE3NrXVeMSCuzsTdwR9bgSA9UuSuD_tFPbwCmbhF2w"

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar módulos necessários
from app.db.supabase import get_supabase_client

# Configurar logger
logger.remove()
logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{function}</cyan> - <level>{message}</level>")

def fix_tools_duplication():
    """
    Corrige o problema de duplicidade na tabela tools.
    """
    try:
        client = get_supabase_client()
        logger.info("Conexão com o Supabase estabelecida")
        
        # Verificar se a ferramenta 'echo' já existe
        response = client.table("tools").select("*").eq("name", "echo").execute()
        
        if response.data and len(response.data) > 0:
            logger.info(f"Ferramenta 'echo' já existe: {response.data}")
            
            # Modificar o script de teste para usar um nome único
            test_file_path = "tests/test_agent_builder_e2e.py"
            
            if os.path.exists(test_file_path):
                with open(test_file_path, "r") as f:
                    content = f.read()
                
                # Substituir o nome fixo 'echo' por um nome dinâmico com UUID
                if "name=\"echo\"" in content:
                    modified_content = content.replace(
                        "name=\"echo\"", 
                        "name=f\"echo_{str(uuid.uuid4())[:8]}\""
                    )
                    
                    with open(test_file_path, "w") as f:
                        f.write(modified_content)
                    
                    logger.info("Teste modificado para usar nome dinâmico para a ferramenta")
                else:
                    logger.warning("Não foi possível encontrar 'name=\"echo\"' no arquivo de teste")
            else:
                logger.error(f"Arquivo de teste não encontrado: {test_file_path}")
        else:
            logger.info("Ferramenta 'echo' não existe, não é necessário modificar o teste")
        
        return True
            
    except Exception as e:
        logger.error(f"Erro ao corrigir duplicidade de tools: {e}")
        return False

if __name__ == "__main__":
    logger.info("=== Corrigindo duplicidade na tabela tools ===")
    result = fix_tools_duplication()
    
    logger.info("\n=== Resumo da correção ===")
    logger.info(f"Correção de duplicidade: {'SUCESSO' if result else 'FALHA'}")
