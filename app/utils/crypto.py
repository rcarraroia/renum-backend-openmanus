"""
Utility module for cryptographic operations.

This module provides functions for securely encrypting and decrypting
sensitive information like API keys.
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from loguru import logger

# Obter chave de criptografia do ambiente ou gerar uma
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY")

if not ENCRYPTION_KEY:
    # Gerar uma chave derivada de uma senha padrão (apenas para desenvolvimento)
    # Em produção, a chave deve ser definida como variável de ambiente
    logger.warning("ENCRYPTION_KEY not set, using default key (NOT SECURE FOR PRODUCTION)")
    password = b"renum-default-password"  # Apenas para desenvolvimento
    salt = b"renum-salt"  # Apenas para desenvolvimento
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    
    ENCRYPTION_KEY = base64.urlsafe_b64encode(kdf.derive(password))
else:
    # Usar a chave fornecida
    ENCRYPTION_KEY = ENCRYPTION_KEY.encode()

# Criar instância Fernet para criptografia
fernet = Fernet(ENCRYPTION_KEY)

def encrypt_api_key(api_key: str) -> str:
    """
    Criptografa uma chave de API.
    
    Args:
        api_key: Chave de API em texto plano
        
    Returns:
        Chave de API criptografada em formato base64
    """
    try:
        encrypted_data = fernet.encrypt(api_key.encode())
        return encrypted_data.decode()
    except Exception as e:
        logger.error(f"Erro ao criptografar chave de API: {str(e)}")
        raise ValueError(f"Falha ao criptografar chave de API: {str(e)}")

def decrypt_api_key(encrypted_api_key: str) -> str:
    """
    Descriptografa uma chave de API.
    
    Args:
        encrypted_api_key: Chave de API criptografada em formato base64
        
    Returns:
        Chave de API em texto plano
    """
    try:
        decrypted_data = fernet.decrypt(encrypted_api_key.encode())
        return decrypted_data.decode()
    except Exception as e:
        logger.error(f"Erro ao descriptografar chave de API: {str(e)}")
        raise ValueError(f"Falha ao descriptografar chave de API: {str(e)}")

def test_encryption() -> bool:
    """
    Testa a funcionalidade de criptografia.
    
    Returns:
        True se o teste for bem-sucedido, False caso contrário
    """
    try:
        test_key = "test-api-key-12345"
        encrypted = encrypt_api_key(test_key)
        decrypted = decrypt_api_key(encrypted)
        
        if decrypted == test_key:
            logger.info("Teste de criptografia bem-sucedido")
            return True
        else:
            logger.error("Teste de criptografia falhou: a chave descriptografada não corresponde à original")
            return False
    except Exception as e:
        logger.error(f"Teste de criptografia falhou com erro: {str(e)}")
        return False
