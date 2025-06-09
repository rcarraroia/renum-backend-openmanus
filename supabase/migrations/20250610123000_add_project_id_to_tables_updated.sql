-- Adicionar coluna project_id como UUID e permitindo nulos temporariamente, se não existir
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='agents' AND column_name='project_id'
  ) THEN
    ALTER TABLE agents ADD COLUMN project_id UUID;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='tools' AND column_name='project_id'
  ) THEN
    ALTER TABLE tools ADD COLUMN project_id UUID;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='agent_tools' AND column_name='project_id'
  ) THEN
    ALTER TABLE agent_tools ADD COLUMN project_id UUID;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='credentials' AND column_name='project_id'
  ) THEN
    ALTER TABLE credentials ADD COLUMN project_id UUID;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='knowledge_documents' AND column_name='project_id'
  ) THEN
    ALTER TABLE knowledge_documents ADD COLUMN project_id UUID;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='project_agents' AND column_name='project_id'
  ) THEN
    ALTER TABLE project_agents ADD COLUMN project_id UUID;
  END IF;
END
$$;

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
ALTER TABLE project_agents ALTER COLUMN project_id SET NOT NULL;

-- Opcional: Adicionar índices para performance de query
CREATE INDEX IF NOT EXISTS idx_agents_project_id ON agents (project_id);
CREATE INDEX IF NOT EXISTS idx_tools_project_id ON tools (project_id);
CREATE INDEX IF NOT EXISTS idx_agent_tools_project_id ON agent_tools (project_id);
CREATE INDEX IF NOT EXISTS idx_credentials_project_id ON credentials (project_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_project_id ON knowledge_documents (project_id);
CREATE INDEX IF NOT EXISTS idx_project_agents_project_id ON project_agents (project_id);
