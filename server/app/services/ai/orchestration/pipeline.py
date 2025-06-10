"""Pipeline definition and configuration module."""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import uuid
import yaml
import json


class PipelineStatus(str, Enum):
    """Pipeline execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class TaskType(str, Enum):
    """Types of tasks in pipeline."""
    TEXT_GENERATION = "text_generation"
    CLASSIFICATION = "classification"
    EXTRACTION = "extraction"
    VALIDATION = "validation"
    HUMAN_REVIEW = "human_review"
    CUSTOM = "custom"


class TaskConfig(BaseModel):
    """Configuration for a pipeline task."""
    name: str
    type: TaskType
    model: Optional[str] = None
    model_version: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    timeout: Optional[int] = 300  # seconds
    retries: int = 3
    cache_enabled: bool = True
    human_review_required: bool = False
    human_review_threshold: Optional[float] = None


class PipelineConfig(BaseModel):
    """Configuration for an AI pipeline."""
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    tasks: List[TaskConfig]
    global_parameters: Dict[str, Any] = Field(default_factory=dict)
    cache_ttl: int = 3600  # seconds
    max_parallel_tasks: int = 5
    enable_monitoring: bool = True
    notification_channels: List[str] = Field(default_factory=list)
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'PipelineConfig':
        """Load pipeline configuration from YAML file."""
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_path: str) -> 'PipelineConfig':
        """Load pipeline configuration from JSON file."""
        with open(json_path, 'r') as f:
            data = json.load(f)
        return cls(**data)
    
    def to_yaml(self, yaml_path: str) -> None:
        """Save pipeline configuration to YAML file."""
        with open(yaml_path, 'w') as f:
            yaml.dump(self.dict(), f, default_flow_style=False)
    
    def to_json(self, json_path: str) -> None:
        """Save pipeline configuration to JSON file."""
        with open(json_path, 'w') as f:
            json.dump(self.dict(), f, indent=2)


class PipelineExecution(BaseModel):
    """Represents a pipeline execution instance."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pipeline_name: str
    pipeline_version: str
    status: PipelineStatus = PipelineStatus.PENDING
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    task_results: Dict[str, Any] = Field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Pipeline:
    """AI Pipeline definition and management."""
    
    def __init__(self, config: Union[PipelineConfig, str, dict]):
        """Initialize pipeline with configuration."""
        if isinstance(config, str):
            # Assume it's a file path
            if config.endswith('.yaml') or config.endswith('.yml'):
                self.config = PipelineConfig.from_yaml(config)
            elif config.endswith('.json'):
                self.config = PipelineConfig.from_json(config)
            else:
                raise ValueError(f"Unsupported configuration file format: {config}")
        elif isinstance(config, dict):
            self.config = PipelineConfig(**config)
        else:
            self.config = config
        
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate pipeline configuration."""
        # Check for circular dependencies
        task_names = {task.name for task in self.config.tasks}
        for task in self.config.tasks:
            for dep in task.dependencies:
                if dep not in task_names:
                    raise ValueError(f"Task '{task.name}' has unknown dependency '{dep}'")
        
        # Check for duplicate task names
        if len(task_names) != len(self.config.tasks):
            raise ValueError("Duplicate task names found in pipeline configuration")
    
    def get_execution_order(self) -> List[List[TaskConfig]]:
        """Get tasks organized by execution order (topological sort)."""
        # Build dependency graph
        graph = {task.name: set(task.dependencies) for task in self.config.tasks}
        task_map = {task.name: task for task in self.config.tasks}
        
        # Kahn's algorithm for topological sort
        in_degree = {task: len(deps) for task, deps in graph.items()}
        queue = [task for task, degree in in_degree.items() if degree == 0]
        execution_order = []
        
        while queue:
            # Get all tasks that can be executed in parallel
            current_level = []
            next_queue = []
            
            for task in queue:
                current_level.append(task_map[task])
                
                # Update in-degrees
                for other_task, deps in graph.items():
                    if task in deps:
                        in_degree[other_task] -= 1
                        if in_degree[other_task] == 0:
                            next_queue.append(other_task)
            
            execution_order.append(current_level)
            queue = next_queue
        
        # Check for cycles
        if sum(len(level) for level in execution_order) != len(self.config.tasks):
            raise ValueError("Circular dependency detected in pipeline")
        
        return execution_order
    
    def create_execution(self, input_data: Dict[str, Any]) -> PipelineExecution:
        """Create a new pipeline execution instance."""
        return PipelineExecution(
            pipeline_name=self.config.name,
            pipeline_version=self.config.version,
            input_data=input_data,
            metadata={
                "description": self.config.description,
                "tasks_count": len(self.config.tasks),
                "cache_ttl": self.config.cache_ttl,
                "max_parallel_tasks": self.config.max_parallel_tasks
            }
        )
    
    def get_task_by_name(self, task_name: str) -> Optional[TaskConfig]:
        """Get task configuration by name."""
        for task in self.config.tasks:
            if task.name == task_name:
                return task
        return None
    
    def add_task(self, task: TaskConfig) -> None:
        """Add a new task to the pipeline."""
        # Validate task
        for dep in task.dependencies:
            if not self.get_task_by_name(dep):
                raise ValueError(f"Dependency '{dep}' not found in pipeline")
        
        # Check for duplicate name
        if self.get_task_by_name(task.name):
            raise ValueError(f"Task with name '{task.name}' already exists")
        
        self.config.tasks.append(task)
    
    def remove_task(self, task_name: str) -> None:
        """Remove a task from the pipeline."""
        # Check if any other task depends on this
        for task in self.config.tasks:
            if task_name in task.dependencies:
                raise ValueError(f"Cannot remove task '{task_name}': task '{task.name}' depends on it")
        
        # Remove the task
        self.config.tasks = [t for t in self.config.tasks if t.name != task_name]
    
    def update_task(self, task_name: str, updates: Dict[str, Any]) -> None:
        """Update task configuration."""
        task = self.get_task_by_name(task_name)
        if not task:
            raise ValueError(f"Task '{task_name}' not found")
        
        # Update task fields
        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        # Revalidate configuration
        self._validate_config()
    
    def visualize(self) -> str:
        """Generate a text representation of the pipeline."""
        lines = [f"Pipeline: {self.config.name} (v{self.config.version})"]
        if self.config.description:
            lines.append(f"Description: {self.config.description}")
        lines.append("")
        
        execution_order = self.get_execution_order()
        for i, level in enumerate(execution_order):
            lines.append(f"Stage {i + 1}:")
            for task in level:
                deps = f" <- {', '.join(task.dependencies)}" if task.dependencies else ""
                lines.append(f"  - {task.name} ({task.type.value}){deps}")
        
        return "\n".join(lines)