import os
import sys
import base64
import secrets
from loguru import logger

# Configurar logger
logger.remove()
logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{function}</cyan> - <level>{message}</level>")

def test_encryption_in_tests():
    """
    Testa e corrige a funcionalidade de criptografia no ambiente de testes.
    """
    try:
        # Gerar uma chave de criptografia segura e fixa para testes
        logger.info("Gerando chave de criptografia fixa para testes...")
        
        # Usar uma chave fixa para testes para garantir consistência
        test_key_bytes = b"testkey12345testkey12345testkey12345"
        test_key = base64.urlsafe_b64encode(test_key_bytes).decode()
        
        # Definir a chave no ambiente
        os.environ["ENCRYPTION_KEY"] = test_key
        logger.info(f"ENCRYPTION_KEY definida no ambiente: {test_key}")
        
        # Salvar a chave em um arquivo .env para uso consistente
        with open(".env", "w") as f:
            f.write(f"ENCRYPTION_KEY={test_key}\n")
        logger.info("ENCRYPTION_KEY salva no arquivo .env")
        
        # Atualizar o script run_tests.sh para usar o arquivo .env
        with open("run_tests.sh", "r") as f:
            content = f.read()
        
        # Modificar o script para carregar o arquivo .env
        if "source .env" not in content:
            new_content = content.replace("#!/bin/bash", "#!/bin/bash\n\n# Carregar variáveis de ambiente do arquivo .env\nsource .env")
            with open("run_tests.sh", "w") as f:
                f.write(new_content)
            logger.info("Script run_tests.sh atualizado para carregar o arquivo .env")
        
        logger.info("Ambiente de criptografia configurado com sucesso para testes")
        return True
            
    except Exception as e:
        logger.error(f"Erro durante configuração do ambiente de criptografia: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("=== Configurando ambiente de criptografia para testes ===")
    result = test_encryption_in_tests()
    
    logger.info("\n=== Resumo da configuração ===")
    logger.info(f"Configuração do ambiente de criptografia: {'SUCESSO' if result else 'FALHA'}")
    
    if result:
        logger.info("O ambiente está pronto para executar os testes end-to-end")
    else:
        logger.error("Falha na configuração do ambiente. Verifique os logs acima para detalhes.")
