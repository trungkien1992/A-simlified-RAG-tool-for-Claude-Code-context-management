#!/usr/bin/env python3
"""
Base Connector Framework - Phase 2
Abstract base classes for all external tool connectors
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, AsyncIterator
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class ConnectorConfig:
    """Configuration for a connector"""
    name: str
    api_url: str
    api_key: Optional[str] = None
    oauth_token: Optional[str] = None
    webhook_url: Optional[str] = None
    rate_limit: int = 100  # requests per minute
    batch_size: int = 50


@dataclass
class DataEntity:
    """Generic data entity from external tool"""
    id: str
    type: str
    source: str
    content: Dict[str, Any]
    timestamp: datetime
    metadata: Dict[str, Any]


class BaseConnector(ABC):
    """Abstract base class for all connectors"""
    
    def __init__(self, config: ConnectorConfig):
        self.config = config
        self.rate_limiter = asyncio.Semaphore(config.rate_limit)
        
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the external service"""
        pass
        
    @abstractmethod
    async def fetch_entities(
        self, 
        entity_type: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> AsyncIterator[DataEntity]:
        """Fetch entities from the external service"""
        pass
        
    @abstractmethod
    async def setup_webhook(self, events: List[str]) -> bool:
        """Setup webhook for real-time updates"""
        pass
        
    @abstractmethod
    async def handle_webhook_event(self, event: Dict[str, Any]) -> DataEntity:
        """Handle incoming webhook event"""
        pass
        
    async def fetch_with_retry(
        self, 
        fetch_func, 
        max_retries: int = 3,
        backoff_factor: float = 2.0
    ):
        """Fetch with exponential backoff retry"""
        for attempt in range(max_retries):
            try:
                async with self.rate_limiter:
                    return await fetch_func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = backoff_factor ** attempt
                logger.warning(
                    f"Retry {attempt + 1}/{max_retries} after {wait_time}s: {e}"
                )
                await asyncio.sleep(wait_time)
