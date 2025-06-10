"""Main pipeline orchestrator that coordinates all components."""

from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
import json

from .pipeline import Pipeline, PipelineConfig, PipelineExecution, PipelineStatus, TaskConfig
from .tasks import CeleryTaskManager, TaskStatus, TaskResult
from .versioning import ModelVersionManager
from .human_loop import HumanInLoopManager
from .cache import ResultCache
from .monitoring import PipelineMonitor


logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """Orchestrates AI pipeline execution with all components."""
    
    def __init__(self, 
                 celery_app,
                 redis_client,
                 model_registry_path: str = "/tmp/model_registry",
                 cache_ttl: int = 3600):
        """Initialize the orchestrator with required services."""
        self.celery_app = celery_app
        self.redis_client = redis_client
        self.task_manager = CeleryTaskManager(celery_app)
        self.version_manager = ModelVersionManager(model_registry_path)
        self.human_loop_manager = HumanInLoopManager(redis_client)
        self.cache = ResultCache(redis_client, default_ttl=cache_ttl)
        self.monitor = PipelineMonitor(redis_client)
        
        self.executor = ThreadPoolExecutor(max_workers=10)
        self._execution_store: Dict[str, PipelineExecution] = {}
        self._pipeline_store: Dict[str, Pipeline] = {}
        
        # Callback handlers
        self._completion_callbacks: List[Callable] = []
        self._error_callbacks: List[Callable] = []
        self._progress_callbacks: List[Callable] = []
    
    def register_pipeline(self, pipeline: Pipeline, pipeline_id: Optional[str] = None) -> str:
        """Register a pipeline for execution."""
        pipeline_id = pipeline_id or pipeline.config.name
        self._pipeline_store[pipeline_id] = pipeline
        
        # Register pipeline in monitoring
        self.monitor.register_pipeline(pipeline_id, pipeline.config.dict())
        
        logger.info(f"Registered pipeline: {pipeline_id}")
        return pipeline_id
    
    async def execute_pipeline(self, 
                             pipeline_id: str, 
                             input_data: Dict[str, Any],
                             execution_id: Optional[str] = None) -> str:
        """Execute a pipeline asynchronously."""
        # Get pipeline
        pipeline = self._pipeline_store.get(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline not found: {pipeline_id}")
        
        # Create execution instance
        execution = pipeline.create_execution(input_data)
        if execution_id:
            execution.id = execution_id
        
        # Store execution
        self._execution_store[execution.id] = execution
        
        # Start monitoring
        self.monitor.start_execution(execution.id, pipeline_id)
        
        # Execute pipeline in background
        asyncio.create_task(self._execute_pipeline_async(pipeline, execution))
        
        logger.info(f"Started pipeline execution: {execution.id}")
        return execution.id
    
    async def _execute_pipeline_async(self, pipeline: Pipeline, execution: PipelineExecution):
        """Execute pipeline tasks asynchronously."""
        try:
            # Update execution status
            execution.status = PipelineStatus.RUNNING
            execution.started_at = datetime.utcnow()
            self._notify_progress(execution.id, "Pipeline started", 0)
            
            # Get execution order
            execution_order = pipeline.get_execution_order()
            total_tasks = len(pipeline.config.tasks)
            completed_tasks = 0
            
            # Execute tasks by stage
            context = {
                "pipeline_id": pipeline.config.name,
                "execution_id": execution.id,
                "global_parameters": pipeline.config.global_parameters
            }
            
            task_outputs = {}
            
            for stage_idx, stage_tasks in enumerate(execution_order):
                logger.info(f"Executing stage {stage_idx + 1} with {len(stage_tasks)} tasks")
                
                # Execute tasks in parallel within stage
                stage_results = await self._execute_stage(
                    stage_tasks,
                    execution.input_data,
                    task_outputs,
                    context,
                    pipeline.config
                )
                
                # Process results
                for task_name, result in stage_results.items():
                    execution.task_results[task_name] = result
                    
                    if result["status"] == TaskStatus.COMPLETED:
                        task_outputs[task_name] = result.get("output", {})
                        completed_tasks += 1
                    elif result["status"] == TaskStatus.FAILED:
                        # Handle task failure
                        execution.status = PipelineStatus.FAILED
                        execution.error = f"Task '{task_name}' failed: {result.get('error')}"
                        self._handle_failure(execution)
                        return
                
                # Update progress
                progress = (completed_tasks / total_tasks) * 100
                self._notify_progress(
                    execution.id,
                    f"Completed stage {stage_idx + 1}/{len(execution_order)}",
                    progress
                )
            
            # Pipeline completed successfully
            execution.status = PipelineStatus.COMPLETED
            execution.output_data = self._aggregate_outputs(task_outputs, pipeline.config)
            execution.completed_at = datetime.utcnow()
            
            # Store final result in cache
            if pipeline.config.cache_ttl > 0:
                cache_key = self._generate_cache_key(pipeline.config.name, execution.input_data)
                self.cache.set(cache_key, execution.output_data, ttl=pipeline.config.cache_ttl)
            
            # Complete monitoring
            self.monitor.complete_execution(execution.id, execution.status)
            
            # Notify completion
            self._notify_completion(execution)
            
            logger.info(f"Pipeline execution completed: {execution.id}")
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {execution.id} - {str(e)}")
            execution.status = PipelineStatus.FAILED
            execution.error = str(e)
            execution.completed_at = datetime.utcnow()
            self._handle_failure(execution)
    
    async def _execute_stage(self, 
                           tasks: List[TaskConfig],
                           input_data: Dict[str, Any],
                           previous_outputs: Dict[str, Any],
                           context: Dict[str, Any],
                           pipeline_config: PipelineConfig) -> Dict[str, Any]:
        """Execute a stage of tasks in parallel."""
        stage_results = {}
        
        # Prepare task executions
        task_futures = []
        
        for task in tasks:
            # Check cache
            if task.cache_enabled and pipeline_config.cache_ttl > 0:
                cache_key = self._generate_task_cache_key(task.name, input_data, previous_outputs)
                cached_result = self.cache.get(cache_key)
                
                if cached_result:
                    logger.info(f"Using cached result for task: {task.name}")
                    stage_results[task.name] = {
                        "status": TaskStatus.COMPLETED,
                        "output": cached_result,
                        "cached": True
                    }
                    continue
            
            # Prepare task input
            task_input = self._prepare_task_input(task, input_data, previous_outputs)
            
            # Check if human review is required
            if task.human_review_required:
                # Submit for human review
                review_result = await self._handle_human_review(task, task_input, context)
                stage_results[task.name] = review_result
            else:
                # Execute task
                if task.model and task.model_version:
                    # Ensure correct model version
                    model_info = self.version_manager.get_model_version(task.model, task.model_version)
                    context["model_info"] = model_info
                
                future = self.task_manager.execute_single_task(
                    task.dict(),
                    task_input,
                    context
                )
                task_futures.append((task.name, future))
        
        # Wait for all tasks to complete
        for task_name, future in task_futures:
            try:
                result = future.get(timeout=tasks[0].timeout)
                stage_results[task_name] = result
                
                # Cache successful results
                task = next(t for t in tasks if t.name == task_name)
                if task.cache_enabled and result["status"] == TaskStatus.COMPLETED:
                    cache_key = self._generate_task_cache_key(
                        task_name,
                        input_data,
                        previous_outputs
                    )
                    self.cache.set(
                        cache_key,
                        result.get("output"),
                        ttl=pipeline_config.cache_ttl
                    )
                    
            except Exception as e:
                logger.error(f"Task execution failed: {task_name} - {str(e)}")
                stage_results[task_name] = {
                    "status": TaskStatus.FAILED,
                    "error": str(e)
                }
        
        return stage_results
    
    async def _handle_human_review(self, 
                                 task: TaskConfig,
                                 task_input: Dict[str, Any],
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle human-in-the-loop review for a task."""
        # Create review request
        review_id = self.human_loop_manager.create_review(
            task_name=task.name,
            task_type=task.type,
            input_data=task_input,
            metadata={
                "pipeline_id": context["pipeline_id"],
                "execution_id": context["execution_id"],
                "threshold": task.human_review_threshold
            }
        )
        
        logger.info(f"Created human review request: {review_id} for task: {task.name}")
        
        # Wait for review completion (with timeout)
        max_wait_time = task.timeout or 300
        start_time = datetime.utcnow()
        
        while True:
            review = self.human_loop_manager.get_review(review_id)
            
            if review["status"] == "completed":
                return {
                    "status": TaskStatus.COMPLETED,
                    "output": review["result"],
                    "human_reviewed": True,
                    "reviewer": review.get("reviewer"),
                    "review_time": review.get("completed_at")
                }
            elif review["status"] == "rejected":
                return {
                    "status": TaskStatus.FAILED,
                    "error": f"Human review rejected: {review.get('reason')}",
                    "human_reviewed": True
                }
            
            # Check timeout
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            if elapsed > max_wait_time:
                return {
                    "status": TaskStatus.FAILED,
                    "error": "Human review timeout",
                    "human_reviewed": False
                }
            
            # Wait before checking again
            await asyncio.sleep(5)
    
    def _prepare_task_input(self, 
                          task: TaskConfig,
                          input_data: Dict[str, Any],
                          previous_outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare input data for a task based on dependencies."""
        task_input = input_data.copy()
        
        # Add outputs from dependencies
        for dep in task.dependencies:
            if dep in previous_outputs:
                task_input[f"{dep}_output"] = previous_outputs[dep]
        
        # Merge with task-specific parameters
        task_input.update(task.parameters)
        
        return task_input
    
    def _aggregate_outputs(self, 
                         task_outputs: Dict[str, Any],
                         pipeline_config: PipelineConfig) -> Dict[str, Any]:
        """Aggregate task outputs into final pipeline output."""
        # Simple aggregation - can be customized
        aggregated = {
            "task_outputs": task_outputs,
            "pipeline_metadata": {
                "name": pipeline_config.name,
                "version": pipeline_config.version,
                "completed_at": datetime.utcnow().isoformat()
            }
        }
        
        # Apply any global transformations
        if "output_mapping" in pipeline_config.global_parameters:
            mapping = pipeline_config.global_parameters["output_mapping"]
            mapped_output = {}
            
            for key, path in mapping.items():
                # Navigate through task outputs
                value = task_outputs
                for part in path.split("."):
                    value = value.get(part, {})
                mapped_output[key] = value
            
            aggregated["mapped_output"] = mapped_output
        
        return aggregated
    
    def _generate_cache_key(self, pipeline_name: str, input_data: Dict[str, Any]) -> str:
        """Generate cache key for pipeline results."""
        import hashlib
        data_str = json.dumps(input_data, sort_keys=True)
        data_hash = hashlib.md5(data_str.encode()).hexdigest()
        return f"pipeline:{pipeline_name}:{data_hash}"
    
    def _generate_task_cache_key(self, 
                               task_name: str,
                               input_data: Dict[str, Any],
                               previous_outputs: Dict[str, Any]) -> str:
        """Generate cache key for task results."""
        import hashlib
        combined_data = {
            "input": input_data,
            "dependencies": previous_outputs
        }
        data_str = json.dumps(combined_data, sort_keys=True)
        data_hash = hashlib.md5(data_str.encode()).hexdigest()
        return f"task:{task_name}:{data_hash}"
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a pipeline execution."""
        execution = self._execution_store.get(execution_id)
        if not execution:
            return None
        
        return {
            "id": execution.id,
            "pipeline": execution.pipeline_name,
            "status": execution.status,
            "started_at": execution.started_at,
            "completed_at": execution.completed_at,
            "task_results": execution.task_results,
            "output_data": execution.output_data,
            "error": execution.error
        }
    
    def pause_execution(self, execution_id: str) -> bool:
        """Pause a running pipeline execution."""
        execution = self._execution_store.get(execution_id)
        if not execution or execution.status != PipelineStatus.RUNNING:
            return False
        
        execution.status = PipelineStatus.PAUSED
        self.monitor.update_execution_status(execution_id, PipelineStatus.PAUSED)
        logger.info(f"Paused pipeline execution: {execution_id}")
        return True
    
    def resume_execution(self, execution_id: str) -> bool:
        """Resume a paused pipeline execution."""
        execution = self._execution_store.get(execution_id)
        if not execution or execution.status != PipelineStatus.PAUSED:
            return False
        
        execution.status = PipelineStatus.RUNNING
        self.monitor.update_execution_status(execution_id, PipelineStatus.RUNNING)
        logger.info(f"Resumed pipeline execution: {execution_id}")
        return True
    
    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a pipeline execution."""
        execution = self._execution_store.get(execution_id)
        if not execution:
            return False
        
        execution.status = PipelineStatus.CANCELLED
        execution.completed_at = datetime.utcnow()
        self.monitor.complete_execution(execution_id, PipelineStatus.CANCELLED)
        
        # Cancel any running tasks
        for task_name, result in execution.task_results.items():
            if "task_id" in result:
                self.task_manager.cancel_task(result["task_id"])
        
        logger.info(f"Cancelled pipeline execution: {execution_id}")
        return True
    
    def add_completion_callback(self, callback: Callable):
        """Add a callback for pipeline completion."""
        self._completion_callbacks.append(callback)
    
    def add_error_callback(self, callback: Callable):
        """Add a callback for pipeline errors."""
        self._error_callbacks.append(callback)
    
    def add_progress_callback(self, callback: Callable):
        """Add a callback for pipeline progress updates."""
        self._progress_callbacks.append(callback)
    
    def _notify_completion(self, execution: PipelineExecution):
        """Notify completion callbacks."""
        for callback in self._completion_callbacks:
            try:
                callback(execution)
            except Exception as e:
                logger.error(f"Error in completion callback: {str(e)}")
    
    def _handle_failure(self, execution: PipelineExecution):
        """Handle pipeline failure."""
        self.monitor.complete_execution(execution.id, PipelineStatus.FAILED)
        
        for callback in self._error_callbacks:
            try:
                callback(execution)
            except Exception as e:
                logger.error(f"Error in error callback: {str(e)}")
    
    def _notify_progress(self, execution_id: str, message: str, progress: float):
        """Notify progress callbacks."""
        for callback in self._progress_callbacks:
            try:
                callback(execution_id, message, progress)
            except Exception as e:
                logger.error(f"Error in progress callback: {str(e)}")