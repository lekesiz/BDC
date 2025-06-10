"""Configuration management for AI pipeline orchestration."""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class OrchestrationConfig:
    """Configuration for the orchestration system."""
    
    # Redis configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # Celery configuration
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    celery_worker_concurrency: int = 4
    celery_task_timeout: int = 3600
    
    # Model registry
    model_registry_path: str = "/tmp/bdc_model_registry"
    
    # Cache configuration
    cache_default_ttl: int = 3600
    cache_max_size: int = 1000000  # 1MB
    cache_strategy: str = "lru"
    cache_compression: str = "json"
    
    # Monitoring configuration
    monitoring_enabled: bool = True
    metrics_retention_days: int = 7
    alerts_retention_days: int = 30
    
    # Human-in-the-loop configuration
    hitl_default_timeout_hours: int = 24
    hitl_reminder_intervals: list = None
    
    # Pipeline execution
    max_parallel_tasks: int = 5
    default_task_timeout: int = 300
    default_retry_count: int = 3
    
    def __post_init__(self):
        """Initialize default values that require computation."""
        if self.hitl_reminder_intervals is None:
            self.hitl_reminder_intervals = [4, 12]  # hours
    
    @classmethod
    def from_env(cls) -> 'OrchestrationConfig':
        """Create configuration from environment variables."""
        return cls(
            redis_host=os.getenv("REDIS_HOST", "localhost"),
            redis_port=int(os.getenv("REDIS_PORT", "6379")),
            redis_db=int(os.getenv("REDIS_DB", "0")),
            redis_password=os.getenv("REDIS_PASSWORD"),
            
            celery_broker_url=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1"),
            celery_result_backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2"),
            celery_worker_concurrency=int(os.getenv("CELERY_WORKER_CONCURRENCY", "4")),
            celery_task_timeout=int(os.getenv("CELERY_TASK_TIMEOUT", "3600")),
            
            model_registry_path=os.getenv("MODEL_REGISTRY_PATH", "/tmp/bdc_model_registry"),
            
            cache_default_ttl=int(os.getenv("CACHE_DEFAULT_TTL", "3600")),
            cache_max_size=int(os.getenv("CACHE_MAX_SIZE", "1000000")),
            cache_strategy=os.getenv("CACHE_STRATEGY", "lru"),
            cache_compression=os.getenv("CACHE_COMPRESSION", "json"),
            
            monitoring_enabled=os.getenv("MONITORING_ENABLED", "true").lower() == "true",
            metrics_retention_days=int(os.getenv("METRICS_RETENTION_DAYS", "7")),
            alerts_retention_days=int(os.getenv("ALERTS_RETENTION_DAYS", "30")),
            
            hitl_default_timeout_hours=int(os.getenv("HITL_DEFAULT_TIMEOUT_HOURS", "24")),
            
            max_parallel_tasks=int(os.getenv("MAX_PARALLEL_TASKS", "5")),
            default_task_timeout=int(os.getenv("DEFAULT_TASK_TIMEOUT", "300")),
            default_retry_count=int(os.getenv("DEFAULT_RETRY_COUNT", "3"))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "redis": {
                "host": self.redis_host,
                "port": self.redis_port,
                "db": self.redis_db,
                "password": self.redis_password
            },
            "celery": {
                "broker_url": self.celery_broker_url,
                "result_backend": self.celery_result_backend,
                "worker_concurrency": self.celery_worker_concurrency,
                "task_timeout": self.celery_task_timeout
            },
            "model_registry": {
                "path": self.model_registry_path
            },
            "cache": {
                "default_ttl": self.cache_default_ttl,
                "max_size": self.cache_max_size,
                "strategy": self.cache_strategy,
                "compression": self.cache_compression
            },
            "monitoring": {
                "enabled": self.monitoring_enabled,
                "metrics_retention_days": self.metrics_retention_days,
                "alerts_retention_days": self.alerts_retention_days
            },
            "hitl": {
                "default_timeout_hours": self.hitl_default_timeout_hours,
                "reminder_intervals": self.hitl_reminder_intervals
            },
            "execution": {
                "max_parallel_tasks": self.max_parallel_tasks,
                "default_task_timeout": self.default_task_timeout,
                "default_retry_count": self.default_retry_count
            }
        }


# Example pipeline configurations
EXAMPLE_PIPELINE_CONFIGS = {
    "document_processing": {
        "name": "document_processing",
        "description": "Extract and classify information from documents",
        "version": "1.0.0",
        "tasks": [
            {
                "name": "extract_text",
                "type": "extraction",
                "model": "gpt-4",
                "model_version": "latest",
                "parameters": {
                    "schema": {
                        "title": "string",
                        "content": "string",
                        "author": "string",
                        "date": "date"
                    }
                },
                "dependencies": [],
                "timeout": 300,
                "retries": 3,
                "cache_enabled": True
            },
            {
                "name": "classify_document",
                "type": "classification",
                "model": "bert-base-uncased",
                "parameters": {
                    "categories": ["legal", "financial", "technical", "other"]
                },
                "dependencies": ["extract_text"],
                "timeout": 120,
                "retries": 2,
                "cache_enabled": True
            },
            {
                "name": "validate_extraction",
                "type": "validation",
                "parameters": {
                    "rules": [
                        {
                            "type": "required",
                            "field": "extract_text_output.title",
                            "value": None
                        },
                        {
                            "type": "required",
                            "field": "extract_text_output.content",
                            "value": None
                        }
                    ]
                },
                "dependencies": ["extract_text"],
                "timeout": 60,
                "retries": 1,
                "cache_enabled": False
            },
            {
                "name": "human_review",
                "type": "human_review",
                "parameters": {
                    "review_criteria": ["accuracy", "completeness"]
                },
                "dependencies": ["classify_document", "validate_extraction"],
                "timeout": 86400,  # 24 hours
                "retries": 0,
                "cache_enabled": False,
                "human_review_required": True,
                "human_review_threshold": 0.8
            }
        ],
        "global_parameters": {
            "output_mapping": {
                "document_title": "extract_text_output.title",
                "document_category": "classify_document_output.category",
                "confidence_score": "classify_document_output.confidence",
                "review_status": "human_review_output.status"
            }
        },
        "cache_ttl": 7200,
        "max_parallel_tasks": 3,
        "enable_monitoring": True,
        "notification_channels": ["email", "slack"]
    },
    
    "content_generation": {
        "name": "content_generation",
        "description": "Generate and refine content based on input prompts",
        "version": "1.0.0",
        "tasks": [
            {
                "name": "generate_draft",
                "type": "text_generation",
                "model": "gpt-4",
                "parameters": {
                    "max_tokens": 2000,
                    "temperature": 0.7
                },
                "dependencies": [],
                "timeout": 300,
                "retries": 3,
                "cache_enabled": True
            },
            {
                "name": "validate_content",
                "type": "validation",
                "parameters": {
                    "rules": [
                        {
                            "type": "range",
                            "field": "generate_draft_output.generated_text",
                            "value": [100, 5000]  # Character length range
                        }
                    ]
                },
                "dependencies": ["generate_draft"],
                "timeout": 60,
                "retries": 1,
                "cache_enabled": False
            },
            {
                "name": "refine_content",
                "type": "text_generation",
                "model": "gpt-4",
                "parameters": {
                    "prompt_template": "Please refine and improve the following content: {generate_draft_output.generated_text}",
                    "max_tokens": 2000,
                    "temperature": 0.5
                },
                "dependencies": ["generate_draft", "validate_content"],
                "timeout": 300,
                "retries": 2,
                "cache_enabled": True
            }
        ],
        "global_parameters": {
            "output_mapping": {
                "final_content": "refine_content_output.generated_text",
                "word_count": "refine_content_output.usage.total_tokens"
            }
        },
        "cache_ttl": 3600,
        "max_parallel_tasks": 2,
        "enable_monitoring": True
    }
}


def get_example_config(name: str) -> Optional[Dict[str, Any]]:
    """Get an example pipeline configuration by name."""
    return EXAMPLE_PIPELINE_CONFIGS.get(name)


def list_example_configs() -> list:
    """List all available example configurations."""
    return list(EXAMPLE_PIPELINE_CONFIGS.keys())