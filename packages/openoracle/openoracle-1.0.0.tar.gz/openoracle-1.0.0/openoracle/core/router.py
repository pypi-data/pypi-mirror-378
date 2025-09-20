"""
Main OpenOracle Router Class
Central interface for oracle routing and data retrieval
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from decimal import Decimal

from .config import OracleConfig, get_config
from .client import OpenOracleClient
from .exceptions import OracleError, RoutingError, ProviderError
from ..schemas.oracle_schemas import (
    OracleProvider,
    DataCategory,
    OracleRoutingRequest,
    OracleRoutingResponse,
    OracleDataPoint,
    OraclePollData,
    AggregatedOracleData
)
# Providers removed - using pure AI routing only
from ..api.client import OpenOracleAPI
from ..ai.pure_ai_routing import PureAIRoutingService

logger = logging.getLogger(__name__)

class OpenOracleRouter:
    """
    Main class for intelligent oracle routing
    Provides a unified interface for all oracle operations
    Uses pure AI-based routing with no deterministic logic
    """

    def __init__(
        self,
        openrouter_api_key: Optional[str] = None,
        chainlink_rpc: Optional[str] = None,
        enable_ai_routing: bool = True
    ):
        """
        Initialize OpenOracle Router

        Args:
            openrouter_api_key: API key for GPT-4o-mini via OpenRouter
            chainlink_rpc: RPC URL for Chainlink queries
            enable_ai_routing: Whether to use AI for routing
        """
        self.enable_ai = enable_ai_routing and openrouter_api_key is not None

        # Use pure AI routing service when API key is provided
        if self.enable_ai:
            self.routing_service = PureAIRoutingService(openrouter_api_key)
        else:
            raise ValueError("OpenRouter API key required for AI-based routing")

        # No provider initialization needed - pure AI handles everything
        self.providers = {}

    async def route_poll_question(
        self,
        question: str,
        category_hint: Optional[DataCategory] = None,
        preferred_chains: Optional[List[str]] = None,
        max_latency_ms: Optional[int] = None,
        max_cost_usd: Optional[Decimal] = None
    ) -> OracleRoutingResponse:
        """
        Route a poll question to the most appropriate oracle using AI

        Args:
            question: The poll question to analyze
            category_hint: Optional hint about data category
            preferred_chains: List of preferred blockchain networks
            max_latency_ms: Maximum acceptable latency
            max_cost_usd: Maximum acceptable cost

        Returns:
            OracleRoutingResponse with routing decision
        """
        # Pure AI routing - all context handled by AI
        return await self.routing_service.analyze_and_route(question)

    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text to determine if it's suitable for a prediction market

        Args:
            text: The text to analyze

        Returns:
            Analysis results including category, confidence, and requirements
        """
        # Use pure AI analysis
        response = await self.routing_service.analyze_and_route(text)

        return {
            'is_prediction_market': response.can_resolve,
            'category': response.data_type.value if response.data_type else 'custom',
            'confidence': response.confidence_score,
            'requirements': response.metadata.get('requirements', {}) if response.metadata else {},
            'market_type': response.metadata.get('market_type', 'unknown') if response.metadata else 'unknown',
            'market_labels': response.market_labels or [],
            'resolution_sources': response.metadata.get('resolution_sources', []) if response.metadata else [],
            'recommended_oracle': response.reasoning
        }

    async def route_text_to_oracle(
        self,
        text: str,
        force_routing: bool = False
    ) -> OracleRoutingResponse:
        """
        Analyze text and route to appropriate oracle if suitable for prediction market

        Args:
            text: The text to analyze and route
            force_routing: Force routing even if not ideal for prediction market

        Returns:
            OracleRoutingResponse with routing decision
        """
        # Pure AI routing handles everything
        response = await self.routing_service.analyze_and_route(text)

        # Override if force_routing is set
        if force_routing and not response.can_resolve:
            response.can_resolve = True
            response.reasoning = f"Force routed: {response.reasoning}"

        return response

    async def batch_route(self, texts: List[str]) -> List[OracleRoutingResponse]:
        """
        Route multiple texts efficiently in a single AI call

        Args:
            texts: List of texts to analyze

        Returns:
            List of routing responses
        """
        return await self.routing_service.batch_analyze(texts)

    async def get_oracle_data(
        self,
        provider: OracleProvider,
        data_type: DataCategory,
        params: Dict[str, Any]
    ) -> Optional[OracleDataPoint]:
        """
        Get data from a specific oracle provider

        Args:
            provider: The oracle provider to use
            data_type: Type of data to retrieve
            params: Provider-specific parameters

        Returns:
            OracleDataPoint with the requested data
        """
        oracle_provider = self.providers.get(provider)
        if not oracle_provider:
            logger.error(f"Provider {provider} not implemented")
            return None

        try:
            if provider == OracleProvider.CHAINLINK:
                if data_type == DataCategory.PRICE:
                    feed = await oracle_provider.get_price_feed(params.get('pair', 'ETH/USD'))
                    if feed:
                        return await oracle_provider.to_oracle_data_point(feed)
                elif data_type == DataCategory.SPORTS:
                    data = await oracle_provider.get_sports_data(
                        params.get('sport', 'NFL'),
                        params.get('game_id', '')
                    )
                    if data:
                        return OracleDataPoint(
                            provider=provider,
                            data_type=data_type,
                            value=data,
                            timestamp=datetime.utcnow(),
                            confidence=0.95
                        )

            elif provider == OracleProvider.PYTH:
                if data_type == DataCategory.PRICE:
                    feed = await oracle_provider.get_price_feed(params.get('symbol', 'BTC/USD'))
                    if feed:
                        return await oracle_provider.to_oracle_data_point(feed)

        except Exception as e:
            logger.error(f"Failed to get oracle data: {e}")

        return None

    async def get_aggregated_data(
        self,
        data_type: DataCategory,
        params: Dict[str, Any],
        providers: Optional[List[OracleProvider]] = None
    ) -> Optional[AggregatedOracleData]:
        """
        Get aggregated data from multiple oracle providers

        Args:
            data_type: Type of data to retrieve
            params: Parameters for data retrieval
            providers: List of providers to aggregate from

        Returns:
            AggregatedOracleData with consensus value
        """
        if not providers:
            # Default to price oracles for price data
            if data_type == DataCategory.PRICE:
                providers = [OracleProvider.CHAINLINK, OracleProvider.PYTH]
            else:
                providers = [OracleProvider.CHAINLINK]

        data_points = []
        individual_values = {}

        for provider in providers:
            data_point = await self.get_oracle_data(provider, data_type, params)
            if data_point:
                data_points.append(data_point)
                individual_values[provider.value] = data_point.value

        if not data_points:
            return None

        # Calculate aggregated value (median for numeric data)
        if all(isinstance(dp.value, (int, float)) for dp in data_points):
            values = sorted([dp.value for dp in data_points])
            if len(values) % 2 == 0:
                median_value = (values[len(values)//2 - 1] + values[len(values)//2]) / 2
            else:
                median_value = values[len(values)//2]

            # Check for discrepancies (>5% difference)
            max_val = max(values)
            min_val = min(values)
            discrepancy = (max_val - min_val) / max_val > 0.05 if max_val > 0 else False

            return AggregatedOracleData(
                data_type=data_type,
                providers=providers,
                aggregation_method="median",
                aggregated_value=median_value,
                individual_values=individual_values,
                timestamp=datetime.utcnow(),
                confidence=0.95 if not discrepancy else 0.8,
                discrepancy_detected=discrepancy
            )
        else:
            # For non-numeric data, return the most recent
            latest_point = max(data_points, key=lambda dp: dp.timestamp)
            return AggregatedOracleData(
                data_type=data_type,
                providers=providers,
                aggregation_method="latest",
                aggregated_value=latest_point.value,
                individual_values=individual_values,
                timestamp=latest_point.timestamp,
                confidence=latest_point.confidence or 0.9,
                discrepancy_detected=False
            )

    async def create_oracle_poll(
        self,
        question: str,
        poll_id: str,
        auto_resolve: bool = True
    ) -> Optional[OraclePollData]:
        """
        Create a poll with oracle backing for automatic resolution

        Args:
            question: The poll question
            poll_id: Unique identifier for the poll
            auto_resolve: Whether to automatically resolve when data is available

        Returns:
            OraclePollData with oracle configuration
        """
        # Route the question to find appropriate oracle
        routing_response = await self.route_poll_question(question)

        if not routing_response.can_resolve:
            logger.warning(f"Cannot create oracle-backed poll: {routing_response.reasoning}")
            return None

        # Get initial oracle data if available
        initial_data = []
        if routing_response.selected_oracle and routing_response.metadata:
            data_point = await self.get_oracle_data(
                routing_response.selected_oracle,
                routing_response.data_type or DataCategory.CUSTOM,
                routing_response.metadata.get('requirements', {})
            )
            if data_point:
                initial_data.append(data_point)

        # Create poll data structure
        poll_data = OraclePollData(
            poll_id=poll_id,
            oracle_provider=routing_response.selected_oracle,
            data_points=initial_data,
            resolution_criteria=routing_response.reasoning,
            auto_resolve=auto_resolve
        )

        return poll_data

    async def resolve_poll(
        self,
        poll_data: OraclePollData
    ) -> Dict[str, Any]:
        """
        Resolve a poll using oracle data

        Args:
            poll_data: The poll data with oracle configuration

        Returns:
            Resolution result with winning option and proof
        """
        # Get latest oracle data
        if poll_data.oracle_provider:
            # This would contain the actual resolution logic
            # For now, return a mock resolution
            return {
                'resolved': True,
                'winning_option': 'Yes',
                'oracle_value': 100.0,
                'proof': '0x' + '0' * 64,
                'timestamp': datetime.utcnow().isoformat()
            }

        return {
            'resolved': False,
            'reason': 'No oracle provider configured'
        }