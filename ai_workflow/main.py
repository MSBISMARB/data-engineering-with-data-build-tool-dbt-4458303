#!/usr/bin/env python3
"""
Main CLI interface for AI Workflow
Provides command-line interface for running workflows
"""

import sys
import argparse
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator import WorkflowOrchestrator
from src.notion_client import NotionWorkflowClient
from src.ai_executor import AIPromptExecutor
from config.config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_command(config: Config):
    """Validate the setup."""
    logger.info("Validating AI Workflow setup...")
    
    orchestrator = WorkflowOrchestrator(
        notion_api_key=config.notion_api_key,
        openai_api_key=config.openai_api_key,
        ai_model=config.ai_model
    )
    
    validation = orchestrator.validate_setup()
    
    print("\n" + "="*60)
    print("VALIDATION RESULTS")
    print("="*60)
    print(f"Notion Client: {'✓ OK' if validation['notion_client'] else '✗ Failed'}")
    print(f"AI Executor: {'✓ OK' if validation['ai_executor'] else '✗ Failed'}")
    print(f"Overall: {'✓ READY' if validation['overall'] else '✗ NOT READY'}")
    print("="*60)
    
    return 0 if validation["overall"] else 1


def list_command(config: Config):
    """List workflows from Notion database."""
    logger.info("Fetching workflows from Notion...")
    
    if not config.notion_database_id:
        logger.error("NOTION_DATABASE_ID is not configured")
        return 1
    
    try:
        client = NotionWorkflowClient(api_key=config.notion_api_key)
        workflows = client.get_workflows(
            database_id=config.notion_database_id,
            status_filter=config.workflow_status_filter
        )
        
        print("\n" + "="*60)
        print(f"WORKFLOWS (Status: {config.workflow_status_filter})")
        print("="*60)
        
        if not workflows:
            print("No workflows found")
        else:
            for i, workflow in enumerate(workflows, 1):
                print(f"\n{i}. {workflow.get('Name', 'Unnamed')}")
                print(f"   ID: {workflow.get('id')}")
                print(f"   Status: {workflow.get('Status', 'N/A')}")
                
                prompt = workflow.get('Prompt', '')
                if prompt:
                    preview = prompt[:80] + "..." if len(prompt) > 80 else prompt
                    print(f"   Prompt: {preview}")
        
        print("\n" + "="*60)
        print(f"Total: {len(workflows)} workflows")
        print("="*60)
        
        return 0
    
    except Exception as e:
        logger.error(f"Failed to list workflows: {e}")
        return 1


def run_command(config: Config, dry_run: bool = False):
    """Run workflows."""
    logger.info("Starting workflow execution...")
    
    if not config.notion_database_id:
        logger.error("NOTION_DATABASE_ID is not configured")
        return 1
    
    try:
        orchestrator = WorkflowOrchestrator(
            notion_api_key=config.notion_api_key,
            openai_api_key=config.openai_api_key,
            ai_model=config.ai_model
        )
        
        results = orchestrator.run_workflows_from_database(
            database_id=config.notion_database_id,
            status_filter=config.workflow_status_filter,
            dry_run=dry_run or config.dry_run,
            max_workflows=config.max_workflows_per_run
        )
        
        # Print summary
        successful = sum(1 for r in results if r.get("success"))
        failed = len(results) - successful
        
        print("\n" + "="*60)
        print("EXECUTION SUMMARY")
        print("="*60)
        print(f"Total workflows: {len(results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        
        if dry_run or config.dry_run:
            print("\n⚠️  DRY RUN MODE - No changes were made to Notion")
        
        print("="*60)
        
        # Print individual results
        for result in results:
            status = "✓" if result.get("success") else "✗"
            print(f"\n{status} {result.get('workflow_name')}")
            
            if result.get("error"):
                print(f"  Error: {result.get('error')}")
            elif result.get("response"):
                response = result["response"][:100] + "..." if len(result["response"]) > 100 else result["response"]
                print(f"  Response: {response}")
            
            if result.get("usage"):
                print(f"  Tokens: {result['usage'].get('total_tokens')}")
        
        print()
        return 0 if failed == 0 else 1
    
    except Exception as e:
        logger.error(f"Failed to run workflows: {e}")
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI Workflow - Industrialize AI workflows from Notion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s validate              Validate setup and configuration
  %(prog)s list                  List workflows from Notion
  %(prog)s run                   Run workflows
  %(prog)s run --dry-run         Run in dry-run mode (no changes)
  
For more information, see README.md
        """
    )
    
    parser.add_argument(
        'command',
        choices=['validate', 'list', 'run'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to config file (default: config/config.env)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run in dry-run mode (no changes to Notion)'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load configuration
    config_file = args.config
    if not config_file:
        config_file = Path(__file__).resolve().parent / "config" / "config.env"
        if not config_file.exists():
            config_file = None
    
    if config_file and Path(config_file).exists():
        config = Config(str(config_file))
    else:
        config = Config()
    
    logger.debug(f"Configuration loaded: {config.to_dict()}")
    
    # Execute command
    try:
        if args.command == 'validate':
            return validate_command(config)
        elif args.command == 'list':
            return list_command(config)
        elif args.command == 'run':
            return run_command(config, dry_run=args.dry_run)
        else:
            parser.print_help()
            return 1
    
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=args.verbose)
        return 1


if __name__ == "__main__":
    sys.exit(main())
