"""
Example script: Run AI workflows from Notion database
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator import WorkflowOrchestrator
from config.config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function to run workflows."""
    # Load configuration
    config_file = Path(__file__).parent.parent / "config" / "config.env"
    config = Config(str(config_file) if config_file.exists() else None)
    
    logger.info("Starting AI Workflow execution")
    logger.info(f"Configuration: {config.to_dict()}")
    
    # Initialize orchestrator
    orchestrator = WorkflowOrchestrator(
        notion_api_key=config.notion_api_key,
        openai_api_key=config.openai_api_key,
        ai_model=config.ai_model
    )
    
    # Validate setup
    logger.info("Validating setup...")
    validation = orchestrator.validate_setup()
    logger.info(f"Validation results: {validation}")
    
    if not validation["overall"]:
        logger.error("Setup validation failed. Please check your configuration.")
        return 1
    
    # Run workflows
    if not config.notion_database_id:
        logger.error("NOTION_DATABASE_ID is not set. Please configure it.")
        return 1
    
    logger.info(f"Running workflows from database: {config.notion_database_id}")
    results = orchestrator.run_workflows_from_database(
        database_id=config.notion_database_id,
        status_filter=config.workflow_status_filter,
        dry_run=config.dry_run,
        max_workflows=config.max_workflows_per_run
    )
    
    # Print summary
    successful = sum(1 for r in results if r.get("success"))
    failed = len(results) - successful
    
    logger.info("\n" + "="*60)
    logger.info("EXECUTION SUMMARY")
    logger.info("="*60)
    logger.info(f"Total workflows: {len(results)}")
    logger.info(f"Successful: {successful}")
    logger.info(f"Failed: {failed}")
    logger.info("="*60)
    
    # Print individual results
    for result in results:
        logger.info(f"\nWorkflow: {result.get('workflow_name')}")
        logger.info(f"  Status: {'✓ Success' if result.get('success') else '✗ Failed'}")
        if result.get("error"):
            logger.info(f"  Error: {result.get('error')}")
        if result.get("usage"):
            logger.info(f"  Tokens: {result['usage'].get('total_tokens')}")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
