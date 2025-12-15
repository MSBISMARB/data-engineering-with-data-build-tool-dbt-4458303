"""
Example script: Test single AI prompt execution
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai_executor import AIPromptExecutor
from config.config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Test AI prompt execution."""
    # Load configuration
    config_file = Path(__file__).parent.parent / "config" / "config.env"
    config = Config(str(config_file) if config_file.exists() else None)
    
    logger.info("Testing AI Prompt Execution")
    
    # Initialize executor
    executor = AIPromptExecutor(
        api_key=config.openai_api_key,
        model=config.ai_model
    )
    
    # Test connection
    logger.info("Validating API connection...")
    if not executor.validate_api_connection():
        logger.error("API connection validation failed")
        return 1
    
    logger.info("✓ API connection validated")
    
    # Execute test prompt
    test_prompt = "Explain in 2 sentences what an AI workflow orchestrator does."
    logger.info(f"\nExecuting test prompt: {test_prompt}")
    
    result = executor.execute_prompt(
        prompt=test_prompt,
        system_message="You are a helpful technical assistant.",
        temperature=0.7,
        max_tokens=100
    )
    
    if result["success"]:
        logger.info("\n✓ Prompt executed successfully")
        logger.info(f"\nResponse:\n{result['response']}")
        logger.info(f"\nTokens used: {result['usage']['total_tokens']}")
    else:
        logger.error(f"\n✗ Prompt execution failed: {result.get('error')}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
