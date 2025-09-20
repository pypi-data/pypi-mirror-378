"""
Supabase Database Client
Handles all database operations for prediction market logging
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
import json

logger = logging.getLogger(__name__)

class SupabaseClient:
    """
    Async Supabase client for database operations
    """

    def __init__(self, url: str, key: str):
        self.url = url
        self.key = key
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }

    async def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a record into a table"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.url}/rest/v1/{table}",
                    headers=self.headers,
                    json=data
                )

                if response.status_code in [200, 201]:
                    return response.json() if response.text else {"success": True}
                else:
                    logger.error(f"Supabase insert failed: {response.status_code} - {response.text}")
                    raise Exception(f"Database insert failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Supabase insert error: {e}")
            raise

    async def select(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Select records from a table"""
        try:
            url = f"{self.url}/rest/v1/{table}"
            params = {}

            if filters:
                for key, value in filters.items():
                    params[key] = f"eq.{value}"

            if limit:
                params["limit"] = str(limit)

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Supabase select failed: {response.status_code}")
                    return []
        except Exception as e:
            logger.error(f"Supabase select error: {e}")
            return []

    async def update(
        self,
        table: str,
        data: Dict[str, Any],
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update records in a table"""
        try:
            url = f"{self.url}/rest/v1/{table}"
            params = {}

            for key, value in filters.items():
                params[key] = f"eq.{value}"

            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    url,
                    headers=self.headers,
                    params=params,
                    json=data
                )

                if response.status_code in [200, 204]:
                    return {"success": True}
                else:
                    logger.error(f"Supabase update failed: {response.status_code}")
                    raise Exception(f"Database update failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Supabase update error: {e}")
            raise

    async def rpc(self, function: str, params: Dict[str, Any]) -> Any:
        """Call a Supabase RPC function"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.url}/rest/v1/rpc/{function}",
                    headers=self.headers,
                    json=params
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Supabase RPC failed: {response.status_code}")
                    raise Exception(f"RPC call failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Supabase RPC error: {e}")
            raise

# Database schema for Supabase
MARKET_ANALYSIS_SCHEMA = """
CREATE TABLE market_analysis_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    request_id VARCHAR(255) UNIQUE NOT NULL,
    creator_address VARCHAR(42) NOT NULL,
    input_text TEXT NOT NULL,

    -- Analysis results
    is_valid_market BOOLEAN NOT NULL,
    confidence_score DECIMAL(3,2) NOT NULL,
    oracle_provider VARCHAR(50),
    market_category VARCHAR(50),
    market_labels JSONB,

    -- Market details
    market_title VARCHAR(255),
    outcomes JSONB,
    resolution_criteria TEXT,
    resolution_timestamp TIMESTAMP,

    -- Economics
    initial_liquidity DECIMAL(20,6),
    estimated_volume DECIMAL(20,6),

    -- Contract data
    contract_address VARCHAR(42),
    transaction_hash VARCHAR(66),

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,

    -- Indexes
    INDEX idx_creator_address (creator_address),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_market_category (market_category)
);

-- Function to track market performance
CREATE OR REPLACE FUNCTION get_market_stats(address VARCHAR)
RETURNS TABLE (
    total_markets INT,
    successful_markets INT,
    total_liquidity DECIMAL,
    average_confidence DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::INT as total_markets,
        COUNT(CASE WHEN status = 'active' THEN 1 END)::INT as successful_markets,
        SUM(initial_liquidity)::DECIMAL as total_liquidity,
        AVG(confidence_score)::DECIMAL as average_confidence
    FROM market_analysis_logs
    WHERE creator_address = address;
END;
$$ LANGUAGE plpgsql;
"""