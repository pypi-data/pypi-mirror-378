"""
Walrus Protocol Storage Integration
Decentralized blob storage for SDK call history and audit trails
"""

import aiohttp
import asyncio
import json
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class SDKCallRecord:
    """Record of an SDK call for audit trail"""
    timestamp: str
    method: str
    endpoint: str
    user_address: str
    request_data: Dict[str, Any]
    response_data: Dict[str, Any]
    sdk_version: str
    platform: str
    duration_ms: int
    success: bool
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class WalrusBlobInfo:
    """Information about a stored Walrus blob"""
    blob_id: str
    timestamp: str
    size_bytes: int
    num_records: int
    user_address: str
    content_hash: str


class WalrusStorage:
    """
    Walrus Protocol storage client for immutable audit trails
    """

    def __init__(
        self,
        publisher_url: str = "https://publisher.walrus-testnet.walrus.space",
        aggregator_url: str = "https://aggregator.walrus-testnet.walrus.space",
        batch_size: int = 100,
        batch_timeout: int = 300  # 5 minutes
    ):
        """
        Initialize Walrus storage

        Args:
            publisher_url: Walrus publisher node URL
            aggregator_url: Walrus aggregator node URL
            batch_size: Number of records to batch before storing
            batch_timeout: Timeout in seconds before forcing batch storage
        """
        self.publisher_url = publisher_url.rstrip('/')
        self.aggregator_url = aggregator_url.rstrip('/')
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout

        self._session: Optional[aiohttp.ClientSession] = None
        self._batch: List[SDKCallRecord] = []
        self._batch_start: Optional[datetime] = None
        self._stored_blobs: List[WalrusBlobInfo] = []

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        # Store any remaining batched records
        if self._batch:
            await self._flush_batch()
        await self.close()

    async def connect(self):
        """Create aiohttp session"""
        if not self._session:
            self._session = aiohttp.ClientSession(
                headers={
                    "Content-Type": "application/octet-stream",
                    "User-Agent": "OpenOracle-SDK/1.0.0"
                }
            )

    async def close(self):
        """Close aiohttp session"""
        if self._session:
            await self._session.close()
            self._session = None

    def _compute_hash(self, data: bytes) -> str:
        """Compute SHA256 hash of data"""
        return hashlib.sha256(data).hexdigest()

    async def store_sdk_call(
        self,
        record: SDKCallRecord,
        immediate: bool = False
    ) -> Optional[str]:
        """
        Store SDK call record to Walrus

        Args:
            record: SDK call record to store
            immediate: Store immediately without batching

        Returns:
            Blob ID if stored immediately, None if batched
        """
        if immediate:
            # Store single record immediately
            return await self._store_blob([record], record.user_address)

        # Add to batch
        self._batch.append(record)

        # Start batch timer if needed
        if not self._batch_start:
            self._batch_start = datetime.now()

        # Check if batch should be stored
        should_flush = (
            len(self._batch) >= self.batch_size or
            (self._batch_start and
             (datetime.now() - self._batch_start).total_seconds() > self.batch_timeout)
        )

        if should_flush:
            return await self._flush_batch()

        return None

    async def _flush_batch(self) -> Optional[str]:
        """Flush current batch to storage"""
        if not self._batch:
            return None

        # Get user address from first record
        user_address = self._batch[0].user_address

        # Store batch
        blob_id = await self._store_blob(self._batch, user_address)

        # Reset batch
        self._batch = []
        self._batch_start = None

        return blob_id

    async def _store_blob(
        self,
        records: List[SDKCallRecord],
        user_address: str
    ) -> Optional[str]:
        """
        Store records as Walrus blob

        Args:
            records: List of SDK call records
            user_address: User's address for indexing

        Returns:
            Blob ID if successful
        """
        if not self._session:
            await self.connect()

        try:
            # Prepare blob data
            blob_data = {
                "version": "1.0.0",
                "timestamp": datetime.utcnow().isoformat(),
                "user_address": user_address,
                "num_records": len(records),
                "records": [r.to_dict() for r in records]
            }

            # Convert to bytes
            blob_bytes = json.dumps(blob_data, separators=(',', ':')).encode('utf-8')
            content_hash = self._compute_hash(blob_bytes)

            # Store to Walrus
            store_url = f"{self.publisher_url}/v1/store"

            async with self._session.post(
                store_url,
                data=blob_bytes,
                headers={
                    "Content-Type": "application/octet-stream",
                    "X-Content-Hash": content_hash
                }
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Failed to store blob: {error_text}")
                    return None

                result = await response.json()
                blob_id = result.get("blob_id")

                if blob_id:
                    # Track stored blob
                    blob_info = WalrusBlobInfo(
                        blob_id=blob_id,
                        timestamp=datetime.utcnow().isoformat(),
                        size_bytes=len(blob_bytes),
                        num_records=len(records),
                        user_address=user_address,
                        content_hash=content_hash
                    )
                    self._stored_blobs.append(blob_info)

                    logger.info(f"Stored {len(records)} records to Walrus blob {blob_id}")

                return blob_id

        except Exception as e:
            logger.error(f"Failed to store to Walrus: {e}")
            return None

    async def retrieve_blob(self, blob_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve blob from Walrus

        Args:
            blob_id: Walrus blob ID

        Returns:
            Blob data if successful
        """
        if not self._session:
            await self.connect()

        try:
            retrieve_url = f"{self.aggregator_url}/v1/api/blob/{blob_id}"

            async with self._session.get(retrieve_url) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Failed to retrieve blob: {error_text}")
                    return None

                blob_bytes = await response.read()
                blob_data = json.loads(blob_bytes.decode('utf-8'))
                return blob_data

        except Exception as e:
            logger.error(f"Failed to retrieve from Walrus: {e}")
            return None

    async def get_user_history(
        self,
        user_address: str,
        limit: int = 100
    ) -> List[SDKCallRecord]:
        """
        Get user's SDK call history

        Args:
            user_address: User's wallet address
            limit: Maximum number of records to return

        Returns:
            List of SDK call records
        """
        all_records = []

        # Check current batch
        for record in self._batch:
            if record.user_address == user_address:
                all_records.append(record)

        # Retrieve from stored blobs
        for blob_info in reversed(self._stored_blobs):
            if blob_info.user_address == user_address:
                blob_data = await self.retrieve_blob(blob_info.blob_id)
                if blob_data:
                    for record_data in blob_data.get("records", []):
                        record = SDKCallRecord(**record_data)
                        all_records.append(record)

                        if len(all_records) >= limit:
                            return all_records[:limit]

        return all_records[:limit]

    async def verify_blob_integrity(self, blob_id: str) -> Tuple[bool, Optional[str]]:
        """
        Verify integrity of stored blob

        Args:
            blob_id: Walrus blob ID

        Returns:
            Tuple of (is_valid, error_message)
        """
        blob_data = await self.retrieve_blob(blob_id)
        if not blob_data:
            return False, "Failed to retrieve blob"

        # Find blob info
        blob_info = None
        for info in self._stored_blobs:
            if info.blob_id == blob_id:
                blob_info = info
                break

        if not blob_info:
            return True, None  # Can't verify without original info

        # Verify record count
        actual_count = len(blob_data.get("records", []))
        if actual_count != blob_info.num_records:
            return False, f"Record count mismatch: expected {blob_info.num_records}, got {actual_count}"

        # Verify content hash
        blob_bytes = json.dumps(blob_data, separators=(',', ':')).encode('utf-8')
        actual_hash = self._compute_hash(blob_bytes)
        if actual_hash != blob_info.content_hash:
            return False, "Content hash mismatch"

        return True, None

    def get_stored_blobs(self) -> List[WalrusBlobInfo]:
        """Get list of stored blob information"""
        return self._stored_blobs.copy()

    def get_pending_count(self) -> int:
        """Get number of records pending in batch"""
        return len(self._batch)

    async def force_flush(self) -> Optional[str]:
        """Force flush of current batch"""
        return await self._flush_batch()