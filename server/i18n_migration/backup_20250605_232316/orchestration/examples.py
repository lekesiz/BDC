"""Examples and usage demonstrations for the AI pipeline orchestration system."""

import asyncio
import redis
from celery import Celery
from datetime import timedelta

from .orchestrator import PipelineOrchestrator
from .pipeline import Pipeline, PipelineConfig
from .versioning import ModelVersionManager, ModelVersion
from .human_loop import HumanInLoopManager, ReviewerProfile, ReviewPriority
from .cache import ResultCache
from .monitoring import PipelineMonitor, AlertRule, AlertSeverity
from .config import OrchestrationConfig, get_example_config


class OrchestrationSystemExample:
    """Complete example of using the AI pipeline orchestration system."""
    
    def __init__(self):
        """Initialize the orchestration system with all components."""
        # Load configuration
        self.config = OrchestrationConfig.from_env()
        
        # Initialize Redis
        self.redis_client = redis.Redis(
            host=self.config.redis_host,
            port=self.config.redis_port,
            db=self.config.redis_db,
            password=self.config.redis_password,
            decode_responses=False
        )
        
        # Initialize Celery
        self.celery_app = Celery(
            'bdc_orchestration',
            broker=self.config.celery_broker_url,
            backend=self.config.celery_result_backend
        )
        
        # Configure Celery
        self.celery_app.conf.update(
            task_serializer='json',
            accept_content=['json'],
            result_serializer='json',
            timezone='UTC',
            enable_utc=True,
            worker_concurrency=self.config.celery_worker_concurrency,
            task_time_limit=self.config.celery_task_timeout
        )
        
        # Initialize orchestrator
        self.orchestrator = PipelineOrchestrator(
            celery_app=self.celery_app,
            redis_client=self.redis_client,
            model_registry_path=self.config.model_registry_path,
            cache_ttl=self.config.cache_default_ttl
        )
        
        print("✅ Orchestration system initialized successfully!")
    
    async def run_complete_example(self):
        """Run a complete example showcasing all features."""
        print("\n🚀 Starting comprehensive AI pipeline orchestration example...\n")
        
        # 1. Setup model versions
        await self.setup_model_versions()
        
        # 2. Setup human reviewers
        await self.setup_human_reviewers()
        
        # 3. Create and register pipelines
        await self.create_pipelines()
        
        # 4. Setup monitoring and alerts
        await self.setup_monitoring()
        
        # 5. Execute pipelines
        await self.execute_pipelines()
        
        # 6. Demonstrate human-in-the-loop
        await self.demonstrate_human_loop()
        
        # 7. Show caching benefits
        await self.demonstrate_caching()
        
        # 8. Display monitoring results
        await self.display_monitoring_results()
        
        print("\n🎉 Complete example finished successfully!")
    
    async def setup_model_versions(self):
        """Setup model versions in the registry."""
        print("📦 Setting up model versions...")
        
        version_manager = self.orchestrator.version_manager
        
        # Register different model versions
        models_to_register = [
            {
                "name": "gpt-4",
                "version": "latest",
                "path": "/tmp/mock_gpt4_model",
                "metadata": {
                    "description": "GPT-4 language model",
                    "capabilities": ["text_generation", "extraction"],
                    "max_tokens": 8192,
                    "cost_per_token": 0.00003
                },
                "tags": ["text-generation", "production"],
                "set_as_default": True
            },
            {
                "name": "bert-base-uncased",
                "version": "v1.0",
                "path": "/tmp/mock_bert_model",
                "metadata": {
                    "description": "BERT base model for classification",
                    "capabilities": ["classification"],
                    "max_sequence_length": 512
                },
                "tags": ["classification", "production"]
            },
            {
                "name": "gpt-3.5-turbo",
                "version": "v1.0",
                "path": "/tmp/mock_gpt35_model",
                "metadata": {
                    "description": "GPT-3.5 Turbo model",
                    "capabilities": ["text_generation"],
                    "max_tokens": 4096,
                    "cost_per_token": 0.000015
                },
                "tags": ["text-generation", "cost-effective"]
            }
        ]
        
        # Create mock model files
        import os
        for model_info in models_to_register:
            model_path = model_info["path"]
            os.makedirs(model_path, exist_ok=True)
            with open(f"{model_path}/model.bin", "w") as f:
                f.write(f"Mock model data for {model_info['name']}")
        
        # Register models
        for model_info in models_to_register:
            try:
                model_version = version_manager.register_model(
                    model_name=model_info["name"],
                    version=model_info["version"],
                    model_path=model_info["path"],
                    metadata=model_info["metadata"],
                    tags=model_info["tags"],
                    set_as_default=model_info.get("set_as_default", False)
                )
                print(f"  ✅ Registered {model_info['name']} v{model_info['version']}")
            except Exception as e:
                print(f"  ❌ Failed to register {model_info['name']}: {str(e)}")
        
        # Show registered models
        print(f"  📋 Total models registered: {len(version_manager.list_models())}")
        
    async def setup_human_reviewers(self):
        """Setup human reviewers for HITL workflows."""
        print("\n👥 Setting up human reviewers...")
        
        hitl_manager = self.orchestrator.human_loop_manager
        
        reviewers = [
            ReviewerProfile(
                id="reviewer_001",
                name="Alice Johnson",
                email="alice@example.com",
                specializations=["legal", "financial"],
                max_concurrent_reviews=3,
                preferences={"notification_email": True}
            ),
            ReviewerProfile(
                id="reviewer_002",
                name="Bob Smith",
                email="bob@example.com",
                specializations=["technical", "classification"],
                max_concurrent_reviews=5,
                preferences={"notification_slack": True}
            ),
            ReviewerProfile(
                id="reviewer_003",
                name="Carol Davis",
                email="carol@example.com",
                specializations=["validation", "extraction"],
                max_concurrent_reviews=2,
                preferences={"priority_urgent_only": True}
            )
        ]
        
        for reviewer in reviewers:
            hitl_manager.register_reviewer(reviewer)
            print(f"  ✅ Registered reviewer: {reviewer.name} ({reviewer.id})")
        
        print(f"  👥 Total reviewers registered: {len(reviewers)}")
    
    async def create_pipelines(self):
        """Create and register pipelines."""
        print("\n🔧 Creating and registering pipelines...")
        
        # Create document processing pipeline
        doc_config = get_example_config("document_processing")
        doc_pipeline = Pipeline(PipelineConfig(**doc_config))
        doc_pipeline_id = self.orchestrator.register_pipeline(doc_pipeline, "document_processing")
        print(f"  ✅ Registered pipeline: {doc_pipeline_id}")
        print(f"     Tasks: {len(doc_pipeline.config.tasks)}")
        print(f"     Execution order: {len(doc_pipeline.get_execution_order())} stages")
        
        # Create content generation pipeline
        content_config = get_example_config("content_generation")
        content_pipeline = Pipeline(PipelineConfig(**content_config))
        content_pipeline_id = self.orchestrator.register_pipeline(content_pipeline, "content_generation")
        print(f"  ✅ Registered pipeline: {content_pipeline_id}")
        print(f"     Tasks: {len(content_pipeline.config.tasks)}")
        
        # Create a custom pipeline for testing
        custom_config = {
            "name": "data_analysis",
            "description": "Analyze and summarize data",
            "version": "1.0.0",
            "tasks": [
                {
                    "name": "load_data",
                    "type": "custom",
                    "parameters": {
                        "handler": "app.services.ai.orchestration.examples.custom_data_loader"
                    },
                    "dependencies": [],
                    "timeout": 120,
                    "cache_enabled": True
                },
                {
                    "name": "analyze_data",
                    "type": "text_generation",
                    "model": "gpt-4",
                    "parameters": {
                        "prompt_template": "Analyze the following data and provide insights: {load_data_output}",
                        "max_tokens": 1000
                    },
                    "dependencies": ["load_data"],
                    "timeout": 300,
                    "cache_enabled": True
                }
            ],
            "cache_ttl": 1800,
            "max_parallel_tasks": 2
        }
        
        custom_pipeline = Pipeline(PipelineConfig(**custom_config))
        custom_pipeline_id = self.orchestrator.register_pipeline(custom_pipeline, "data_analysis")
        print(f"  ✅ Registered pipeline: {custom_pipeline_id}")
        
        print(f"  📊 Total pipelines registered: 3")
    
    async def setup_monitoring(self):
        """Setup monitoring and alert rules."""
        print("\n📊 Setting up monitoring and alerts...")
        
        monitor = self.orchestrator.monitor
        
        # Add custom alert rules
        custom_rules = [
            AlertRule(
                name="Very High Error Rate",
                metric_name="error_rate",
                operator=">",
                threshold=0.5,  # 50%
                severity=AlertSeverity.CRITICAL,
                message_template="CRITICAL: Pipeline {pipeline} has very high error rate: {current_value:.2%}",
                cooldown_minutes=15
            ),
            AlertRule(
                name="Execution Timeout",
                metric_name="max_execution_time",
                operator=">",
                threshold=1800,  # 30 minutes
                severity=AlertSeverity.WARNING,
                message_template="Pipeline {pipeline} has long execution time: {current_value:.1f}s",
                cooldown_minutes=60
            ),
            AlertRule(
                name="No Recent Executions",
                metric_name="execution_count",
                operator="==",
                threshold=0,
                severity=AlertSeverity.INFO,
                message_template="Pipeline {pipeline} has no recent executions",
                cooldown_minutes=120
            )
        ]
        
        for rule in custom_rules:
            monitor.add_alert_rule("*", rule)  # Apply to all pipelines
            print(f"  ✅ Added alert rule: {rule.name}")
        
        # Add event handler for alerts
        def alert_handler(event_type, data):
            if event_type == "alert_triggered":
                print(f"  🚨 ALERT: {data['message']}")
        
        monitor.add_event_handler(alert_handler)
        print(f"  📢 Added alert event handler")
    
    async def execute_pipelines(self):
        """Execute pipelines with different scenarios."""
        print("\n⚡ Executing pipelines...")
        
        # Execute document processing pipeline
        doc_input = {
            "document": {
                "content": "This is a sample legal document about contract terms and conditions. It contains important clauses about liability and termination procedures.",
                "metadata": {
                    "source": "legal_dept",
                    "uploaded_by": "user123"
                }
            },
            "prompt": "Extract key information from this document"
        }
        
        doc_execution_id = await self.orchestrator.execute_pipeline(
            "document_processing",
            doc_input
        )
        print(f"  ⏳ Started document processing: {doc_execution_id}")
        
        # Execute content generation pipeline
        content_input = {
            "prompt": "Write a comprehensive guide about AI pipeline orchestration",
            "requirements": {
                "tone": "professional",
                "length": "medium",
                "audience": "technical"
            }
        }
        
        content_execution_id = await self.orchestrator.execute_pipeline(
            "content_generation",
            content_input
        )
        print(f"  ⏳ Started content generation: {content_execution_id}")
        
        # Execute data analysis pipeline
        data_input = {
            "data_source": "sales_data.csv",
            "analysis_type": "trend_analysis",
            "time_period": "last_quarter"
        }
        
        data_execution_id = await self.orchestrator.execute_pipeline(
            "data_analysis",
            data_input
        )
        print(f"  ⏳ Started data analysis: {data_execution_id}")
        
        # Wait a bit for executions to start
        await asyncio.sleep(2)
        
        # Show execution status
        print("\n  📋 Execution Status:")
        for exec_id, name in [
            (doc_execution_id, "Document Processing"),
            (content_execution_id, "Content Generation"),
            (data_execution_id, "Data Analysis")
        ]:
            status = self.orchestrator.get_execution_status(exec_id)
            if status:
                print(f"    {name}: {status['status']}")
            else:
                print(f"    {name}: Not found")
        
        return {
            "document_processing": doc_execution_id,
            "content_generation": content_execution_id,
            "data_analysis": data_execution_id
        }
    
    async def demonstrate_human_loop(self):
        """Demonstrate human-in-the-loop workflow."""
        print("\n👤 Demonstrating Human-in-the-Loop workflow...")
        
        hitl_manager = self.orchestrator.human_loop_manager
        
        # Create a review request
        review_id = hitl_manager.create_review(
            task_name="document_validation",
            task_type="validation",
            input_data={
                "document_title": "Sample Contract",
                "extracted_entities": ["Company A", "Company B", "2024-01-01"],
                "confidence_scores": [0.95, 0.88, 0.92]
            },
            priority=ReviewPriority.HIGH,
            timeout=timedelta(hours=2),
            metadata={
                "requester": "system",
                "urgency": "business_critical"
            }
        )
        
        print(f"  📝 Created review request: {review_id}")
        
        # List pending reviews
        pending_reviews = hitl_manager.list_pending_reviews()
        print(f"  📋 Pending reviews: {len(pending_reviews)}")
        
        # Simulate reviewer assignment
        if pending_reviews:
            review = pending_reviews[0]
            assigned = hitl_manager.assign_review(review["id"], "reviewer_001")
            if assigned:
                print(f"  ✅ Assigned review to reviewer_001")
                
                # Simulate review completion
                review_result = {
                    "validation_result": "approved",
                    "corrections": [],
                    "confidence": 0.95,
                    "reviewer_notes": "All extracted entities look accurate"
                }
                
                completed = hitl_manager.complete_review(
                    review["id"],
                    "reviewer_001",
                    review_result,
                    feedback="Quick and accurate extraction"
                )
                
                if completed:
                    print(f"  ✅ Review completed successfully")
        
        # Show reviewer workload
        workload = hitl_manager.get_reviewer_workload("reviewer_001")
        print(f"  👥 Reviewer workload: {workload.get('current_reviews_count', 0)} active reviews")
    
    async def demonstrate_caching(self):
        """Demonstrate caching capabilities."""
        print("\n💾 Demonstrating caching capabilities...")
        
        cache = self.orchestrator.cache
        
        # Test basic caching
        test_data = {
            "result": "This is a cached result",
            "computation_time": 123.45,
            "metadata": {"model": "gpt-4", "tokens": 150}
        }
        
        cache_key = {"pipeline": "test", "input_hash": "abc123"}
        
        # Set cache
        cached = cache.set(cache_key, test_data, ttl=300, tags=["test", "demo"])
        print(f"  💾 Cached data: {cached}")
        
        # Get from cache
        retrieved = cache.get(cache_key)
        print(f"  📖 Retrieved from cache: {retrieved is not None}")
        
        # Test cache stats
        stats = cache.get_stats()
        print(f"  📊 Cache stats:")
        print(f"    Hit rate: {stats['hit_rate']:.2%}")
        print(f"    Total entries: {stats['entry_count']}")
        print(f"    Total size: {stats['total_size']} bytes")
        
        # Test cache optimization
        optimization_result = cache.optimize()
        print(f"  🔧 Cache optimization:")
        print(f"    Cleaned expired: {optimization_result['cleaned_expired']}")
        print(f"    Total entries: {optimization_result['total_entries']}")
    
    async def display_monitoring_results(self):
        """Display monitoring and system health information."""
        print("\n📈 System Health and Monitoring Results...")
        
        monitor = self.orchestrator.monitor
        
        # Get system health
        health = monitor.get_system_health()
        print(f"  🏥 System Health:")
        print(f"    Total pipelines: {health['total_pipelines']}")
        print(f"    Active pipelines: {health['active_pipelines']}")
        print(f"    Total executions: {health['total_executions']}")
        print(f"    Success rate: {health['overall_success_rate']:.2%}")
        print(f"    Active alerts: {health['active_alerts']}")
        
        # Get pipeline metrics
        all_metrics = monitor.get_all_metrics()
        print(f"\n  📊 Pipeline Metrics:")
        for pipeline_id, metrics in all_metrics.items():
            if metrics['execution_count'] > 0:
                print(f"    {pipeline_id}:")
                print(f"      Executions: {metrics['execution_count']}")
                print(f"      Success rate: {metrics['success_rate']:.2%}")
                print(f"      Avg execution time: {metrics['average_execution_time']:.1f}s")
        
        # Get active alerts
        alerts = monitor.get_active_alerts()
        if alerts:
            print(f"\n  🚨 Active Alerts ({len(alerts)}):")
            for alert in alerts[:3]:  # Show first 3
                print(f"    {alert['severity']}: {alert['message']}")
        else:
            print(f"\n  ✅ No active alerts")
        
        # Get execution history
        history = monitor.get_execution_history(limit=5)
        print(f"\n  📝 Recent Executions ({len(history)}):")
        for execution in history:
            status_emoji = "✅" if execution.get("status") == "completed" else "❌" if execution.get("status") == "failed" else "⏳"
            print(f"    {status_emoji} {execution.get('pipeline_id', 'Unknown')} - {execution.get('status', 'Unknown')}")


# Custom task handler example
def custom_data_loader(task_config, input_data, context):
    """Example custom task handler for data loading."""
    import random
    import time
    
    # Simulate data loading
    time.sleep(1)
    
    data_source = input_data.get("data_source", "default.csv")
    analysis_type = input_data.get("analysis_type", "basic")
    
    # Mock data generation
    mock_data = {
        "records_count": random.randint(1000, 10000),
        "columns": ["date", "sales", "region", "product"],
        "summary_stats": {
            "total_sales": random.randint(100000, 1000000),
            "avg_daily_sales": random.randint(1000, 5000),
            "top_region": random.choice(["North", "South", "East", "West"])
        },
        "data_quality": {
            "completeness": random.uniform(0.9, 1.0),
            "accuracy": random.uniform(0.85, 0.98)
        }
    }
    
    return {
        "loaded_data": mock_data,
        "source": data_source,
        "analysis_type": analysis_type,
        "load_time": time.time()
    }


async def main():
    """Run the comprehensive example."""
    try:
        example = OrchestrationSystemExample()
        await example.run_complete_example()
    except Exception as e:
        print(f"❌ Error running example: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())