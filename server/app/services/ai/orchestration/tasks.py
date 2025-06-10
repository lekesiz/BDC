"""Task orchestration with Celery integration."""

from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from enum import Enum
from celery import Task, group, chain, chord
from celery.result import AsyncResult
import logging
import json
import traceback
from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"
    WAITING_HUMAN_REVIEW = "waiting_human_review"


class TaskResult(BaseModel):
    """Result of a task execution."""
    task_name: str
    status: TaskStatus
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time: Optional[float] = None  # seconds
    retry_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PipelineTask(Task):
    """Base Celery task for pipeline operations."""
    
    name = "pipeline_task"
    max_retries = 3
    default_retry_delay = 60  # seconds
    
    def __init__(self):
        super().__init__()
        self._task_registry: Dict[str, Callable] = {}
        self._setup_default_tasks()
    
    def _setup_default_tasks(self):
        """Register default task implementations."""
        from ..models.text_generation import TextGenerationService
        from ..models.classification import ClassificationService
        from ..models.extraction import ExtractionService
        
        # Register default task handlers
        self.register_task_handler("text_generation", self._text_generation_handler)
        self.register_task_handler("classification", self._classification_handler)
        self.register_task_handler("extraction", self._extraction_handler)
        self.register_task_handler("validation", self._validation_handler)
    
    def register_task_handler(self, task_type: str, handler: Callable):
        """Register a task handler for a specific task type."""
        self._task_registry[task_type] = handler
    
    def run(self, task_config: dict, input_data: dict, context: dict = None) -> dict:
        """Execute a pipeline task."""
        task_name = task_config["name"]
        task_type = task_config["type"]
        
        logger.info(f"Starting task: {task_name} (type: {task_type})")
        
        result = TaskResult(
            task_name=task_name,
            status=TaskStatus.RUNNING,
            started_at=datetime.utcnow(),
            retry_count=self.request.retries
        )
        
        try:
            # Get task handler
            handler = self._task_registry.get(task_type)
            if not handler:
                if task_type == "custom":
                    handler = self._custom_task_handler
                else:
                    raise ValueError(f"Unknown task type: {task_type}")
            
            # Execute task
            output = handler(
                task_config=task_config,
                input_data=input_data,
                context=context or {}
            )
            
            # Update result
            result.status = TaskStatus.COMPLETED
            result.output = output
            result.completed_at = datetime.utcnow()
            result.execution_time = (result.completed_at - result.started_at).total_seconds()
            
            logger.info(f"Task completed: {task_name} (execution time: {result.execution_time}s)")
            
        except Exception as e:
            logger.error(f"Task failed: {task_name} - {str(e)}")
            result.status = TaskStatus.FAILED
            result.error = str(e)
            result.completed_at = datetime.utcnow()
            result.execution_time = (result.completed_at - result.started_at).total_seconds()
            
            # Retry if applicable
            if self.request.retries < self.max_retries:
                logger.info(f"Retrying task: {task_name} (attempt {self.request.retries + 1}/{self.max_retries})")
                raise self.retry(exc=e, countdown=self.default_retry_delay)
        
        return result.dict()
    
    def _text_generation_handler(self, task_config: dict, input_data: dict, context: dict) -> dict:
        """Handle text generation tasks."""
        from ..models.text_generation import TextGenerationService
        
        service = TextGenerationService()
        model = task_config.get("model", "gpt-3.5-turbo")
        model_version = task_config.get("model_version")
        parameters = task_config.get("parameters", {})
        
        # Extract prompt from input data
        prompt = input_data.get("prompt") or parameters.get("prompt")
        if not prompt:
            raise ValueError("No prompt provided for text generation")
        
        # Generate text
        response = service.generate(
            prompt=prompt,
            model=model,
            **parameters
        )
        
        return {
            "generated_text": response.text,
            "model": response.model,
            "usage": response.usage,
            "metadata": response.metadata
        }
    
    def _classification_handler(self, task_config: dict, input_data: dict, context: dict) -> dict:
        """Handle classification tasks."""
        from ..models.classification import ClassificationService
        
        service = ClassificationService()
        model = task_config.get("model", "bert-base-uncased")
        parameters = task_config.get("parameters", {})
        
        # Extract text from input data
        text = input_data.get("text") or input_data.get("document", {}).get("content")
        if not text:
            raise ValueError("No text provided for classification")
        
        # Get categories
        categories = parameters.get("categories", [])
        if not categories:
            raise ValueError("No categories provided for classification")
        
        # Classify text
        result = service.classify(
            text=text,
            categories=categories,
            model=model,
            **parameters
        )
        
        return {
            "category": result.category,
            "confidence": result.confidence,
            "all_scores": result.scores,
            "metadata": result.metadata
        }
    
    def _extraction_handler(self, task_config: dict, input_data: dict, context: dict) -> dict:
        """Handle extraction tasks."""
        from ..models.extraction import ExtractionService
        
        service = ExtractionService()
        model = task_config.get("model", "gpt-3.5-turbo")
        parameters = task_config.get("parameters", {})
        
        # Extract text from input data
        text = input_data.get("text") or input_data.get("document", {}).get("content")
        if not text:
            raise ValueError("No text provided for extraction")
        
        # Get schema
        schema = parameters.get("schema", {})
        if not schema:
            raise ValueError("No extraction schema provided")
        
        # Extract information
        result = service.extract(
            text=text,
            schema=schema,
            model=model,
            **parameters
        )
        
        return {
            "extracted_data": result.data,
            "confidence": result.confidence,
            "metadata": result.metadata
        }
    
    def _validation_handler(self, task_config: dict, input_data: dict, context: dict) -> dict:
        """Handle validation tasks."""
        parameters = task_config.get("parameters", {})
        rules = parameters.get("rules", [])
        
        validation_results = []
        all_valid = True
        
        for rule in rules:
            rule_type = rule.get("type")
            field = rule.get("field")
            condition = rule.get("condition")
            value = rule.get("value")
            
            # Get field value from input data
            field_value = input_data
            for part in field.split("."):
                field_value = field_value.get(part, None)
                if field_value is None:
                    break
            
            # Validate based on rule type
            is_valid = False
            if rule_type == "required":
                is_valid = field_value is not None
            elif rule_type == "type":
                is_valid = isinstance(field_value, eval(value))
            elif rule_type == "range":
                min_val, max_val = value
                is_valid = min_val <= field_value <= max_val
            elif rule_type == "regex":
                import re
                is_valid = bool(re.match(value, str(field_value)))
            elif rule_type == "custom":
                # Execute custom validation function
                func = eval(condition)
                is_valid = func(field_value)
            
            validation_results.append({
                "field": field,
                "rule": rule_type,
                "valid": is_valid,
                "value": field_value,
                "expected": value
            })
            
            if not is_valid:
                all_valid = False
        
        return {
            "valid": all_valid,
            "results": validation_results,
            "summary": f"{sum(r['valid'] for r in validation_results)}/{len(validation_results)} rules passed"
        }
    
    def _custom_task_handler(self, task_config: dict, input_data: dict, context: dict) -> dict:
        """Handle custom tasks."""
        parameters = task_config.get("parameters", {})
        handler_path = parameters.get("handler")
        
        if not handler_path:
            raise ValueError("No handler specified for custom task")
        
        # Import and execute custom handler
        module_path, func_name = handler_path.rsplit(".", 1)
        module = __import__(module_path, fromlist=[func_name])
        handler = getattr(module, func_name)
        
        return handler(
            task_config=task_config,
            input_data=input_data,
            context=context
        )


class CeleryTaskManager:
    """Manager for Celery task execution."""
    
    def __init__(self, celery_app):
        self.celery_app = celery_app
        self.task = PipelineTask()
        self.task.bind(celery_app)
    
    def execute_single_task(self, task_config: dict, input_data: dict, context: dict = None) -> AsyncResult:
        """Execute a single task asynchronously."""
        return self.task.apply_async(
            args=[task_config, input_data, context],
            task_id=f"{task_config['name']}_{datetime.utcnow().timestamp()}"
        )
    
    def execute_parallel_tasks(self, tasks: List[dict], input_data: dict, context: dict = None) -> AsyncResult:
        """Execute multiple tasks in parallel."""
        job = group(
            self.task.s(task_config, input_data, context)
            for task_config in tasks
        )
        return job.apply_async()
    
    def execute_sequential_tasks(self, tasks: List[dict], input_data: dict, context: dict = None) -> AsyncResult:
        """Execute tasks sequentially."""
        if not tasks:
            return None
        
        # Create chain of tasks
        task_chain = self.task.s(tasks[0], input_data, context)
        
        for task_config in tasks[1:]:
            task_chain = task_chain | self.task.s(task_config, input_data, context)
        
        return task_chain.apply_async()
    
    def execute_with_callback(self, tasks: List[dict], callback_task: dict, 
                            input_data: dict, context: dict = None) -> AsyncResult:
        """Execute tasks with a callback after completion."""
        job = chord(
            (self.task.s(task_config, input_data, context) for task_config in tasks),
            self.task.s(callback_task, input_data, context)
        )
        return job.apply_async()
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the status of a task."""
        result = AsyncResult(task_id, app=self.celery_app)
        
        status_map = {
            "PENDING": TaskStatus.PENDING,
            "STARTED": TaskStatus.RUNNING,
            "RETRY": TaskStatus.RETRYING,
            "FAILURE": TaskStatus.FAILED,
            "SUCCESS": TaskStatus.COMPLETED
        }
        
        return {
            "task_id": task_id,
            "status": status_map.get(result.state, TaskStatus.PENDING),
            "result": result.result if result.ready() else None,
            "error": str(result.info) if result.failed() else None
        }
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        result = AsyncResult(task_id, app=self.celery_app)
        result.revoke(terminate=True)
        return True