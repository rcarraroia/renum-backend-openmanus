"""
RenumTaskMaster agent implementation.

This module implements the RenumTaskMaster agent, which is specialized in
task management using natural language commands.
"""

import os
from typing import Dict, List, Optional, Any

from app.agent.base import BaseAgent
from app.agent.manus import Manus
from app.tool.task_management.task_store import TaskStore
from app.tool.task_management.task_tools import (
    CreateTaskTool,
    GetTaskTool,
    GetTasksTool,
    UpdateTaskStatusTool,
    UpdateTaskPriorityTool,
    DeleteTaskTool
)


class RenumTaskMaster(Manus):
    """
    RenumTaskMaster agent for task management.
    
    This agent specializes in processing natural language commands for
    task management, including creation, querying, and updating tasks.
    """
    
    def __init__(
        self,
        storage_path: str = "tasks.json",
        **kwargs
    ):
        """
        Initialize the RenumTaskMaster agent.
        
        Args:
            storage_path: Path to the JSON file for task storage
            **kwargs: Additional arguments to pass to the parent class
        """
        # Initialize the parent class
        super().__init__(**kwargs)
        
        # Set up task storage
        self.task_store = TaskStore(storage_path=storage_path)
        
        # Register task management tools
        self._register_task_tools()
        
        # Configure system prompt for task management
        self._configure_system_prompt()
    
    def _register_task_tools(self) -> None:
        """Register task management tools with the agent."""
        # Create tool instances
        create_task_tool = CreateTaskTool(self.task_store)
        get_task_tool = GetTaskTool(self.task_store)
        get_tasks_tool = GetTasksTool(self.task_store)
        update_status_tool = UpdateTaskStatusTool(self.task_store)
        update_priority_tool = UpdateTaskPriorityTool(self.task_store)
        delete_task_tool = DeleteTaskTool(self.task_store)
        
        # Register tools with the agent
        self.register_tool(create_task_tool)
        self.register_tool(get_task_tool)
        self.register_tool(get_tasks_tool)
        self.register_tool(update_status_tool)
        self.register_tool(update_priority_tool)
        self.register_tool(delete_task_tool)
    
    def _configure_system_prompt(self) -> None:
        """Configure the system prompt for task management."""
        self.system_prompt = """
        Você é o RenumTaskMaster, um assistente especializado em gerenciamento de tarefas.
        
        Suas responsabilidades incluem:
        1. Criar novas tarefas a partir de descrições em linguagem natural
        2. Responder a consultas sobre tarefas existentes
        3. Atualizar o status e a prioridade das tarefas
        4. Gerenciar a exclusão de tarefas quando necessário
        
        Ao processar comandos, você deve:
        - Extrair informações relevantes como descrição, data de vencimento e prioridade
        - Utilizar as ferramentas apropriadas para executar as ações solicitadas
        - Fornecer respostas claras e concisas sobre o resultado das ações
        
        Exemplos de comandos que você deve processar:
        - "Crie uma tarefa 'Revisar documentação' para o dia 28/05 com prioridade alta"
        - "Quais tarefas estão pendentes?"
        - "Mostre as tarefas de hoje"
        - "Marcar 'Revisar documentação' como concluída"
        - "Alterar a prioridade da tarefa 'Preparar apresentação' para média"
        
        Regras importantes:
        - Sempre confirme a criação, atualização ou exclusão de tarefas
        - Ao listar tarefas, organize-as por prioridade e data de vencimento
        - Utilize o formato ISO (YYYY-MM-DD) para datas internamente
        - Prioridades válidas são: baixa, média, alta
        - Status válidos são: pendente, em_progresso, concluída
        
        Você deve ser prestativo, eficiente e focado exclusivamente no gerenciamento de tarefas.
        """
        
        # Update the next_step_prompt to focus on task management
        self.next_step_prompt = """
        Baseado na conversa até agora e na última mensagem do usuário, qual é a próxima ação mais apropriada para gerenciar as tarefas?
        
        Considere:
        1. O usuário está tentando criar, consultar, atualizar ou excluir uma tarefa?
        2. Quais informações são necessárias para executar essa ação?
        3. Qual ferramenta deve ser utilizada para realizar essa ação?
        
        Escolha a ferramenta mais adequada e forneça os parâmetros corretos para executá-la.
        """
    
    async def process_message(self, message: str) -> str:
        """
        Process a user message and generate a response.
        
        This method overrides the parent class to add specialized handling
        for task management commands.
        
        Args:
            message: User message to process
            
        Returns:
            Agent's response
        """
        # Pre-process the message to extract dates in Brazilian format
        processed_message = self._preprocess_date_formats(message)
        
        # Use the parent class to process the message
        return await super().process_message(processed_message)
    
    def _preprocess_date_formats(self, message: str) -> str:
        """
        Pre-process message to convert Brazilian date formats to ISO format.
        
        Args:
            message: Original user message
            
        Returns:
            Processed message with standardized date formats
        """
        import re
        from datetime import datetime
        
        # Pattern for Brazilian date format (DD/MM/YYYY or DD/MM)
        br_date_pattern = r'(\d{1,2}/\d{1,2}(?:/\d{4})?)'
        
        def convert_date(match):
            date_str = match.group(1)
            try:
                # Add current year if year is not specified
                if len(date_str.split('/')) == 2:
                    current_year = datetime.now().year
                    date_str = f"{date_str}/{current_year}"
                
                # Parse the date
                date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                
                # Return ISO format
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                # Return original string if parsing fails
                return match.group(1)
        
        # Replace all occurrences of Brazilian date format
        processed_message = re.sub(br_date_pattern, convert_date, message)
        
        return processed_message
