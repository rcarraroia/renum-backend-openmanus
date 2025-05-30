#!/bin/bash

# Carregar variáveis de ambiente do arquivo .env
source .env

# Script para executar os testes end-to-end com variáveis de ambiente configuradas
# Este script garante que todas as variáveis necessárias estejam definidas

# Definir variáveis de ambiente
export SUPABASE_URL="https://wvplmbsfxsqfxupeucsd.supabase.co"
export SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind2cGxtYnNmeHNxZnh1cGV1Y3NkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODI4NTk4NSwiZXhwIjoyMDYzODYxOTg1fQ.4HE3NrXVeMSCuzsTdwR9bgSA9UuSuD_tFPbwCmbhF2w"

# Gerar uma chave de criptografia segura para testes
export ENCRYPTION_KEY=$(python -c "import base64; import secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())")
echo "ENCRYPTION_KEY gerada: $ENCRYPTION_KEY"

# Executar os testes
echo "Executando testes end-to-end..."
python -m tests.test_agent_builder_e2e
