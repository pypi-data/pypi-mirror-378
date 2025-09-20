#!/usr/bin/env python3
"""
Oracle Routing Test CLI
Tests AI-powered detection and routing of prediction market opportunities
"""

import asyncio
import os
import sys
import json
from typing import Dict, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
import argparse

from openoracle import (
    OpenOracleAPI,
    OracleConfig,
    OracleProvider,
    DataCategory
)

# Import OpenAI for AI analysis
try:
    import openai
except ImportError:
    print("Please install openai: pip install openai")
    sys.exit(1)

class PredictionMarketAnalyzer:
    """Analyzes text to determine if it's suitable for prediction markets"""

    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)

    async def analyze_text(self, text: str) -> Dict:
        """
        Analyze text to determine:
        1. Is this suitable for a prediction market?
        2. What type of prediction market (sports, politics, crypto, weather, etc.)?
        3. What oracle provider should handle it?
        4. Extract key parameters (event, outcome options, timeframe)
        """

        prompt = f"""
        Analyze the following text and determine if it's suitable for a prediction market.

        Text: "{text}"

        Return a JSON object with:
        {{
            "is_prediction_market": boolean,
            "confidence": float (0-1),
            "market_type": string (sports/politics/crypto/weather/economic/other),
            "oracle_provider": string (chainlink/pyth/uma/api3/custom),
            "event_description": string,
            "outcome_options": list[string],
            "resolution_date": string (ISO format estimate),
            "data_category": string (price/sports/weather/custom),
            "reasoning": string
        }}

        Consider these factors:
        - Clear, measurable outcomes
        - Specific timeframe
        - Verifiable resolution
        - Binary or multiple discrete outcomes
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in prediction markets and oracle systems."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )

            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"AI analysis error: {e}")
            return {
                "is_prediction_market": False,
                "confidence": 0.0,
                "reasoning": f"Analysis failed: {str(e)}"
            }

class OracleRouter:
    """Routes prediction markets to appropriate oracle providers"""

    def __init__(self):
        self.oracle_api = None
        self.provider_configs = {
            OracleProvider.CHAINLINK: {
                "categories": [DataCategory.PRICE, DataCategory.SPORTS],
                "min_confidence": 0.7
            },
            OracleProvider.PYTH: {
                "categories": [DataCategory.PRICE],
                "min_confidence": 0.8
            },
            OracleProvider.UMA: {
                "categories": [DataCategory.CUSTOM],
                "min_confidence": 0.6
            },
            OracleProvider.API3: {
                "categories": [DataCategory.WEATHER],
                "min_confidence": 0.7
            }
        }

    async def initialize(self):
        """Initialize Oracle API connection"""
        config = OracleConfig(
            api_key=os.getenv("OPENORACLE_API_KEY", "test-key"),
            network="testnet"
        )
        self.oracle_api = OpenOracleAPI(config)
        await self.oracle_api.connect()

    async def route_to_oracle(self, analysis: Dict) -> Optional[Dict]:
        """Route the prediction market to appropriate oracle"""

        if not analysis.get("is_prediction_market"):
            return {
                "routed": False,
                "reason": "Not suitable for prediction market",
                "confidence": analysis.get("confidence", 0)
            }

        # Map analysis to oracle provider
        provider_str = analysis.get("oracle_provider", "").upper()
        if provider_str == "CHAINLINK":
            provider = OracleProvider.CHAINLINK
        elif provider_str == "PYTH":
            provider = OracleProvider.PYTH
        elif provider_str == "UMA":
            provider = OracleProvider.UMA
        elif provider_str == "API3":
            provider = OracleProvider.API3
        else:
            provider = OracleProvider.CHAINLINK  # Default

        # Map data category
        category_map = {
            "price": DataCategory.PRICE,
            "sports": DataCategory.SPORTS,
            "weather": DataCategory.WEATHER,
            "custom": DataCategory.CUSTOM
        }
        category = category_map.get(
            analysis.get("data_category", "custom").lower(),
            DataCategory.CUSTOM
        )

        # Check if provider supports this category
        provider_config = self.provider_configs.get(provider)
        if provider_config and category not in provider_config["categories"]:
            # Find alternative provider
            for alt_provider, alt_config in self.provider_configs.items():
                if category in alt_config["categories"]:
                    provider = alt_provider
                    break

        # Create oracle request
        try:
            request_data = {
                "provider": provider,
                "category": category,
                "pair": analysis.get("event_description", "")[:50],  # Truncate for pair field
                "metadata": {
                    "event": analysis.get("event_description"),
                    "outcomes": analysis.get("outcome_options", []),
                    "resolution_date": analysis.get("resolution_date"),
                    "confidence": analysis.get("confidence"),
                    "market_type": analysis.get("market_type")
                }
            }

            # Simulate oracle request (in real scenario, would submit to oracle)
            result = {
                "routed": True,
                "provider": provider.value,
                "category": category.value,
                "request_data": request_data,
                "estimated_resolution": analysis.get("resolution_date"),
                "confidence": analysis.get("confidence")
            }

            # If we had a real oracle connection:
            # price_feed = await self.oracle_api.get_price_feed(
            #     provider=provider,
            #     pair=request_data["pair"]
            # )
            # result["current_feed"] = price_feed

            return result

        except Exception as e:
            return {
                "routed": False,
                "reason": f"Oracle routing failed: {str(e)}",
                "confidence": analysis.get("confidence", 0)
            }

    async def close(self):
        """Close Oracle API connection"""
        if self.oracle_api:
            await self.oracle_api.close()

async def test_prediction_market_routing(text: str, verbose: bool = False):
    """Main test function"""

    # Get OpenAI API key
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return

    print(f"\n{'='*60}")
    print("PREDICTION MARKET ORACLE ROUTING TEST")
    print(f"{'='*60}\n")

    print(f"Input Text: {text[:200]}{'...' if len(text) > 200 else ''}\n")

    # Step 1: AI Analysis
    print("Step 1: AI Analysis...")
    analyzer = PredictionMarketAnalyzer(openai_key)
    analysis = await analyzer.analyze_text(text)

    if verbose:
        print(f"Analysis Result:")
        print(json.dumps(analysis, indent=2))
    else:
        print(f"  - Is Prediction Market: {analysis.get('is_prediction_market')}")
        print(f"  - Confidence: {analysis.get('confidence', 0):.2%}")
        print(f"  - Market Type: {analysis.get('market_type', 'N/A')}")
        print(f"  - Oracle Provider: {analysis.get('oracle_provider', 'N/A')}")

    print(f"\nReasoning: {analysis.get('reasoning', 'No reasoning provided')}\n")

    # Step 2: Oracle Routing
    print("Step 2: Oracle Routing...")
    router = OracleRouter()
    await router.initialize()

    routing_result = await router.route_to_oracle(analysis)

    if routing_result.get("routed"):
        print(f"  ✅ Successfully routed to oracle!")
        print(f"  - Provider: {routing_result.get('provider')}")
        print(f"  - Category: {routing_result.get('category')}")
        print(f"  - Resolution: {routing_result.get('estimated_resolution')}")

        if verbose and "request_data" in routing_result:
            print(f"\nRequest Data:")
            print(json.dumps(routing_result["request_data"], indent=2, default=str))
    else:
        print(f"  ❌ Not routed to oracle")
        print(f"  - Reason: {routing_result.get('reason')}")

    await router.close()

    print(f"\n{'='*60}\n")

    return analysis, routing_result

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Test Oracle Routing for Prediction Markets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Will the S&P 500 close above 5000 by end of month?"
  %(prog)s "Who will win the Lakers vs Warriors game tonight?"
  %(prog)s "Will it rain in NYC tomorrow?"
  %(prog)s -f sample.txt  # Read from file
  %(prog)s -t  # Run test suite
        """
    )

    parser.add_argument(
        "text",
        nargs="?",
        help="Text to analyze for prediction market potential"
    )
    parser.add_argument(
        "-f", "--file",
        help="Read text from file"
    )
    parser.add_argument(
        "-t", "--test",
        action="store_true",
        help="Run test suite with sample scenarios"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed output"
    )

    args = parser.parse_args()

    # Determine input text
    if args.test:
        # Run test suite
        test_scenarios = [
            "Will Bitcoin reach $100,000 by December 31, 2024?",
            "The weather tomorrow will be sunny with no rain",
            "Who will win the 2024 NBA championship?",
            "Will the Federal Reserve raise interest rates in the next meeting?",
            "I think stocks are going up",  # Vague, should fail
            "The new iPhone will be released next month",  # Not really predictable
            "Will SpaceX successfully land on Mars by 2030?",
            "How many hurricanes will hit Florida this season?",
        ]

        async def run_tests():
            print("\n🧪 RUNNING TEST SUITE\n")
            results = []
            for i, scenario in enumerate(test_scenarios, 1):
                print(f"Test {i}/{len(test_scenarios)}: {scenario[:50]}...")
                analysis, routing = await test_prediction_market_routing(
                    scenario,
                    verbose=args.verbose
                )
                results.append({
                    "scenario": scenario,
                    "is_market": analysis.get("is_prediction_market"),
                    "routed": routing.get("routed"),
                    "confidence": analysis.get("confidence", 0)
                })
                await asyncio.sleep(1)  # Rate limiting

            # Summary
            print("\n📊 TEST SUMMARY")
            print(f"{'='*60}")
            successful = sum(1 for r in results if r["is_market"] and r["routed"])
            print(f"Successful routings: {successful}/{len(results)}")
            print("\nDetails:")
            for r in results:
                status = "✅" if r["is_market"] and r["routed"] else "❌"
                print(f"{status} {r['scenario'][:50]}... (confidence: {r['confidence']:.2%})")

        asyncio.run(run_tests())

    elif args.file:
        try:
            with open(args.file, 'r') as f:
                text = f.read().strip()
            if text:
                asyncio.run(test_prediction_market_routing(text, args.verbose))
            else:
                print("Error: File is empty")
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found")
        except Exception as e:
            print(f"Error reading file: {e}")

    elif args.text:
        asyncio.run(test_prediction_market_routing(args.text, args.verbose))

    else:
        # Interactive mode
        print("Enter text to analyze (or 'quit' to exit):")
        while True:
            try:
                text = input("> ").strip()
                if text.lower() in ['quit', 'exit', 'q']:
                    break
                if text:
                    asyncio.run(test_prediction_market_routing(text, args.verbose))
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except EOFError:
                break

if __name__ == "__main__":
    main()