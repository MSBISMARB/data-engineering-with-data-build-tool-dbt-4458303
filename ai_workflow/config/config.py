"""
Configuration loader for AI Workflow
"""

import os
from typing import Dict, Any
from pathlib import Path


class Config:
    """Configuration manager for AI Workflow."""
    
    def __init__(self, env_file: str = None):
        """
        Initialize configuration.
        
        Args:
            env_file: Path to .env file (optional)
        """
        if env_file and os.path.exists(env_file):
            self._load_env_file(env_file)
    
    def _load_env_file(self, env_file: str):
        """Load environment variables from file."""
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    
    @property
    def notion_api_key(self) -> str:
        """Get Notion API key."""
        return os.getenv("NOTION_API_KEY", "")
    
    @property
    def notion_database_id(self) -> str:
        """Get Notion database ID."""
        return os.getenv("NOTION_DATABASE_ID", "")
    
    @property
    def openai_api_key(self) -> str:
        """Get OpenAI API key."""
        return os.getenv("OPENAI_API_KEY", "")
    
    @property
    def ai_model(self) -> str:
        """Get AI model name."""
        return os.getenv("AI_MODEL", "gpt-3.5-turbo")
    
    @property
    def workflow_status_filter(self) -> str:
        """Get workflow status filter."""
        return os.getenv("WORKFLOW_STATUS_FILTER", "Active")
    
    @property
    def max_workflows_per_run(self) -> int:
        """Get maximum workflows per run."""
        return int(os.getenv("MAX_WORKFLOWS_PER_RUN", "10"))
    
    @property
    def dry_run(self) -> bool:
        """Get dry run flag."""
        return os.getenv("DRY_RUN", "false").lower() in ["true", "1", "yes"]
    
    @property
    def log_level(self) -> str:
        """Get log level."""
        return os.getenv("LOG_LEVEL", "INFO")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "notion_api_key": "***" if self.notion_api_key else "",
            "notion_database_id": self.notion_database_id,
            "openai_api_key": "***" if self.openai_api_key else "",
            "ai_model": self.ai_model,
            "workflow_status_filter": self.workflow_status_filter,
            "max_workflows_per_run": self.max_workflows_per_run,
            "dry_run": self.dry_run,
            "log_level": self.log_level
        }
