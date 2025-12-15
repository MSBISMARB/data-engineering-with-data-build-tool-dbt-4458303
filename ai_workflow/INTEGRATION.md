# Integration Guide: AI Workflow with SaaS Applications

This guide explains how to integrate the AI Workflow system into your SaaS application.

## Architecture Overview

```
┌─────────────────┐
│   Your SaaS     │
│   Application   │
└────────┬────────┘
         │
         ↓
┌─────────────────┐      ┌──────────────┐
│  AI Workflow    │ ←──→ │    Notion    │
│   Orchestrator  │      │   Database   │
└────────┬────────┘      └──────────────┘
         │
         ↓
┌─────────────────┐
│   OpenAI API    │
└─────────────────┘
```

## Integration Methods

### 1. Python Library Integration (Recommended)

Import and use the orchestrator directly in your application:

```python
from ai_workflow.src.orchestrator import WorkflowOrchestrator

class MyApplication:
    def __init__(self):
        self.workflow_orchestrator = WorkflowOrchestrator(
            notion_api_key=os.getenv("NOTION_API_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            ai_model="gpt-3.5-turbo"
        )
    
    def process_user_request(self, user_id: str, request: str):
        # Create a workflow in Notion programmatically
        # or run pre-configured workflows
        
        results = self.workflow_orchestrator.run_workflows_from_database(
            database_id=self.config.notion_database_id,
            status_filter="Active",
            max_workflows=5
        )
        
        return results
```

### 2. API Wrapper Integration

Create a REST API wrapper around the workflow system:

```python
from flask import Flask, jsonify, request
from ai_workflow.src.orchestrator import WorkflowOrchestrator

app = Flask(__name__)
orchestrator = WorkflowOrchestrator(
    notion_api_key=os.getenv("NOTION_API_KEY"),
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

@app.route('/api/workflows/run', methods=['POST'])
def run_workflows():
    data = request.json
    database_id = data.get('database_id')
    
    results = orchestrator.run_workflows_from_database(
        database_id=database_id,
        status_filter=data.get('status', 'Active')
    )
    
    return jsonify(results)

@app.route('/api/workflows/validate', methods=['GET'])
def validate():
    validation = orchestrator.validate_setup()
    return jsonify(validation)
```

### 3. Webhook Integration

Set up webhooks to trigger workflows based on events:

```python
from ai_workflow.src.orchestrator import WorkflowOrchestrator

def handle_webhook(event_type: str, payload: dict):
    """Handle incoming webhook events."""
    
    orchestrator = WorkflowOrchestrator(
        notion_api_key=os.getenv("NOTION_API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Map event to workflow
    workflow_mapping = {
        "user.signup": "welcome_email_workflow",
        "order.created": "order_confirmation_workflow",
        "support.ticket": "auto_response_workflow"
    }
    
    workflow_db_id = get_workflow_database_id(workflow_mapping[event_type])
    
    results = orchestrator.run_workflows_from_database(
        database_id=workflow_db_id,
        status_filter="Active"
    )
    
    return results
```

### 4. Background Task Integration

Use with Celery or similar task queue:

```python
from celery import Celery
from ai_workflow.src.orchestrator import WorkflowOrchestrator

celery = Celery('tasks', broker='redis://localhost:6379')

@celery.task
def run_ai_workflows(database_id: str):
    """Background task to run AI workflows."""
    orchestrator = WorkflowOrchestrator(
        notion_api_key=os.getenv("NOTION_API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    results = orchestrator.run_workflows_from_database(
        database_id=database_id,
        status_filter="Active"
    )
    
    # Store results in database
    save_results_to_db(results)
    
    return results

# Schedule periodic execution
@celery.task
def scheduled_workflow_execution():
    """Run every hour."""
    run_ai_workflows.delay(os.getenv("NOTION_DATABASE_ID"))
```

## Use Cases

### 1. Customer Onboarding

```python
def onboard_new_customer(customer_data: dict):
    """Automate customer onboarding with AI."""
    orchestrator = WorkflowOrchestrator()
    
    # Run personalized welcome workflow
    result = orchestrator.run_workflow(
        workflow_id="onboarding_workflow_id",
        workflow_config={
            "Name": "Welcome Email",
            "Prompt": f"Generate a personalized welcome email for {customer_data['name']} "
                     f"in {customer_data['industry']} industry",
            "Temperature": 0.7
        }
    )
    
    # Send email with AI-generated content
    send_email(customer_data['email'], result['response'])
```

### 2. Content Generation

```python
def generate_product_descriptions():
    """Batch generate product descriptions."""
    orchestrator = WorkflowOrchestrator()
    
    # Notion database has one workflow per product
    results = orchestrator.run_workflows_from_database(
        database_id="product_descriptions_db_id",
        status_filter="Pending",
        max_workflows=50
    )
    
    # Update product catalog with generated descriptions
    for result in results:
        if result['success']:
            update_product(result['workflow_id'], result['response'])
```

### 3. Support Automation

```python
def handle_support_ticket(ticket: dict):
    """Auto-respond to support tickets."""
    orchestrator = WorkflowOrchestrator()
    
    # Create dynamic workflow
    result = orchestrator.ai_executor.execute_prompt(
        prompt=f"Customer issue: {ticket['description']}. "
               f"Provide a helpful response.",
        system_message="You are a customer support specialist."
    )
    
    if result['success']:
        # Send auto-response
        send_ticket_response(ticket['id'], result['response'])
        
        # Log AI usage
        log_ai_usage(ticket['id'], result['usage'])
```

### 4. Data Analysis Reports

```python
def generate_analytics_report(data: dict):
    """Generate AI-powered analytics insights."""
    orchestrator = WorkflowOrchestrator()
    
    # Prepare data context
    context = {
        "revenue": data['revenue'],
        "users": data['users'],
        "churn": data['churn_rate']
    }
    
    result = orchestrator.ai_executor.execute_with_context(
        prompt="Analyze this data and provide 3 key insights: "
               "Revenue: {revenue}, Users: {users}, Churn: {churn}",
        context=context
    )
    
    return result['response']
```

## Security Best Practices

### 1. API Key Management

```python
# Use environment variables
import os
from dotenv import load_dotenv

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Never hardcode keys
# BAD: notion_api_key = "secret_abc123"
# GOOD: notion_api_key = os.getenv("NOTION_API_KEY")
```

### 2. Rate Limiting

```python
from functools import wraps
import time

def rate_limit(max_calls: int, period: int):
    """Rate limit decorator."""
    calls = []
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            calls[:] = [c for c in calls if c > now - period]
            
            if len(calls) >= max_calls:
                raise Exception("Rate limit exceeded")
            
            calls.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(max_calls=10, period=60)  # 10 calls per minute
def run_workflow_with_limit(workflow_id: str):
    # Your workflow execution code
    pass
```

### 3. Input Validation

```python
def validate_workflow_input(workflow_config: dict) -> bool:
    """Validate workflow configuration."""
    required_fields = ["Name", "Prompt"]
    
    for field in required_fields:
        if field not in workflow_config:
            raise ValueError(f"Missing required field: {field}")
    
    # Sanitize prompt
    prompt = workflow_config["Prompt"]
    if len(prompt) > 10000:
        raise ValueError("Prompt too long")
    
    # Check for injection attempts
    forbidden_patterns = ["<script>", "javascript:"]
    for pattern in forbidden_patterns:
        if pattern.lower() in prompt.lower():
            raise ValueError("Invalid prompt content")
    
    return True
```

### 4. Error Handling

```python
def safe_workflow_execution(workflow_id: str):
    """Execute workflow with comprehensive error handling."""
    try:
        orchestrator = WorkflowOrchestrator()
        result = orchestrator.run_workflow(workflow_id, config)
        
        return {
            "status": "success",
            "data": result
        }
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return {
            "status": "error",
            "error": "Invalid input",
            "message": str(e)
        }
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            "status": "error",
            "error": "Internal error",
            "message": "An unexpected error occurred"
        }
```

## Monitoring and Logging

### 1. Custom Logging

```python
import logging
from datetime import datetime

def setup_workflow_logging():
    """Configure logging for workflow execution."""
    logger = logging.getLogger('ai_workflow')
    logger.setLevel(logging.INFO)
    
    # File handler
    fh = logging.FileHandler(f'workflow_{datetime.now():%Y%m%d}.log')
    fh.setLevel(logging.INFO)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger
```

### 2. Metrics Tracking

```python
from dataclasses import dataclass
from typing import List

@dataclass
class WorkflowMetrics:
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_tokens_used: int = 0
    total_cost: float = 0.0
    
    def record_execution(self, result: dict):
        """Record workflow execution metrics."""
        self.total_executions += 1
        
        if result.get('success'):
            self.successful_executions += 1
        else:
            self.failed_executions += 1
        
        if 'usage' in result:
            tokens = result['usage'].get('total_tokens', 0)
            self.total_tokens_used += tokens
            
            # Estimate cost (adjust rates as needed)
            self.total_cost += (tokens / 1000) * 0.002

metrics = WorkflowMetrics()

def track_workflow_execution(workflow_id: str):
    """Execute and track workflow."""
    orchestrator = WorkflowOrchestrator()
    result = orchestrator.run_workflow(workflow_id, config)
    
    metrics.record_execution(result)
    
    return result
```

## Testing

### 1. Unit Tests

```python
import unittest
from unittest.mock import Mock, patch

class TestWorkflowOrchestrator(unittest.TestCase):
    def setUp(self):
        self.orchestrator = WorkflowOrchestrator(
            notion_api_key="test_key",
            openai_api_key="test_key"
        )
    
    @patch('ai_workflow.src.orchestrator.NotionWorkflowClient')
    @patch('ai_workflow.src.orchestrator.AIPromptExecutor')
    def test_run_workflow_success(self, mock_ai, mock_notion):
        """Test successful workflow execution."""
        mock_ai.return_value.execute_prompt.return_value = {
            'success': True,
            'response': 'Test response',
            'usage': {'total_tokens': 50}
        }
        
        result = self.orchestrator.run_workflow(
            workflow_id="test_id",
            workflow_config={
                "Name": "Test",
                "Prompt": "Test prompt"
            },
            dry_run=True
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['response'], 'Test response')
```

### 2. Integration Tests

```python
def test_full_workflow_integration():
    """Test complete workflow from Notion to AI execution."""
    # This requires actual API keys for integration testing
    orchestrator = WorkflowOrchestrator()
    
    # Use a test database
    results = orchestrator.run_workflows_from_database(
        database_id=os.getenv("TEST_DATABASE_ID"),
        status_filter="Test",
        dry_run=True
    )
    
    assert len(results) > 0
    assert all('workflow_id' in r for r in results)
```

## Performance Optimization

### 1. Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_workflow(workflow_id: str):
    """Cache workflow configurations."""
    client = NotionWorkflowClient()
    return client.get_database_items(workflow_id)
```

### 2. Async Execution

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def run_workflows_async(workflow_ids: List[str]):
    """Run multiple workflows concurrently."""
    orchestrator = WorkflowOrchestrator()
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(
                executor,
                orchestrator.run_workflow,
                wf_id,
                config
            )
            for wf_id in workflow_ids
        ]
        
        results = await asyncio.gather(*tasks)
        return results
```

## Deployment Checklist

- [ ] Set environment variables for API keys
- [ ] Configure rate limits
- [ ] Set up error monitoring (Sentry, etc.)
- [ ] Configure logging
- [ ] Set up backup Notion databases
- [ ] Test failover scenarios
- [ ] Document API endpoints
- [ ] Set up CI/CD pipeline
- [ ] Configure auto-scaling
- [ ] Set up cost monitoring for OpenAI usage

## Support

For integration questions or issues, please refer to:
- Main documentation: [README.md](README.md)
- Quick start: [QUICKSTART.md](../QUICKSTART.md)
- GitHub Issues: [Project Issues](https://github.com/MSBISMARB/data-engineering-with-data-build-tool-dbt-4458303/issues)
