# Auditoria de Endpoints - Backend

Este documento detalha os principais endpoints dos módulos `code_support.py`, `content_creator.py` e `data_analyst.py` do backend, conforme solicitado para fins de auditoria e documentação.

---

## code_support.py

| Método | Caminho                         | Função                      | Descrição                                                        |
|--------|---------------------------------|-----------------------------|------------------------------------------------------------------|
| POST   | /boilerplate                    | generate_boilerplate        | Gera código boilerplate a partir de um request                   |
| POST   | /tests                          | generate_tests              | Gera testes unitários a partir de um request                     |
| POST   | /project-structure              | generate_project_structure  | Gera estrutura de projeto a partir de um request                 |
| POST   | /prompt                         | send_prompt                 | Envia prompt ao agente de suporte a código                       |
| DELETE | /conversation/{conversation_id} | end_conversation            | Encerra uma conversa de suporte a código                         |

---

## content_creator.py

| Método | Caminho                         | Função                      | Descrição                                                        |
|--------|---------------------------------|-----------------------------|------------------------------------------------------------------|
| POST   | /email                          | generate_email              | Gera rascunho de e-mail a partir de um request                   |
| POST   | /social-media                   | create_social_media_post    | Cria post para redes sociais a partir de um request              |
| POST   | /content-store                  | manage_content_store        | Gerencia conteúdo armazenado                                     |
| POST   | /prompt                         | send_prompt                 | Envia prompt ao agente de criação de conteúdo                    |
| DELETE | /conversation/{conversation_id} | end_conversation            | Encerra uma conversa de criação de conteúdo                      |

---

## data_analyst.py

| Método | Caminho                         | Função                      | Descrição                                                        |
|--------|---------------------------------|-----------------------------|------------------------------------------------------------------|
| POST   | /data-loader                    | load_data                   | Carrega dados de diversas fontes                                 |
| POST   | /sales-analysis                 | analyze_sales               | Analisa dados de vendas                                          |
| POST   | /filtering                      | filter_data                 | Filtra e transforma dados                                        |
| POST   | /prompt                         | send_prompt                 | Envia prompt ao agente de análise de dados                       |
| DELETE | /conversation/{conversation_id} | end_conversation            | Encerra uma conversa de análise de dados                         |

---

Cada endpoint segue o padrão REST, recebendo dados via request body (para POST) ou path param (para DELETE), e retorna respostas padronizadas (normalmente Dict ou modelos de resposta).

---

## Rotas em `api/routes/`

### codesupport.py

| Método | Caminho                | Função                | Descrição resumida                                 |
|--------|------------------------|-----------------------|----------------------------------------------------|
| POST   | /message               | process_message       | Processa uma mensagem para o agente de code support|
| POST   | /generate/project      | generate_project      | Gera um novo projeto a partir de um request        |
| POST   | /generate/boilerplate  | generate_boilerplate  | Gera código boilerplate                            |
| POST   | /generate/structure    | generate_structure    | Gera a estrutura de um projeto                     |
| POST   | /generate/tests        | generate_tests        | Gera testes para o projeto                         |

---

### taskmaster.py

| Método | Caminho     | Função            | Descrição resumida                                 |
|--------|-------------|-------------------|----------------------------------------------------|
| POST   | /prompt     | send_prompt       | Envia prompt para o agente TaskMaster              |
| POST   | /shutdown   | shutdown_agent    | Solicita o desligamento do agente                  |
| GET    | /status     | get_agent_status  | Consulta o status do agente                        |
