#!/usr/bin/env python3
"""
Jira Connector - Phase 2
Integrates with Atlassian Jira for issue tracking data
"""

import aiohttp
import asyncio
from typing import Dict, List, Any, Optional, AsyncIterator
from datetime import datetime
from .base_connector import BaseConnector, DataEntity, ConnectorConfig

logger = logging.getLogger(__name__)


class JiraConnector(BaseConnector):
    """Connector for Atlassian Jira"""
    
    async def authenticate(self) -> bool:
        """Authenticate using API token"""
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Accept": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.config.api_url}/rest/api/3/myself",
                headers=headers
            ) as response:
                return response.status == 200
                
    async def fetch_entities(
        self,
        entity_type: str = "issue",
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> AsyncIterator[DataEntity]:
        """Fetch Jira issues"""
        if entity_type != "issue":
            raise ValueError(f"Unsupported entity type: {entity_type}")
            
        jql = self._build_jql(filters)
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Accept": "application/json"
        }
        
        start_at = 0
        total_fetched = 0
        
        async with aiohttp.ClientSession() as session:
            while True:
                if limit and total_fetched >= limit:
                    break
                    
                params = {
                    "jql": jql,
                    "startAt": start_at,
                    "maxResults": min(
                        self.config.batch_size,
                        limit - total_fetched if limit else self.config.batch_size
                    )
                }
                
                response = await self.fetch_with_retry(
                    lambda: session.get(
                        f"{self.config.api_url}/rest/api/3/search",
                        headers=headers,
                        params=params
                    )
                )
                
                async with response as resp:
                    if resp.status != 200:
                        raise Exception(f"Jira API error: {resp.status}")
                        
                    data = await resp.json()
                    issues = data.get("issues", [])
                    
                    if not issues:
                        break
                        
                    for issue in issues:
                        yield self._convert_to_entity(issue)
                        total_fetched += 1
                        
                    start_at += len(issues)
                    
                    if start_at >= data.get("total", 0):
                        break
                        
    def _build_jql(self, filters: Optional[Dict[str, Any]]) -> str:
        """Build JQL query from filters"""
        if not filters:
            return "ORDER BY updated DESC"
            
        conditions = []
        if "project" in filters:
            conditions.append(f"project = {filters['project']}")
        if "updated_after" in filters:
            conditions.append(f"updated >= {filters['updated_after']}")
        if "assignee" in filters:
            conditions.append(f"assignee = {filters['assignee']}")
            
        jql = " AND ".join(conditions) if conditions else ""
        return f"{jql} ORDER BY updated DESC"
        
    def _convert_to_entity(self, issue: Dict[str, Any]) -> DataEntity:
        """Convert Jira issue to DataEntity"""
        return DataEntity(
            id=f"jira:{issue['key']}",
            type="jira_ticket",
            source="jira",
            content={
                "key": issue["key"],
                "summary": issue["fields"]["summary"],
                "description": issue["fields"].get("description", ""),
                "status": issue["fields"]["status"]["name"],
                "priority": issue["fields"].get("priority", {}).get("name"),
                "assignee": issue["fields"].get("assignee", {}).get("displayName"),
                "reporter": issue["fields"].get("reporter", {}).get("displayName"),
                "labels": issue["fields"].get("labels", []),
                "components": [c["name"] for c in issue["fields"].get("components", [])],
                "fix_versions": [v["name"] for v in issue["fields"].get("fixVersions", [])]
            },
            timestamp=datetime.fromisoformat(
                issue["fields"]["updated"].replace("Z", "+00:00")
            ),
            metadata={
                "project": issue["fields"]["project"]["key"],
                "issue_type": issue["fields"]["issuetype"]["name"],
                "created": issue["fields"]["created"],
                "resolution": issue["fields"].get("resolution", {}).get("name")
            }
        )
        
    async def setup_webhook(self, events: List[str]) -> bool:
        """Setup Jira webhook"""
        webhook_data = {
            "name": "Astra RAG Webhook",
            "url": self.config.webhook_url,
            "events": events,
            "filters": {
                "issue-related-events-section": ""
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.config.api_url}/rest/webhooks/1.0/webhook",
                headers=headers,
                json=webhook_data
            ) as response:
                return response.status == 201
                
    async def handle_webhook_event(self, event: Dict[str, Any]) -> DataEntity:
        """Process incoming Jira webhook event"""
        issue = event.get("issue", {})
        return self._convert_to_entity(issue)
