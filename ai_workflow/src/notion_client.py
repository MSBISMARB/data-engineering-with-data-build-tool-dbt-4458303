"""
Notion Client Module
Handles integration with Notion API to fetch workflow configurations
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    from notion_client import Client
except ImportError:
    Client = None

logger = logging.getLogger(__name__)


class NotionWorkflowClient:
    """Client for interacting with Notion to retrieve AI workflow configurations."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Notion client.
        
        Args:
            api_key: Notion API key. If not provided, reads from NOTION_API_KEY env var.
        """
        if Client is None:
            raise ImportError(
                "notion-client is not installed. "
                "Install it with: pip install 'notion-client>=2.0.0'"
            )
        
        self.api_key = api_key or os.getenv("NOTION_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Notion API key is required. "
                "Set NOTION_API_KEY environment variable or pass api_key parameter."
            )
        
        self.client = Client(auth=self.api_key)
        logger.info("Notion client initialized successfully")
    
    def get_database_items(self, database_id: str, filter_config: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Retrieve items from a Notion database.
        
        Args:
            database_id: The ID of the Notion database
            filter_config: Optional filter configuration for the query
            
        Returns:
            List of database items with their properties
        """
        try:
            query_params = {"database_id": database_id}
            if filter_config:
                query_params["filter"] = filter_config
            
            response = self.client.databases.query(**query_params)
            
            items = []
            for page in response.get("results", []):
                items.append(self._parse_page_properties(page))
            
            logger.info(f"Retrieved {len(items)} items from database {database_id}")
            return items
        
        except Exception as e:
            logger.error(f"Error retrieving database items: {str(e)}")
            raise
    
    def _parse_page_properties(self, page: Dict) -> Dict[str, Any]:
        """
        Parse Notion page properties into a clean dictionary.
        
        Args:
            page: Raw page object from Notion API
            
        Returns:
            Dictionary with cleaned properties
        """
        properties = {}
        properties["id"] = page.get("id")
        properties["created_time"] = page.get("created_time")
        properties["last_edited_time"] = page.get("last_edited_time")
        
        for prop_name, prop_data in page.get("properties", {}).items():
            prop_type = prop_data.get("type")
            
            if prop_type == "title":
                title_list = prop_data.get("title", [])
                properties[prop_name] = title_list[0].get("plain_text", "") if title_list else ""
            
            elif prop_type == "rich_text":
                text_list = prop_data.get("rich_text", [])
                properties[prop_name] = text_list[0].get("plain_text", "") if text_list else ""
            
            elif prop_type == "number":
                properties[prop_name] = prop_data.get("number")
            
            elif prop_type == "select":
                select_obj = prop_data.get("select")
                properties[prop_name] = select_obj.get("name") if select_obj else None
            
            elif prop_type == "multi_select":
                properties[prop_name] = [item.get("name") for item in prop_data.get("multi_select", [])]
            
            elif prop_type == "date":
                date_obj = prop_data.get("date")
                properties[prop_name] = date_obj.get("start") if date_obj else None
            
            elif prop_type == "checkbox":
                properties[prop_name] = prop_data.get("checkbox", False)
            
            elif prop_type == "url":
                properties[prop_name] = prop_data.get("url")
            
            elif prop_type == "email":
                properties[prop_name] = prop_data.get("email")
            
            elif prop_type == "phone_number":
                properties[prop_name] = prop_data.get("phone_number")
        
        return properties
    
    def get_workflows(self, database_id: str, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get AI workflows from Notion database.
        
        Args:
            database_id: The ID of the workflows database
            status_filter: Optional status to filter by (e.g., "Active", "Pending")
            
        Returns:
            List of workflow configurations
        """
        filter_config = None
        if status_filter:
            filter_config = {
                "property": "Status",
                "select": {
                    "equals": status_filter
                }
            }
        
        workflows = self.get_database_items(database_id, filter_config)
        logger.info(f"Retrieved {len(workflows)} workflows")
        return workflows
    
    def update_workflow_status(self, page_id: str, status: str, result: Optional[str] = None):
        """
        Update workflow status in Notion.
        
        Args:
            page_id: The ID of the page to update
            status: New status value
            result: Optional result/output to store
        """
        try:
            properties = {
                "Status": {
                    "select": {
                        "name": status
                    }
                }
            }
            
            if result:
                properties["Result"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": result[:2000]  # Notion rich text property limit
                            }
                        }
                    ]
                }
            
            properties["Last Executed"] = {
                "date": {
                    "start": datetime.utcnow().isoformat()
                }
            }
            
            self.client.pages.update(page_id=page_id, properties=properties)
            logger.info(f"Updated workflow {page_id} status to {status}")
        
        except Exception as e:
            logger.error(f"Error updating workflow status: {str(e)}")
            raise
