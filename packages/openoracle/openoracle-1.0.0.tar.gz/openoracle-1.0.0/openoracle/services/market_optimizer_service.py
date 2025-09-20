"""
Market Optimizer Service
Transforms any text into a valid prediction market and explains oracle selection
"""

import json
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import httpx

from ..schemas.prediction_market_schemas import (
    PredictionQualification,
    OracleRouting
)

logger = logging.getLogger(__name__)

class MarketOptimizerService:
    """
    Service that can transform ANY text into a valid prediction market
    and explains exactly how oracle selection works
    """

    # Oracle capabilities and what they can actually measure
    ORACLE_CAPABILITIES_DETAILED = {
        "CHAINLINK": {
            "can_measure": {
                "prices": "Any crypto/stock/commodity price from aggregated sources",
                "sports": "NFL, NBA, MLB game results via TheRundown and SportsdataIO partnerships",
                "weather": "Temperature, precipitation, wind via AccuWeather API",
                "randomness": "VRF for provably fair random numbers"
            },
            "cannot_measure": {
                "subjective": "Opinions, quality judgments, artistic merit",
                "future_unknowns": "Things that don't have data feeds yet",
                "private_data": "Private company metrics, personal information"
            },
            "examples": {
                "valid": [
                    "Will ETH price exceed $5000?",
                    "Will the Lakers win tonight?",
                    "Will temperature in NYC exceed 90°F tomorrow?"
                ],
                "invalid": [
                    "Will the new iPhone be good?",
                    "Will people like the movie?",
                    "Will my startup succeed?"
                ]
            }
        },

        "PYTH": {
            "can_measure": {
                "crypto_prices": "Real-time BTC, ETH, SOL, etc. with microsecond latency",
                "stock_prices": "NYSE, NASDAQ stocks during market hours",
                "forex": "Currency pairs like USD/EUR, GBP/JPY",
                "commodities": "Gold, silver, oil futures"
            },
            "cannot_measure": {
                "events": "Non-price events",
                "sports": "Game outcomes",
                "weather": "Environmental data"
            },
            "examples": {
                "valid": [
                    "Will Bitcoin hit $100,000 by EOY?",
                    "Will TSLA stock close above $300?",
                    "Will gold price exceed $2000/oz?"
                ],
                "invalid": [
                    "Will Tesla release a new car?",
                    "Will Elon tweet about Dogecoin?",
                    "Will there be a recession?"
                ]
            }
        },

        "UMA": {
            "can_measure": {
                "elections": "Political outcomes verified by humans using AP/Reuters",
                "corporate_events": "Product launches, earnings, announcements",
                "legal_outcomes": "Court decisions, regulatory rulings",
                "any_verifiable": "ANYTHING that humans can verify after it happens"
            },
            "cannot_measure": {
                "real_time": "Needs 2-hour dispute period",
                "high_frequency": "Not for rapid resolution"
            },
            "examples": {
                "valid": [
                    "Will Biden win the 2024 election?",
                    "Will Apple announce new iPhone by September?",
                    "Will the Fed raise rates this quarter?",
                    "Will Twitter reach 500M users?"
                ],
                "invalid": [
                    "What's the BTC price right now?",
                    "Current temperature in Tokyo?"
                ]
            }
        },

        "BAND": {
            "can_measure": {
                "any_api": "Can call ANY public API endpoint",
                "cross_chain": "Data from other blockchains",
                "social_media": "Twitter followers, YouTube views",
                "custom": "Any data source with an API"
            },
            "cannot_measure": {
                "private": "Private or authenticated APIs",
                "subjective": "Quality or opinion data"
            },
            "examples": {
                "valid": [
                    "Will @elonmusk reach 200M Twitter followers?",
                    "Will YouTube video get 1B views?",
                    "Will GitHub repo get 10k stars?"
                ],
                "invalid": [
                    "Will the tweet be funny?",
                    "Will the video be good?"
                ]
            }
        },

        "API3": {
            "can_measure": {
                "weather": "Direct NOAA integration for US weather",
                "nft_floors": "OpenSea, Blur collection floor prices",
                "first_party": "Direct from data source, no middlemen"
            },
            "cannot_measure": {
                "aggregated": "Not for consensus across sources",
                "complex_events": "Simple data points only"
            },
            "examples": {
                "valid": [
                    "Will it rain in NYC tomorrow?",
                    "Will BAYC floor exceed 100 ETH?",
                    "Will hurricane hit Florida?"
                ],
                "invalid": [
                    "Will NFTs be popular?",
                    "Will weather be nice?"
                ]
            }
        }
    }

    def __init__(self, openrouter_api_key: str):
        self.api_key = openrouter_api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "openai/gpt-4o-mini"

    async def transform_to_valid_market(
        self,
        text: str,
        force_oracle: Optional[str] = None,
        optimize: bool = True
    ) -> Dict[str, Any]:
        """
        Transform ANY text into a valid prediction market

        Args:
            text: Original text (can be invalid)
            force_oracle: Force specific oracle provider
            optimize: If True, transform invalid questions to valid ones

        Returns:
            Transformed market with explanation
        """

        # First, try the original text
        qualification = await self._qualify_original(text)

        if qualification.is_prediction_market and not optimize:
            # Original is valid, route it
            routing = await self._route_to_oracle(text, force_oracle)
            return {
                "success": True,
                "original_valid": True,
                "transformed_question": text,
                "oracle": routing.oracle_provider,
                "explanation": routing.reasoning,
                "transformation": None
            }

        if not qualification.is_prediction_market and not optimize:
            # Not valid and optimization disabled
            return {
                "success": False,
                "original_valid": False,
                "reason": qualification.reasoning,
                "suggestion": "Enable optimize=True to transform into valid market"
            }

        # Transform the invalid question into valid markets
        transformations = await self._generate_transformations(text, qualification)

        return {
            "success": True,
            "original_valid": False,
            "original_issue": qualification.reasoning,
            "transformations": transformations,
            "explanation": self._explain_transformations(transformations)
        }

    async def _qualify_original(self, text: str) -> PredictionQualification:
        """Check if original text is a valid prediction market"""

        prompt = f"""
        Is this a valid prediction market question?

        Text: "{text}"

        A valid prediction market must have:
        1. Clear, measurable outcome (not subjective)
        2. Specific timeframe or trigger
        3. Data that oracles can actually verify

        Return JSON:
        {{
            "is_prediction_market": boolean,
            "confidence": 0.0-1.0,
            "reasoning": "why valid or invalid",
            "issues": ["list", "of", "problems"] or []
        }}
        """

        response = await self._call_ai(prompt)
        return PredictionQualification(
            is_prediction_market=response.get("is_prediction_market", False),
            confidence=response.get("confidence", 0.0),
            reasoning=response.get("reasoning", ""),
            has_clear_outcome=True,  # Simplified
            is_measurable=True,
            is_verifiable=True,
            has_timeframe=True,
            outcomes=["Yes", "No"],
            verification_method="Oracle"
        )

    async def _generate_transformations(
        self,
        text: str,
        qualification: PredictionQualification
    ) -> list:
        """
        Generate multiple valid prediction markets from invalid text
        """

        prompt = f"""
        Transform this text into valid prediction markets for different oracles.

        Original text: "{text}"
        Issues: {qualification.reasoning}

        Generate transformations for each oracle type:

        1. PRICE MARKET (Chainlink/Pyth):
        - Must involve measurable price threshold
        - Add specific asset, amount, and date

        2. EVENT MARKET (UMA):
        - Must be verifiable by news sources
        - Add specific trigger and deadline

        3. SPORTS MARKET (Chainlink):
        - Must involve team/game outcome
        - Add specific match and date

        4. WEATHER MARKET (API3):
        - Must involve measurable weather metric
        - Add location and date

        5. SOCIAL MARKET (Band):
        - Must involve measurable social metric
        - Add specific account and threshold

        For each transformation, return:
        {{
            "oracle": "provider_name",
            "transformed_question": "new valid question",
            "explanation": "what changed and why",
            "confidence": 0.0-1.0,
            "data_source": "where data comes from"
        }}

        Return array of 5 transformations in JSON.
        """

        response = await self._call_ai(prompt)
        return response if isinstance(response, list) else []

    def _explain_transformations(self, transformations: list) -> str:
        """Generate human-readable explanation of transformations"""

        if not transformations:
            return "No valid transformations could be generated."

        explanation = "Here's how we can transform your question into valid prediction markets:\n\n"

        for i, t in enumerate(transformations, 1):
            explanation += f"{i}. {t['oracle'].upper()} Oracle:\n"
            explanation += f"   Question: {t['transformed_question']}\n"
            explanation += f"   Why it works: {t['explanation']}\n"
            explanation += f"   Data source: {t['data_source']}\n\n"

        return explanation

    async def explain_oracle_selection(self, question: str) -> Dict[str, Any]:
        """
        Detailed explanation of WHY a specific oracle was selected
        """

        prompt = f"""
        Explain the oracle selection for this prediction market:

        Question: "{question}"

        For EACH oracle, explain:
        1. CAN IT RESOLVE THIS? (Yes/No and why)
        2. HOW WOULD IT RESOLVE? (Data source and method)
        3. PROS AND CONS for this specific question
        4. ESTIMATED COST AND LATENCY

        Oracles to evaluate:
        - Chainlink: Aggregated price feeds, sports data, weather
        - Pyth: Real-time crypto/stock prices
        - UMA: Human-verified events (2hr dispute period)
        - Band: Any API endpoint
        - API3: Direct first-party APIs

        Return JSON:
        {{
            "selected_oracle": "best_choice",
            "reasoning": "detailed explanation",
            "oracle_evaluations": {{
                "chainlink": {{"can_resolve": bool, "how": "", "pros": [], "cons": [], "cost": 0.0}},
                "pyth": {{"can_resolve": bool, "how": "", "pros": [], "cons": [], "cost": 0.0}},
                "uma": {{"can_resolve": bool, "how": "", "pros": [], "cons": [], "cost": 0.0}},
                "band": {{"can_resolve": bool, "how": "", "pros": [], "cons": [], "cost": 0.0}},
                "api3": {{"can_resolve": bool, "how": "", "pros": [], "cons": [], "cost": 0.0}}
            }}
        }}
        """

        response = await self._call_ai(prompt)
        return response

    async def get_oracle_examples(self, oracle_provider: str) -> Dict[str, Any]:
        """
        Get specific examples of what an oracle can and cannot do
        """

        oracle = oracle_provider.upper()
        if oracle in self.ORACLE_CAPABILITIES_DETAILED:
            return self.ORACLE_CAPABILITIES_DETAILED[oracle]

        return {
            "error": f"Unknown oracle provider: {oracle_provider}"
        }

    async def suggest_best_oracle_for_category(self, category: str) -> Dict[str, Any]:
        """
        Suggest the best oracle for a specific category of predictions
        """

        categories_to_oracles = {
            "crypto_prices": {
                "best": "pyth",
                "reason": "Pyth has sub-second latency for crypto prices",
                "alternatives": ["chainlink"],
                "examples": ["BTC > $100k?", "ETH > $10k?"]
            },
            "sports": {
                "best": "chainlink",
                "reason": "Chainlink has official partnerships with sports data providers",
                "alternatives": ["uma"],
                "examples": ["Lakers win?", "Super Bowl winner?"]
            },
            "elections": {
                "best": "uma",
                "reason": "UMA uses human verification for political outcomes",
                "alternatives": ["band"],
                "examples": ["Presidential winner?", "Senate control?"]
            },
            "weather": {
                "best": "api3",
                "reason": "API3 has direct NOAA integration",
                "alternatives": ["chainlink"],
                "examples": ["Rain tomorrow?", "Hurricane landfall?"]
            },
            "social_media": {
                "best": "band",
                "reason": "Band can call any API including Twitter/YouTube",
                "alternatives": ["uma"],
                "examples": ["1M followers?", "Video views?"]
            },
            "corporate_events": {
                "best": "uma",
                "reason": "UMA can verify announcements from official sources",
                "alternatives": ["band"],
                "examples": ["Product launch?", "Earnings beat?"]
            },
            "nft": {
                "best": "api3",
                "reason": "API3 has direct OpenSea/Blur integration",
                "alternatives": ["chainlink"],
                "examples": ["Floor price > 10 ETH?", "Collection volume?"]
            }
        }

        if category.lower() in categories_to_oracles:
            return categories_to_oracles[category.lower()]

        return {
            "error": f"Unknown category: {category}",
            "available_categories": list(categories_to_oracles.keys())
        }

    async def _route_to_oracle(
        self,
        text: str,
        force_oracle: Optional[str] = None
    ) -> OracleRouting:
        """Route to specific oracle with explanation"""

        if force_oracle:
            # Forced oracle selection
            return OracleRouting(
                oracle_provider=force_oracle,
                reasoning=f"Forced to use {force_oracle} oracle",
                confidence=1.0,
                data_type="custom",
                update_frequency="on_demand",
                resolution_method="direct",
                expected_latency_ms=1000,
                estimated_cost_usd=1.0,
                resolution_sources=[]
            )

        # AI-based routing
        evaluation = await self.explain_oracle_selection(text)

        return OracleRouting(
            oracle_provider=evaluation.get("selected_oracle", "chainlink"),
            reasoning=evaluation.get("reasoning", ""),
            confidence=0.9,
            data_type="custom",
            update_frequency="on_demand",
            resolution_method="direct",
            expected_latency_ms=1000,
            estimated_cost_usd=1.0,
            resolution_sources=[]
        )

    async def _call_ai(self, prompt: str) -> Dict[str, Any]:
        """Call OpenRouter AI API"""

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
                            "content": "You are an expert in prediction markets and oracles."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2000,
                    "response_format": {"type": "json_object"}
                },
                timeout=30.0
            )

            if response.status_code == 200:
                result = response.json()
                return json.loads(result["choices"][0]["message"]["content"])
            else:
                raise Exception(f"AI API error: {response.status_code}")


# Example usage
async def example():
    optimizer = MarketOptimizerService("your-api-key")

    # Example 1: Invalid subjective question
    result = await optimizer.transform_to_valid_market(
        "Will the new iPhone be good?",
        optimize=True
    )
    print("Transformations:", result['transformations'])

    # Example 2: Explain oracle selection
    explanation = await optimizer.explain_oracle_selection(
        "Will Bitcoin exceed $100,000 by December 31, 2024?"
    )
    print("Selected:", explanation['selected_oracle'])
    print("Why:", explanation['reasoning'])

    # Example 3: Force specific oracle
    result = await optimizer.transform_to_valid_market(
        "Something about weather",
        force_oracle="api3",
        optimize=True
    )
    print("Forced to API3:", result)