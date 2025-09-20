#!/usr/bin/env python3
"""
CLI Tool for Creating Prediction Markets
Simple command-line interface for the prediction market API
"""

import asyncio
import os
import sys
import json
import argparse
from decimal import Decimal
from datetime import datetime, timedelta
import httpx

# API Configuration
API_BASE_URL = os.getenv("MARKET_API_URL", "http://localhost:8000")

async def create_single_market(question: str, wallet: str, liquidity: float):
    """Create a single prediction market"""

    endpoint = f"{API_BASE_URL}/api/v1/markets/create"

    payload = {
        "question": question,
        "creator_wallet": wallet,
        "initial_liquidity_usdc": liquidity,
        "resolution_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
    }

    print(f"\n{'='*60}")
    print("CREATING PREDICTION MARKET")
    print(f"{'='*60}")
    print(f"Question: {question}")
    print(f"Liquidity: ${liquidity} USDC")
    print(f"Creator: {wallet[:10]}...{wallet[-8:]}")
    print("\nProcessing...\n")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                endpoint,
                json=payload,
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()

                print("✅ MARKET CREATED SUCCESSFULLY!")
                print(f"\n📊 Market Details:")
                print(f"  • ID: {data['market_id']}")
                print(f"  • Title: {data['title']}")
                print(f"  • Outcomes: {', '.join(data['outcomes'])}")
                print(f"  • Oracle: {data['oracle_provider'].upper()}")
                print(f"  • Resolution: {data['resolution_date'][:10]}")

                print(f"\n💰 Cost Breakdown:")
                costs = data['costs']
                print(f"  • Liquidity: ${costs['initial_liquidity']:.2f}")
                print(f"  • Oracle Fee: ${costs['oracle_fee']:.2f}")
                print(f"  • Gas Fee: ${costs['gas_fee']:.2f}")
                print(f"  • Total: ${costs['total']:.2f}")

                print(f"\n🔗 Market URL: {data['market_url']}")
                print(f"📝 Transaction: {data['transaction_hash']}")

                return data
            else:
                error = response.json()
                print(f"❌ Failed: {error.get('detail', 'Unknown error')}")
                return None

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

async def analyze_text(text: str):
    """Analyze text for prediction market suitability"""

    endpoint = f"{API_BASE_URL}/api/v1/markets/analyze"

    print(f"\n{'='*60}")
    print("ANALYZING TEXT")
    print(f"{'='*60}")
    print(f"Text: {text[:100]}{'...' if len(text) > 100 else ''}\n")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                endpoint,
                params={"text": text},
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()

                if data['is_prediction_market']:
                    print("✅ SUITABLE FOR PREDICTION MARKET")
                    print(f"\n📊 Analysis:")
                    print(f"  • Confidence: {data['confidence']:.1%}")
                    print(f"  • Outcomes: {', '.join(data['outcomes'])}")
                    print(f"  • Timeframe: {data.get('timeframe', 'Not specified')}")
                    print(f"  • Oracle: {data['oracle_provider'].upper()}")
                    print(f"  • Est. Cost: ${data['estimated_cost']:.2f}")
                    print(f"\n💡 Reasoning: {data['reasoning']}")
                    print(f"🔍 Resolution Sources: {', '.join(data['resolution_sources'])}")
                else:
                    print("❌ NOT SUITABLE FOR PREDICTION MARKET")
                    print(f"\nReason: {data['reasoning']}")
                    print(f"Confidence: {data['confidence']:.1%}")

                return data
            else:
                print(f"❌ Analysis failed: {response.status_code}")
                return None

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

async def batch_create_markets(markets: list):
    """Create multiple markets in batch"""

    endpoint = f"{API_BASE_URL}/api/v1/markets/batch"

    print(f"\n{'='*60}")
    print(f"CREATING {len(markets)} MARKETS IN BATCH")
    print(f"{'='*60}\n")

    payload = {
        "markets": markets
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                endpoint,
                json=payload,
                timeout=60.0
            )

            if response.status_code == 200:
                data = response.json()

                print(f"📊 Batch Results:")
                print(f"  • Total: {data['total_markets']}")
                print(f"  • Successful: {data['successful']} ✅")
                print(f"  • Failed: {data['failed']} ❌")
                print(f"  • Batch ID: {data['batch_id']}")

                print(f"\n📋 Individual Results:")
                for i, result in enumerate(data['results'], 1):
                    if result['success']:
                        print(f"  {i}. ✅ {result['title']} - {result['market_id']}")
                    else:
                        print(f"  {i}. ❌ Failed: {result.get('error', 'Unknown error')}")

                return data
            else:
                print(f"❌ Batch creation failed: {response.status_code}")
                return None

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

async def get_creator_stats(address: str):
    """Get statistics for a market creator"""

    endpoint = f"{API_BASE_URL}/api/v1/markets/stats/{address}"

    print(f"\n{'='*60}")
    print(f"CREATOR STATISTICS")
    print(f"{'='*60}")
    print(f"Address: {address[:10]}...{address[-8:]}\n")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint, timeout=30.0)

            if response.status_code == 200:
                stats = response.json()

                print(f"📊 Statistics:")
                print(f"  • Total Markets: {stats['total_markets']}")
                print(f"  • Successful: {stats['successful_markets']}")
                print(f"  • Total Liquidity: ${stats['total_liquidity']:,.2f}")
                print(f"  • Avg Confidence: {stats['average_confidence']:.1%}")

                return stats
            else:
                print(f"❌ Failed to get stats: {response.status_code}")
                return None

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def main():
    """Main CLI interface"""

    parser = argparse.ArgumentParser(
        description="Create prediction markets with AI-powered oracle routing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create "Will Bitcoin exceed $100k by EOY?" --wallet 0x123... --liquidity 1000
  %(prog)s analyze "Will it rain tomorrow?"
  %(prog)s stats 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7
  %(prog)s demo
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a prediction market")
    create_parser.add_argument("question", help="The prediction market question")
    create_parser.add_argument("--wallet", required=True, help="Creator wallet address")
    create_parser.add_argument("--liquidity", type=float, default=100.0, help="Initial liquidity in USDC")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze text for suitability")
    analyze_parser.add_argument("text", help="Text to analyze")

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Get creator statistics")
    stats_parser.add_argument("address", help="Creator wallet address")

    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run demo markets")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute commands
    if args.command == "create":
        asyncio.run(create_single_market(
            args.question,
            args.wallet,
            args.liquidity
        ))

    elif args.command == "analyze":
        asyncio.run(analyze_text(args.text))

    elif args.command == "stats":
        asyncio.run(get_creator_stats(args.address))

    elif args.command == "demo":
        # Demo markets
        demo_markets = [
            "Will the Lakers win the championship this year?",
            "Will Bitcoin reach $150,000 by June 2025?",
            "Will SpaceX land on Mars before 2030?",
            "Will the Fed cut rates in Q1 2025?",
            "Will it snow in NYC on Christmas Day 2024?"
        ]

        print("\n🎮 DEMO MODE - Analyzing sample markets\n")

        for question in demo_markets:
            await asyncio.sleep(1)  # Rate limiting
            await analyze_text(question)
            print("\n" + "-"*60 + "\n")

if __name__ == "__main__":
    main()