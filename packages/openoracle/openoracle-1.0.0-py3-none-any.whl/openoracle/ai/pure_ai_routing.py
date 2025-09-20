"""
Pure AI-based Oracle Routing Service
All decisions made by LLM with contextual knowledge
"""

import json
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import httpx

from ..schemas.oracle_schemas import (
    OracleProvider,
    DataCategory,
    OracleRoutingRequest,
    OracleRoutingResponse,
    UpdateFrequency
)

logger = logging.getLogger(__name__)

class PredictionMarketAnalysis(BaseModel):
    """Complete prediction market analysis from AI"""
    is_prediction_market: bool
    confidence: float = Field(ge=0, le=1)
    market_labels: List[str]
    category: str
    oracle_provider: str
    reasoning: str
    requirements: Dict[str, Any] = Field(default_factory=dict)
    resolution_sources: List[str] = Field(default_factory=list)
    market_type: str
    timeframe: Optional[str] = None
    resolution_method: str = "direct"
    update_frequency: str = "on_demand"

class PureAIRoutingService:
    """
    Pure AI routing - no deterministic logic
    All decisions via LLM with comprehensive context
    """

    # Complete oracle knowledge injected into every prompt
    ORACLE_CONTEXT = """
    ORACLE PROVIDERS AND THEIR BEST USE CASES:

    CHAINLINK:
    - Sports: Official partnerships with TheRundown, SportsdataIO for NFL/NBA/MLB data
    - Price feeds: Aggregated from multiple sources, highly reliable
    - Weather: AccuWeather integration
    - Chains: Ethereum, Polygon, Arbitrum, Optimism, Avalanche
    - Latency: 500ms, Reliability: 99%

    PYTH:
    - Crypto prices: Sub-second updates, best for BTC/ETH/SOL price thresholds
    - Stocks: Real-time NYSE/NASDAQ data
    - Forex: Major and minor currency pairs
    - Chains: Solana, Ethereum, Arbitrum, Base
    - Latency: 100ms (fastest), Reliability: 98%

    UMA (Optimistic Oracle):
    - Elections: Human validators verify AP/Reuters results
    - Corporate events: Product launches, earnings, announcements
    - Legal outcomes: Court decisions, regulatory rulings
    - Resolution: 2-hour challenge period for human verification
    - Best for events needing human judgment

    BAND:
    - Cross-chain: Best for multi-chain requirements
    - Custom APIs: Can integrate any external API
    - Social media: Twitter/Reddit sentiment and events
    - Flexible but slower than specialized oracles

    API3:
    - Weather: Direct NOAA integration (most accurate)
    - NFTs: OpenSea/Blur floor prices
    - First-party APIs: Direct from data sources
    - Chains: Ethereum, Polygon, Avalanche

    MARKET CATEGORIES AND TYPICAL ORACLES:
    - Sports betting → Chainlink (partnerships)
    - Election/Politics → UMA (human verification)
    - Crypto prices → Pyth (fastest) or Chainlink (reliable)
    - Weather events → API3 (NOAA) or Chainlink (AccuWeather)
    - Stock prices → Pyth (real-time) or Chainlink
    - NFT floors → API3 (OpenSea direct)
    - Corporate events → UMA (needs verification)
    - Social media → Band (API flexibility)

    RESOLUTION SOURCES:
    - Sports: ESPN, TheAthletic, Official league sites
    - Elections: AP, Reuters, Official government sources
    - Crypto: CoinGecko, CoinMarketCap, DEX prices
    - Stocks: NYSE, NASDAQ, Bloomberg
    - Weather: NOAA, AccuWeather, Weather.gov
    - Corporate: SEC filings, Press releases, Official announcements
    """

    def __init__(self, openrouter_api_key: str):
        self.api_key = openrouter_api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "openai/gpt-4o-mini"

    async def analyze_and_route(self, text: str) -> OracleRoutingResponse:
        """
        Complete AI analysis and routing in one call
        No deterministic logic - pure AI decision making
        """

        prompt = f"""
        You are an expert Oracle Routing system for prediction markets.

        {self.ORACLE_CONTEXT}

        Analyze this text and determine:
        1. Is it a valid prediction market?
        2. Which oracle provider should handle it?
        3. What market categories apply?

        Text to analyze: "{text}"

        Think step by step:
        - First, check if this has clear, measurable, verifiable outcomes
        - Identify the type of data needed (price, sports, election, etc.)
        - Match to the best oracle based on the context provided
        - Consider latency, reliability, and data source requirements
        - Assign market labels from: Sports, Politics, Entertainment, Crypto, Finance, Technology

        Return a JSON object with this EXACT structure:
        {{
            "is_prediction_market": boolean,
            "confidence": 0.0 to 1.0,
            "market_labels": ["Sports", "Politics", etc.],
            "category": "price|sports|election|weather|events|stocks|crypto|custom",
            "oracle_provider": "chainlink|pyth|uma|band|api3",
            "reasoning": "Detailed explanation of your decision",
            "requirements": {{
                "assets": ["BTC", "ETH"] or [],
                "timeframe": "24h|7d|30d|specific date" or null,
                "threshold": "price or value" or null
            }},
            "resolution_sources": ["Source 1", "Source 2"],
            "market_type": "price_threshold|game_outcome|election|event|custom",
            "timeframe": "When this resolves",
            "resolution_method": "direct|optimistic|aggregated",
            "update_frequency": "realtime|high_freq|medium_freq|on_demand"
        }}

        Respond ONLY with the JSON object, no additional text.
        """

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an oracle routing expert. Always respond with valid JSON only."
                            },
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 1000,
                        "response_format": {"type": "json_object"}
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    analysis = json.loads(result["choices"][0]["message"]["content"])

                    # Validate and create response
                    return self._create_routing_response(analysis)
                else:
                    logger.error(f"AI routing failed: {response.status_code}")
                    return self._error_response(f"API error: {response.status_code}")

        except Exception as e:
            logger.error(f"AI routing exception: {e}")
            return self._error_response(str(e))

    def _create_routing_response(self, analysis: Dict[str, Any]) -> OracleRoutingResponse:
        """Convert AI analysis to routing response"""
        try:
            # Map strings to enums safely
            oracle_str = analysis.get("oracle_provider", "chainlink")
            oracle = OracleProvider(oracle_str) if oracle_str in [p.value for p in OracleProvider] else OracleProvider.CHAINLINK

            category_str = analysis.get("category", "custom")
            category = DataCategory(category_str) if category_str in [c.value for c in DataCategory] else DataCategory.CUSTOM

            freq_str = analysis.get("update_frequency", "on_demand")
            frequency = UpdateFrequency(freq_str) if freq_str in [f.value for f in UpdateFrequency] else UpdateFrequency.ON_DEMAND

            return OracleRoutingResponse(
                can_resolve=analysis.get("is_prediction_market", False),
                selected_oracle=oracle if analysis.get("is_prediction_market") else None,
                reasoning=analysis.get("reasoning", ""),
                data_type=category,
                confidence_score=float(analysis.get("confidence", 0.0)),
                market_labels=analysis.get("market_labels", []),
                resolution_method=analysis.get("resolution_method", "direct"),
                update_frequency=frequency,
                metadata={
                    "market_type": analysis.get("market_type"),
                    "resolution_sources": analysis.get("resolution_sources", []),
                    "requirements": analysis.get("requirements", {}),
                    "timeframe": analysis.get("timeframe")
                }
            )
        except Exception as e:
            logger.error(f"Failed to create routing response: {e}")
            return self._error_response(f"Response creation failed: {str(e)}")

    def _error_response(self, error: str) -> OracleRoutingResponse:
        """Create error response"""
        return OracleRoutingResponse(
            can_resolve=False,
            reasoning=f"AI analysis failed: {error}",
            confidence_score=0.0,
            market_labels=["Custom"]
        )

    async def batch_analyze(self, texts: List[str]) -> List[OracleRoutingResponse]:
        """
        Analyze multiple texts in a single AI call for efficiency
        """

        batch_prompt = f"""
        {self.ORACLE_CONTEXT}

        Analyze these {len(texts)} texts for prediction market routing.
        For each one, determine the best oracle and categorization.

        Texts:
        {json.dumps([{"id": i, "text": text} for i, text in enumerate(texts)])}

        Return a JSON array where each element matches the structure from before.
        Maintain the same order as the input texts.
        """

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "Analyze multiple prediction markets. Return a JSON array."
                            },
                            {"role": "user", "content": batch_prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 3000,
                        "response_format": {"type": "json_object"}
                    },
                    timeout=60.0
                )

                if response.status_code == 200:
                    result = response.json()
                    analyses = json.loads(result["choices"][0]["message"]["content"])

                    # Convert each analysis to routing response
                    if isinstance(analyses, dict) and "results" in analyses:
                        analyses = analyses["results"]

                    return [self._create_routing_response(a) for a in analyses]
                else:
                    # Return error responses for all
                    return [self._error_response(f"Batch API error: {response.status_code}") for _ in texts]

        except Exception as e:
            logger.error(f"Batch analysis failed: {e}")
            return [self._error_response(str(e)) for _ in texts]