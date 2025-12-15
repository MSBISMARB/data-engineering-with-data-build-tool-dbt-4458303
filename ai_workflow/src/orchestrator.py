"""
Workflow Orchestrator
Coordinates the execution of AI workflows from Notion
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from .notion_client import NotionWorkflowClient
from .ai_executor import AIPromptExecutor

logger = logging.getLogger(__name__)


class WorkflowOrchestrator:
    """Orchestrates AI workflows from Notion to execution."""
    
    def __init__(
        self,
        notion_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        ai_model: str = "gpt-3.5-turbo"
    ):
        """
        Initialize workflow orchestrator.
        
        Args:
            notion_api_key: Notion API key
            openai_api_key: OpenAI API key
            ai_model: AI model to use
        """
        self.notion_client = NotionWorkflowClient(api_key=notion_api_key)
        self.ai_executor = AIPromptExecutor(api_key=openai_api_key, model=ai_model)
        logger.info("Workflow orchestrator initialized")
    
    def run_workflow(
        self,
        workflow_id: str,
        workflow_config: Dict[str, Any],
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Run a single workflow.
        
        Args:
            workflow_id: The Notion page ID for the workflow
            workflow_config: Configuration from Notion
            dry_run: If True, don't actually execute or update Notion
            
        Returns:
            Dictionary with execution results
        """
        workflow_name = workflow_config.get("Name", "Unnamed Workflow")
        logger.info(f"Starting workflow: {workflow_name} (ID: {workflow_id})")
        
        try:
            # Extract workflow parameters
            prompt = workflow_config.get("Prompt", "")
            system_message = workflow_config.get("System Message", None)
            temperature = workflow_config.get("Temperature", 0.7)
            max_tokens = workflow_config.get("Max Tokens", None)
            
            if not prompt:
                raise ValueError("Workflow must have a Prompt")
            
            # Update status to Running (if not dry run)
            if not dry_run:
                self.notion_client.update_workflow_status(
                    page_id=workflow_id,
                    status="Running"
                )
            
            # Execute the AI prompt
            logger.info(f"Executing AI prompt for workflow: {workflow_name}")
            execution_result = self.ai_executor.execute_prompt(
                prompt=prompt,
                system_message=system_message,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Prepare result
            result = {
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "success": execution_result.get("success", False),
                "response": execution_result.get("response"),
                "usage": execution_result.get("usage"),
                "error": execution_result.get("error"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Update status in Notion (if not dry run)
            if not dry_run:
                if result["success"]:
                    self.notion_client.update_workflow_status(
                        page_id=workflow_id,
                        status="Completed",
                        result=execution_result.get("response", "")
                    )
                else:
                    self.notion_client.update_workflow_status(
                        page_id=workflow_id,
                        status="Failed",
                        result=f"Error: {execution_result.get('error', 'Unknown error')}"
                    )
            
            logger.info(f"Workflow {workflow_name} completed successfully")
            return result
        
        except Exception as e:
            logger.error(f"Error running workflow {workflow_name}: {str(e)}")
            
            # Update status to Failed (if not dry run)
            if not dry_run:
                try:
                    self.notion_client.update_workflow_status(
                        page_id=workflow_id,
                        status="Failed",
                        result=f"Error: {str(e)}"
                    )
                except Exception as update_error:
                    logger.error(f"Failed to update status: {str(update_error)}")
            
            return {
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def run_workflows_from_database(
        self,
        database_id: str,
        status_filter: str = "Active",
        dry_run: bool = False,
        max_workflows: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Run all workflows from a Notion database.
        
        Args:
            database_id: The Notion database ID
            status_filter: Filter workflows by status
            dry_run: If True, don't actually execute or update Notion
            max_workflows: Optional limit on number of workflows to run
            
        Returns:
            List of execution results
        """
        logger.info(f"Fetching workflows from database: {database_id}")
        workflows = self.notion_client.get_workflows(
            database_id=database_id,
            status_filter=status_filter
        )
        
        if max_workflows:
            workflows = workflows[:max_workflows]
        
        logger.info(f"Found {len(workflows)} workflows to execute")
        
        results = []
        for i, workflow in enumerate(workflows):
            logger.info(f"Processing workflow {i+1}/{len(workflows)}")
            workflow_id = workflow.get("id")
            
            result = self.run_workflow(
                workflow_id=workflow_id,
                workflow_config=workflow,
                dry_run=dry_run
            )
            results.append(result)
        
        # Generate summary
        successful = sum(1 for r in results if r.get("success"))
        failed = len(results) - successful
        
        logger.info(
            f"Batch execution completed. "
            f"Total: {len(results)}, Successful: {successful}, Failed: {failed}"
        )
        
        return results
    
    def validate_setup(self) -> Dict[str, bool]:
        """
        Validate that all components are properly configured.
        
        Returns:
            Dictionary with validation results for each component
        """
        validation = {
            "notion_client": False,
            "ai_executor": False,
            "overall": False
        }
        
        try:
            # Validate Notion client
            logger.info("Validating Notion client...")
            validation["notion_client"] = self.notion_client.client is not None
        except Exception as e:
            logger.error(f"Notion validation failed: {str(e)}")
        
        try:
            # Validate AI executor
            logger.info("Validating AI executor...")
            validation["ai_executor"] = self.ai_executor.validate_api_connection()
        except Exception as e:
            logger.error(f"AI executor validation failed: {str(e)}")
        
        validation["overall"] = (
            validation["notion_client"] and 
            validation["ai_executor"]
        )
        
        return validation
