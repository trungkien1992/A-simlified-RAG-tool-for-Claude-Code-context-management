#!/usr/bin/env python3
"""
Modular Ingestion Engine - Phase 2
Microservice-based ingestion with orchestrator and workers
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import aioredis
from ..connectors.base_connector import BaseConnector, DataEntity
from ..hybrid.hybrid_rag import HybridRAG

logger = logging.getLogger(__name__)


@dataclass
class IngestionJob:
    """Represents an ingestion job"""
    id: str
    connector: str
    entity_type: str
    filters: Dict[str, Any]
    status: str  # pending, processing, completed, failed
    created_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    entities_processed: int = 0


class IngestionOrchestrator:
    """Orchestrates ingestion across multiple connectors"""
    
    def __init__(self, redis_url: str = "redis://localhost"):
        self.redis_url = redis_url
        self.connectors: Dict[str, BaseConnector] = {}
        self.workers: List[IngestionWorker] = []
        self.job_queue = asyncio.Queue()
        
    async def initialize(self):
        """Initialize orchestrator"""
        self.redis = await aioredis.create_redis_pool(self.redis_url)
        logger.info("Ingestion orchestrator initialized")
        
    def register_connector(self, name: str, connector: BaseConnector):
        """Register a new connector"""
        self.connectors[name] = connector
        logger.info(f"Registered connector: {name}")
        
    async def schedule_ingestion(
        self,
        connector_name: str,
        entity_type: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Schedule an ingestion job"""
        job = IngestionJob(
            id=f"job_{datetime.now().timestamp()}",
            connector=connector_name,
            entity_type=entity_type,
            filters=filters or {},
            status="pending",
            created_at=datetime.now()
        )
        
        # Add to queue
        await self.job_queue.put(job)
        
        # Store in Redis
        await self.redis.set(
            f"ingestion_job:{job.id}",
            job.__dict__,
            expire=86400  # 24 hours
        )
        
        return job.id
        
    async def get_job_status(self, job_id: str) -> Optional[IngestionJob]:
        """Get status of an ingestion job"""
        data = await self.redis.get(f"ingestion_job:{job_id}")
        if data:
            return IngestionJob(**data)
        return None
        
    async def start_workers(self, num_workers: int = 4):
        """Start ingestion workers"""
        for i in range(num_workers):
            worker = IngestionWorker(
                worker_id=f"worker_{i}",
                orchestrator=self
            )
            self.workers.append(worker)
            asyncio.create_task(worker.run())
            
        logger.info(f"Started {num_workers} ingestion workers")


class IngestionWorker:
    """Worker that processes ingestion jobs"""
    
    def __init__(self, worker_id: str, orchestrator: IngestionOrchestrator):
        self.worker_id = worker_id
        self.orchestrator = orchestrator
        self.rag_system: Optional[HybridRAG] = None
        
    async def run(self):
        """Main worker loop"""
        logger.info(f"{self.worker_id} started")
        
        while True:
            try:
                # Get job from queue
                job = await self.orchestrator.job_queue.get()
                
                # Process job
                await self.process_job(job)
                
            except Exception as e:
                logger.error(f"{self.worker_id} error: {e}")
                await asyncio.sleep(5)
                
    async def process_job(self, job: IngestionJob):
        """Process a single ingestion job"""
        logger.info(f"{self.worker_id} processing job {job.id}")
        
        try:
            # Update job status
            job.status = "processing"
            await self._update_job_status(job)
            
            # Get connector
            connector = self.orchestrator.connectors.get(job.connector)
            if not connector:
                raise ValueError(f"Unknown connector: {job.connector}")
                
            # Fetch and process entities
            count = 0
            async for entity in connector.fetch_entities(
                entity_type=job.entity_type,
                filters=job.filters
            ):
                await self._process_entity(entity)
                count += 1
                
                # Update progress periodically
                if count % 100 == 0:
                    job.entities_processed = count
                    await self._update_job_status(job)
                    
            # Mark job as completed
            job.status = "completed"
            job.entities_processed = count
            job.completed_at = datetime.now()
            await self._update_job_status(job)
            
            logger.info(
                f"{self.worker_id} completed job {job.id}: "
                f"{count} entities processed"
            )
            
        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            await self._update_job_status(job)
            logger.error(f"{self.worker_id} job {job.id} failed: {e}")
            
    async def _process_entity(self, entity: DataEntity):
        """Process a single entity into the RAG system"""
        # This would integrate with the dual pipeline ingestion
        # Converting external entities to graph nodes and vector chunks
        pass
        
    async def _update_job_status(self, job: IngestionJob):
        """Update job status in Redis"""
        await self.orchestrator.redis.set(
            f"ingestion_job:{job.id}",
            job.__dict__,
            expire=86400
        )
