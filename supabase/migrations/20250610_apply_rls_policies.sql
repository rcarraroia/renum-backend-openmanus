-- Habilitar Row Level Security (RLS) nas tabelas relevantes
ALTER TABLE public.agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tools ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_tools ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.knowledge_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_executions ENABLE ROW LEVEL SECURITY;

-- Função para definir o contexto do projeto na sessão
CREATE OR REPLACE FUNCTION public.set_project_context(p_project_id UUID)
RETURNS void LANGUAGE plpgsql AS $$
BEGIN
  PERFORM set_config('app.current_project_id', p_project_id::text, true);
END;
$$;

-- Função para validar o project_id nas operações de insert/update
CREATE OR REPLACE FUNCTION public.validate_project_id()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.project_id IS NULL THEN
    RAISE EXCEPTION 'project_id não pode ser nulo';
  END IF;

  IF NEW.project_id <> current_setting('app.current_project_id')::uuid THEN
    RAISE EXCEPTION 'project_id inválido para o contexto atual';
  END IF;

  RETURN NEW;
END;
$$;

-- Políticas RLS para a tabela agents
CREATE POLICY agents_select_policy ON public.agents
  FOR SELECT USING (project_id = current_setting('app.current_project_id')::uuid);

CREATE POLICY agents_insert_policy ON public.agents
  FOR INSERT WITH CHECK (project_id = current_setting('app.current_project_id')::uuid);

CREATE POLICY agents_update_policy ON public.agents
  FOR UPDATE USING (project_id = current_setting('app.current_project_id')::uuid)
  WITH CHECK (project_id = current_setting('app.current_project_id')::uuid);

CREATE POLICY agents_delete_policy ON public.agents
  FOR DELETE USING (project_id = current_setting('app.current_project_id')::uuid);

-- Políticas RLS para a tabela tools
CREATE POLICY tools_select_policy ON public.tools
  FOR SELECT USING (project_id = current_setting('app.current_project_id')::uuid);

CREATE POLICY tools_insert_policy ON public.tools
  FOR INSERT WITH CHECK (project_id = current_setting('app.current_project_id')::uuid);

CREATE POLICY tools_update_policy ON public.tools
  FOR UPDATE USING (project_id = current_setting('app.current_project_id')::uuid)
  WITH CHECK (project_id = current_setting('app.current_project_id')::uuid);

CREATE POLICY tools_delete_policy ON public.tools
  FOR DELETE USING (project_id = current_setting('app.current_project_id')::uuid);

-- Políticas RLS para a tabela agent_tools
CREATE POLICY agent_tools_select_policy ON public.agent_tools
  FOR SELECT USING (project_id = current_setting('app.current_project_id')::uuid);

CREATE POLICY agent_tools_insert_policy ON public.agent_tools
  FOR INSERT WITH CHECK (project_id = current_setting('app.current_project_id')::uuid);

CREATE POLICY agent_tools_update_policy ON public.agent_tools
  FOR UPDATE USING (project_id = current_setting('app.current_project_id')::uuid)
  WITH CHECK (project_id = current_setting('app.current_project_id')::uuid);

CREATE POLICY agent_tools_delete_policy ON public.agent_tools
  FOR DELETE USING (project_id = current_setting('app.current_project_id')::uuid);

-- Políticas RLS para a tabela credentials
CREATE POLICY credentials_select_policy ON public.credentials
  FOR SELECT USING (project_id = current_setting('app.current_project_id')::uuid);

CREATE POLICY credentials_insert_policy ON public.credentials
  FOR INSERT WITH CHECK (project_id = current_setting('app.current_project_id')::uuid);

CREATE POLICY credentials_update_policy ON public.credentials
  FOR UPDATE USING (project_id = current_setting('app.current_project_id')::uuid)
  WITH CHECK (project_id = current_setting('app.current_project_id')::uuid);

CREATE POLICY credentials_delete_policy ON public.credentials
  FOR DELETE USING (project_id = current_setting('app.current_project_id')::uuid);

-- Políticas RLS para a tabela knowledge_documents
CREATE POLICY knowledge_documents_select_policy ON public.knowledge_documents
  FOR SELECT USING (project_id = current_setting('app.current_project_id')::uuid);

CREATE POLICY knowledge_documents_insert_policy ON public.knowledge_documents
  FOR INSERT WITH CHECK (project_id = current_setting('app.current_project_id')::uuid);

CREATE POLICY knowledge_documents_update_policy ON public.knowledge_documents
  FOR UPDATE USING (project_id = current_setting('app.current_project_id')::uuid)
  WITH CHECK (project_id = current_setting('app.current_project_id')::uuid);

CREATE POLICY knowledge_documents_delete_policy ON public.knowledge_documents
  FOR DELETE USING (project_id = current_setting('app.current_project_id')::uuid);

-- Políticas RLS para a tabela agent_executions
CREATE POLICY agent_executions_select_policy ON public.agent_executions
  FOR SELECT USING (project_id = current_setting('app.current_project_id')::uuid);

CREATE POLICY agent_executions_insert_policy ON public.agent_executions
  FOR INSERT WITH CHECK (project_id = current_setting('app.current_project_id')::uuid);

CREATE POLICY agent_executions_update_policy ON public.agent_executions
  FOR UPDATE USING (project_id = current_setting('app.current_project_id')::uuid)
  WITH CHECK (project_id = current_setting('app.current_project_id')::uuid);

CREATE POLICY agent_executions_delete_policy ON public.agent_executions
  FOR DELETE USING (project_id = current_setting('app.current_project_id')::uuid);

-- Triggers para validar project_id antes de insert ou update
CREATE TRIGGER validate_project_id_agents
BEFORE INSERT OR UPDATE ON public.agents
FOR EACH ROW EXECUTE FUNCTION public.validate_project_id();

CREATE TRIGGER validate_project_id_tools
BEFORE INSERT OR UPDATE ON public.tools
FOR EACH ROW EXECUTE FUNCTION public.validate_project_id();

CREATE TRIGGER validate_project_id_agent_tools
BEFORE INSERT OR UPDATE ON public.agent_tools
FOR EACH ROW EXECUTE FUNCTION public.validate_project_id();

CREATE TRIGGER validate_project_id_credentials
BEFORE INSERT OR UPDATE ON public.credentials
FOR EACH ROW EXECUTE FUNCTION public.validate_project_id();

CREATE TRIGGER validate_project_id_knowledge_documents
BEFORE INSERT OR UPDATE ON public.knowledge_documents
FOR EACH ROW EXECUTE FUNCTION public.validate_project_id();

CREATE TRIGGER validate_project_id_agent_executions
BEFORE INSERT OR UPDATE ON public.agent_executions
FOR EACH ROW EXECUTE FUNCTION public.validate_project_id();
