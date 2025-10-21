"""Workflow orchestration engine."""
import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from test_ai.config import get_settings
from test_ai.api_clients import OpenAIClient, GitHubClient, NotionClientWrapper, GmailClient


class StepType(str, Enum):
    """Types of workflow steps."""
    OPENAI = "openai"
    GITHUB = "github"
    NOTION = "notion"
    GMAIL = "gmail"
    TRANSFORM = "transform"


class WorkflowStep(BaseModel):
    """A single step in a workflow."""
    
    id: str = Field(..., description="Step identifier")
    type: StepType = Field(..., description="Step type")
    action: str = Field(..., description="Action to perform")
    params: Dict[str, Any] = Field(default_factory=dict, description="Step parameters")
    next_step: Optional[str] = Field(None, description="Next step ID")


class Workflow(BaseModel):
    """A workflow definition."""
    
    id: str = Field(..., description="Workflow identifier")
    name: str = Field(..., description="Workflow name")
    description: str = Field(..., description="Workflow description")
    steps: List[WorkflowStep] = Field(default_factory=list, description="Workflow steps")
    variables: Dict[str, Any] = Field(default_factory=dict, description="Workflow variables")


class WorkflowResult(BaseModel):
    """Result of a workflow execution."""
    
    workflow_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    steps_executed: List[str] = Field(default_factory=list)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)


class WorkflowEngine:
    """Orchestrates workflow execution."""
    
    def __init__(self):
        self.settings = get_settings()
        self.openai_client = OpenAIClient()
        self.github_client = GitHubClient()
        self.notion_client = NotionClientWrapper()
        self.gmail_client = GmailClient()
    
    def execute_workflow(self, workflow: Workflow) -> WorkflowResult:
        """Execute a workflow."""
        result = WorkflowResult(
            workflow_id=workflow.id,
            status="running",
            started_at=datetime.now()
        )
        
        context = workflow.variables.copy()
        current_step_id = workflow.steps[0].id if workflow.steps else None
        
        while current_step_id:
            step = next((s for s in workflow.steps if s.id == current_step_id), None)
            if not step:
                break
            
            try:
                output = self._execute_step(step, context)
                result.steps_executed.append(step.id)
                result.outputs[step.id] = output
                
                context[f"{step.id}_output"] = output
                current_step_id = step.next_step
                
            except Exception as e:
                result.errors.append(f"Error in step {step.id}: {str(e)}")
                result.status = "failed"
                break
        
        if not result.errors:
            result.status = "completed"
        
        result.completed_at = datetime.now()
        
        self._save_workflow_log(workflow, result)
        
        return result
    
    def _execute_step(self, step: WorkflowStep, context: Dict[str, Any]) -> Any:
        """Execute a single workflow step."""
        params = self._interpolate_params(step.params, context)
        
        if step.type == StepType.OPENAI:
            return self._execute_openai_step(step.action, params)
        elif step.type == StepType.GITHUB:
            return self._execute_github_step(step.action, params)
        elif step.type == StepType.NOTION:
            return self._execute_notion_step(step.action, params)
        elif step.type == StepType.GMAIL:
            return self._execute_gmail_step(step.action, params)
        elif step.type == StepType.TRANSFORM:
            return self._execute_transform_step(step.action, params, context)
        else:
            raise ValueError(f"Unknown step type: {step.type}")
    
    def _execute_openai_step(self, action: str, params: Dict) -> Any:
        """Execute an OpenAI step."""
        if action == "generate_completion":
            return self.openai_client.generate_completion(**params)
        elif action == "summarize":
            return self.openai_client.summarize_text(params.get("text", ""))
        elif action == "generate_sop":
            return self.openai_client.generate_sop(params.get("task_description", ""))
        else:
            raise ValueError(f"Unknown OpenAI action: {action}")
    
    def _execute_github_step(self, action: str, params: Dict) -> Any:
        """Execute a GitHub step."""
        if action == "create_issue":
            return self.github_client.create_issue(**params)
        elif action == "commit_file":
            return self.github_client.commit_file(**params)
        elif action == "list_repositories":
            return self.github_client.list_repositories()
        else:
            raise ValueError(f"Unknown GitHub action: {action}")
    
    def _execute_notion_step(self, action: str, params: Dict) -> Any:
        """Execute a Notion step."""
        if action == "create_page":
            return self.notion_client.create_page(**params)
        elif action == "append_to_page":
            return self.notion_client.append_to_page(**params)
        elif action == "search_pages":
            return self.notion_client.search_pages(params.get("query", ""))
        else:
            raise ValueError(f"Unknown Notion action: {action}")
    
    def _execute_gmail_step(self, action: str, params: Dict) -> Any:
        """Execute a Gmail step."""
        if action == "list_messages":
            return self.gmail_client.list_messages(**params)
        elif action == "get_message":
            return self.gmail_client.get_message(params.get("message_id", ""))
        else:
            raise ValueError(f"Unknown Gmail action: {action}")
    
    def _execute_transform_step(self, action: str, params: Dict, context: Dict) -> Any:
        """Execute a transform step."""
        if action == "extract":
            key = params.get("key", "")
            source = params.get("source", "")
            return context.get(source, {}).get(key, "")
        elif action == "format":
            template = params.get("template", "")
            return template.format(**context)
        else:
            raise ValueError(f"Unknown transform action: {action}")
    
    def _interpolate_params(self, params: Dict, context: Dict) -> Dict:
        """Interpolate context variables in parameters."""
        result = {}
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                var_name = value[2:-2].strip()
                result[key] = context.get(var_name, value)
            else:
                result[key] = value
        return result
    
    def _save_workflow_log(self, workflow: Workflow, result: WorkflowResult):
        """Save workflow execution log."""
        log_file = self.settings.logs_dir / f"workflow_{workflow.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        log_data = {
            "workflow": workflow.model_dump(),
            "result": result.model_dump(mode='json')
        }
        
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2, default=str)
    
    def save_workflow(self, workflow: Workflow) -> bool:
        """Save a workflow definition."""
        try:
            file_path = self.settings.workflows_dir / f"{workflow.id}.json"
            with open(file_path, 'w') as f:
                json.dump(workflow.model_dump(), f, indent=2)
            return True
        except Exception:
            return False
    
    def load_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Load a workflow definition."""
        try:
            file_path = self.settings.workflows_dir / f"{workflow_id}.json"
            with open(file_path, 'r') as f:
                data = json.load(f)
            return Workflow(**data)
        except Exception:
            return None
    
    def list_workflows(self) -> List[Dict]:
        """List all available workflows."""
        workflows = []
        for file_path in self.settings.workflows_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                workflows.append({
                    "id": data.get("id"),
                    "name": data.get("name"),
                    "description": data.get("description")
                })
            except Exception:
                continue
        return workflows
