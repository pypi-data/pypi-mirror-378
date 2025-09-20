"""
Secure AI Router - Routes AI requests through OpenOracle proxy
No OpenRouter API key required!
"""

import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

from .proxy_client import ProxyClient
from ..schemas.market_proposal import MarketProposal, MarketSuggestion

logger = logging.getLogger(__name__)


@dataclass
class AIRoutingConfig:
    """Configuration for AI routing"""
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 2000
    fallback_models: List[str] = None
    response_format: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.fallback_models is None:
            self.fallback_models = ["gpt-3.5-turbo", "claude-3-haiku"]


class SecureAIRouter:
    """
    Secure AI routing through OpenOracle proxy
    Users only need their OpenOracle API key - we handle OpenRouter on the backend!
    """

    def __init__(
        self,
        openoracle_api_key: str,
        proxy_url: str = "https://api.openoracle.xyz",
        config: Optional[AIRoutingConfig] = None
    ):
        """
        Initialize secure AI router

        Args:
            openoracle_api_key: Your OpenOracle API key (NOT OpenRouter!)
            proxy_url: OpenOracle proxy server URL
            config: Optional routing configuration
        """
        self.api_key = openoracle_api_key
        self.proxy_url = proxy_url
        self.config = config or AIRoutingConfig()
        self.proxy_client = ProxyClient(openoracle_api_key, proxy_url)

    async def __aenter__(self):
        """Async context manager entry"""
        await self.proxy_client.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.proxy_client.close()

    async def generate_market_proposals(
        self,
        user_input: str,
        user_address: str,
        max_suggestions: int = 3
    ) -> MarketProposal:
        """
        Generate market proposals from user input

        Args:
            user_input: User's market idea
            user_address: User's wallet address
            max_suggestions: Number of suggestions to generate

        Returns:
            MarketProposal with AI-generated suggestions
        """
        system_prompt = """You are an expert at creating prediction markets.
        Transform the user's input into clear, engaging prediction market proposals.
        Each proposal should have:
        1. A clear, specific question with a measurable outcome
        2. Defined resolution criteria
        3. Appropriate timeframe
        4. Binary YES/NO format

        Generate diverse suggestions with different angles and timeframes."""

        user_prompt = f"""Transform this idea into {max_suggestions} prediction market proposals:
        "{user_input}"

        Return JSON with this structure:
        {{
            "suggestions": [
                {{
                    "title": "Clear market question",
                    "description": "Detailed description",
                    "outcomes": ["YES", "NO"],
                    "resolutionDate": "YYYY-MM-DD",
                    "category": "category",
                    "tags": ["tag1", "tag2"],
                    "estimatedProbability": 0.5,
                    "reasoning": "Why this market is interesting"
                }}
            ],
            "analysis": {{
                "marketType": "prediction/opinion/forecast",
                "complexity": "simple/moderate/complex",
                "suggestedOracle": "best oracle for this market"
            }}
        }}"""

        try:
            response = await self.proxy_client.generate_ai_content(
                prompt=f"{system_prompt}\n\n{user_prompt}",
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                response_format={"type": "json_object"}
            )

            result = response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            data = json.loads(result)

            # Convert to MarketProposal
            suggestions = []
            for s in data.get("suggestions", []):
                suggestions.append(MarketSuggestion(
                    title=s["title"],
                    description=s["description"],
                    outcomes=s["outcomes"],
                    resolution_date=s["resolutionDate"],
                    category=s.get("category", "general"),
                    tags=s.get("tags", []),
                    estimated_probability=s.get("estimatedProbability", 0.5),
                    reasoning=s.get("reasoning", "")
                ))

            analysis = data.get("analysis", {})

            return MarketProposal(
                user_input=user_input,
                suggestions=suggestions,
                recommended_index=0,
                analysis={
                    "market_type": analysis.get("marketType", "prediction"),
                    "complexity": analysis.get("complexity", "moderate"),
                    "suggested_oracle": analysis.get("suggestedOracle", "uma")
                },
                user_address=user_address
            )

        except Exception as e:
            logger.error(f"Failed to generate proposals: {e}")
            raise

    async def optimize_market_text(
        self,
        text: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Optimize market text for clarity and engagement

        Args:
            text: Market text to optimize
            context: Optional context about the market

        Returns:
            Optimized market details
        """
        prompt = f"""Optimize this prediction market text for clarity:

        Original: {text}
        Context: {context or 'General prediction market'}

        Return JSON with:
        {{
            "optimized_title": "Clear, engaging title",
            "description": "Detailed description",
            "resolution_criteria": "How this will be resolved",
            "potential_issues": ["issue1", "issue2"],
            "improvements": ["improvement1", "improvement2"]
        }}"""

        response = await self.proxy_client.generate_ai_content(
            prompt=prompt,
            model=self.config.model,
            temperature=0.5,  # Lower temperature for optimization
            response_format={"type": "json_object"}
        )

        result = response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        return json.loads(result)

    async def analyze_market_viability(
        self,
        title: str,
        description: str,
        resolution_date: str
    ) -> Dict[str, Any]:
        """
        Analyze market viability and potential issues

        Args:
            title: Market title
            description: Market description
            resolution_date: Resolution date

        Returns:
            Viability analysis
        """
        prompt = f"""Analyze this prediction market for viability:

        Title: {title}
        Description: {description}
        Resolution Date: {resolution_date}

        Return JSON with:
        {{
            "viability_score": 0.0-1.0,
            "strengths": ["strength1", "strength2"],
            "weaknesses": ["weakness1", "weakness2"],
            "suggested_improvements": ["improvement1", "improvement2"],
            "resolution_challenges": ["challenge1"],
            "estimated_interest": "low/medium/high",
            "similar_markets": ["example1", "example2"]
        }}"""

        response = await self.proxy_client.generate_ai_content(
            prompt=prompt,
            model=self.config.model,
            temperature=0.3,  # Low temperature for analysis
            response_format={"type": "json_object"}
        )

        result = response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        return json.loads(result)

    async def route_to_best_oracle(
        self,
        market_data: Dict[str, Any]
    ) -> str:
        """
        Determine best oracle for market using AI

        Args:
            market_data: Market details

        Returns:
            Recommended oracle name
        """
        prompt = f"""Given this prediction market, recommend the best oracle:

        Market: {json.dumps(market_data, indent=2)}

        Available oracles:
        - UMA: Best for subjective/complex markets with human verification
        - Chainlink: Best for price/data feeds
        - Pyth: Best for financial markets
        - API3: Best for first-party oracle data
        - Band: Best for cross-chain data

        Return JSON: {{"oracle": "oracle_name", "reasoning": "why this oracle"}}"""

        response = await self.proxy_client.generate_ai_content(
            prompt=prompt,
            model=self.config.model,
            temperature=0.2,  # Very low temperature for routing decisions
            response_format={"type": "json_object"}
        )

        result = response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        data = json.loads(result)
        return data.get("oracle", "uma")

    async def check_usage(self) -> Dict[str, Any]:
        """
        Check API usage and limits

        Returns:
            Usage statistics
        """
        return await self.proxy_client.get_usage_stats()

    async def validate_connection(self) -> bool:
        """
        Validate connection to proxy

        Returns:
            True if connection is valid
        """
        return await self.proxy_client.validate_api_key()