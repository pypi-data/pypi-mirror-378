#!/usr/bin/env python3
"""
Test CLI for Oracle Text Analysis and Routing
Demonstrates SDK capabilities for analyzing text and routing to oracles
"""

import asyncio
import sys
import json
from typing import Optional

from openoracle import (
    OpenOracleRouter,
    OracleConfig,
    DataCategory
)

async def test_text_analysis(router: OpenOracleRouter, text: str):
    """Test text analysis capabilities"""
    print(f"\n{'='*60}")
    print("TEXT ANALYSIS")
    print(f"{'='*60}")
    print(f"Input: {text[:100]}{'...' if len(text) > 100 else ''}\n")

    # Analyze the text
    analysis = await router.analyze_text(text)

    print("Analysis Results:")
    print(f"  ✓ Is Prediction Market: {analysis['is_prediction_market']}")
    print(f"  ✓ Category: {analysis['category']}")
    print(f"  ✓ Confidence: {analysis['confidence']:.2%}")
    print(f"  ✓ Market Type: {analysis['market_type']}")
    print(f"  ✓ Market Labels: {', '.join(analysis['market_labels'])}")
    print(f"  ✓ Recommended Oracle: {analysis['recommended_oracle']}")

    if analysis['requirements']:
        print("\nExtracted Requirements:")
        for key, value in analysis['requirements'].items():
            if value and key != 'original_question':
                print(f"  • {key}: {value}")

    if analysis['resolution_sources']:
        print(f"\nResolution Sources: {', '.join(analysis['resolution_sources'])}")

    return analysis

async def test_oracle_routing(router: OpenOracleRouter, text: str):
    """Test oracle routing capabilities"""
    print(f"\n{'='*60}")
    print("ORACLE ROUTING")
    print(f"{'='*60}")

    # Route to oracle
    response = await router.route_text_to_oracle(text)

    if response.can_resolve:
        print(f"✅ Successfully routed to oracle!")
        print(f"\nRouting Decision:")
        print(f"  • Selected Oracle: {response.selected_oracle.value if response.selected_oracle else 'None'}")
        print(f"  • Confidence: {response.confidence_score:.2%}")
        print(f"  • Market Labels: {', '.join(response.market_labels) if response.market_labels else 'None'}")
        print(f"  • Data Type: {response.data_type.value if response.data_type else 'None'}")
        print(f"  • Resolution Method: {response.resolution_method}")
        print(f"\nReasoning: {response.reasoning}")

        if response.metadata:
            print(f"\nMetadata:")
            print(f"  • Market Type: {response.metadata.get('market_type')}")
            if response.metadata.get('requirements', {}).get('assets'):
                print(f"  • Assets: {', '.join(response.metadata['requirements']['assets'])}")

        if response.alternatives:
            print(f"\nAlternative Oracles: {', '.join([alt.value for alt in response.alternatives])}")
    else:
        print(f"❌ Not suitable for prediction market")
        print(f"Reason: {response.reasoning}")

    return response

async def main():
    """Main test function"""

    # Test scenarios
    test_cases = [
        # Sports
        "Will the Lakers beat the Warriors in tonight's game?",
        "Who will win the 2024 Super Bowl?",

        # Politics
        "Will Biden win the 2024 presidential election?",
        "Will the Democrats retain control of the Senate?",

        # Crypto/Finance
        "Will Bitcoin exceed $100,000 by December 31, 2024?",
        "Will ETH price be above $5000 by end of month?",
        "Will the S&P 500 close above 5000 points this week?",

        # Technology
        "Will Apple release a new iPhone by September 2024?",
        "Will OpenAI announce GPT-5 this year?",

        # Entertainment
        "Will Oppenheimer win Best Picture at the Oscars?",
        "Will Taylor Swift's next album go #1?",

        # Weather/Events
        "Will it rain in New York tomorrow?",
        "Will there be a hurricane in Florida this season?",

        # Invalid/Vague
        "The weather is nice today",
        "I think stocks will go up",
        "What do you think about crypto?"
    ]

    # Initialize router
    router = OpenOracleRouter(enable_ai_routing=False)

    print("\n" + "="*60)
    print("ORACLE TEXT ROUTING TEST SUITE")
    print("Testing text analysis and oracle routing capabilities")
    print("="*60)

    # Run tests
    for i, text in enumerate(test_cases, 1):
        print(f"\n\n{'='*60}")
        print(f"TEST CASE {i}/{len(test_cases)}")
        print(f"{'='*60}")

        # Analyze text
        analysis = await test_text_analysis(router, text)

        # Only route if it's a valid prediction market
        if analysis['is_prediction_market']:
            routing = await test_oracle_routing(router, text)
        else:
            print(f"\n⚠️ Skipping routing - not a valid prediction market")

    # Summary
    print(f"\n\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total test cases: {len(test_cases)}")

    valid_markets = sum(1 for text in test_cases
                       if router.analyze_text(text)['is_prediction_market'])
    print(f"Valid prediction markets: {valid_markets}/{len(test_cases)}")

    # List oracle capabilities
    print(f"\n{'='*60}")
    print("ORACLE CAPABILITIES")
    print(f"{'='*60}")

    from openoracle import OracleProvider
    for provider in [OracleProvider.CHAINLINK, OracleProvider.PYTH, OracleProvider.UMA]:
        capabilities = router.get_oracle_capabilities(provider)
        if 'error' not in capabilities:
            print(f"\n{provider.value.upper()}:")
            print(f"  • Categories: {', '.join([cat.value for cat in capabilities['categories']])}")
            print(f"  • Reliability: {capabilities['reliability']:.0%}")
            print(f"  • Latency: {capabilities['latency_ms']}ms")
            print(f"  • Chains: {', '.join(capabilities['chains'][:3])}...")

if __name__ == "__main__":
    asyncio.run(main())