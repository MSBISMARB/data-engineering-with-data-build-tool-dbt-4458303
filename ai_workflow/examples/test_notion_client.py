"""
Example script: Test Notion integration
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.notion_client import NotionWorkflowClient
from config.config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Test Notion client."""
    # Load configuration
    config_file = Path(__file__).parent.parent / "config" / "config.env"
    config = Config(str(config_file) if config_file.exists() else None)
    
    logger.info("Testing Notion Integration")
    
    if not config.notion_database_id:
        logger.error("NOTION_DATABASE_ID is not configured")
        return 1
    
    # Initialize Notion client
    try:
        client = NotionWorkflowClient(api_key=config.notion_api_key)
        logger.info("✓ Notion client initialized")
    except Exception as e:
        logger.error(f"✗ Failed to initialize Notion client: {e}")
        return 1
    
    # Fetch workflows
    try:
        logger.info(f"\nFetching workflows from database: {config.notion_database_id}")
        workflows = client.get_workflows(
            database_id=config.notion_database_id,
            status_filter=config.workflow_status_filter
        )
        
        logger.info(f"✓ Retrieved {len(workflows)} workflows")
        
        # Display workflows
        for i, workflow in enumerate(workflows, 1):
            logger.info(f"\n--- Workflow {i} ---")
            logger.info(f"Name: {workflow.get('Name', 'N/A')}")
            logger.info(f"Status: {workflow.get('Status', 'N/A')}")
            logger.info(f"ID: {workflow.get('id', 'N/A')}")
            
            # Show first 100 chars of prompt if available
            prompt = workflow.get('Prompt', '')
            if prompt:
                preview = prompt[:100] + "..." if len(prompt) > 100 else prompt
                logger.info(f"Prompt preview: {preview}")
    
    except Exception as e:
        logger.error(f"✗ Failed to fetch workflows: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
