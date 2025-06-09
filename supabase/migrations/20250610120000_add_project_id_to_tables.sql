-- Adicionar coluna project_id como UUID e permitindo nulos temporariamente
ALTER TABLE agents ADD COLUMN IF NOT EXISTS project_id UUID;
ALTER TABLE tools ADD COLUMN IF NOT EXISTS project_id UUID;
ALTER TABLE agent_tools ADD COLUMN IF NOT EXISTS project_id UUID;
ALTER TABLE credentials ADD COLUMN IF NOT EXISTS project_id UUID;
ALTER TABLE knowledge_documents ADD COLUMN IF NOT EXISTS project_id UUID;
-- Se a tabela agent_executions for adicionada futuramente, incluir aqui também
-- ALTER TABLE agent_executions ADD COLUMN IF NOT EXISTS project_id UUID;

-- Opcional: Para dados existentes, atualize project_id com um valor padrão (substitua pelo ID de um projeto padrão ou um UUID aleatório)
-- UPDATE agents SET project_id = '00000000-0000-0000-0000-000000000001' WHERE project_id IS NULL;
-- UPDATE tools SET project_id = '00000000-0000-0000-0000-000000000001' WHERE project_id IS NULL;
-- ... repita para todas as tabelas ...

-- Alterar coluna project_id para NOT NULL após preencher os valores existentes (se aplicável)
ALTER TABLE agents ALTER COLUMN project_id SET NOT NULL;
ALTER TABLE tools ALTER COLUMN project_id SET NOT NULL;
ALTER TABLE agent_tools ALTER COLUMN project_id SET NOT NULL;
ALTER TABLE credentials ALTER COLUMN project_id SET NOT NULL;
ALTER TABLE knowledge_documents ALTER COLUMN project_id SET NOT NULL;
-- ALTER TABLE agent_executions ALTER COLUMN project_id SET NOT NULL; -- Apenas se a tabela existir e for criada

-- Opcional: Adicionar índices para performance de query
CREATE INDEX IF NOT EXISTS idx_agents_project_id ON agents (project_id);
CREATE INDEX IF NOT EXISTS idx_tools_project_id ON tools (project_id);
CREATE INDEX IF NOT EXISTS idx_agent_tools_project_id ON agent_tools (project_id);
CREATE INDEX IF NOT EXISTS idx_credentials_project_id ON credentials (project_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_project_id ON knowledge_documents (project_id);
-- CREATE INDEX IF NOT EXISTS idx_agent_executions_project_id ON agent_executions (project_id);
