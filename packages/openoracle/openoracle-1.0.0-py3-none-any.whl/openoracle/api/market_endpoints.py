"""
FastAPI Endpoints for Prediction Market Creation
Simple API for creating prediction markets with one call
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
from decimal import Decimal
import logging

from ..schemas.prediction_market_schemas import (
    CreateMarketRequest,
    CreateMarketResponse,
    BatchMarketRequest,
    BatchMarketResponse,
    PredictionMarketRequest,
    MarketValidator
)
from ..services.market_creation_service import MarketCreationService

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="OpenOracle Prediction Market API",
    description="Create prediction markets with AI-powered oracle routing",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize service (would use dependency injection in production)
def get_market_service() -> MarketCreationService:
    """Get market creation service instance"""
    return MarketCreationService(
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_key=os.getenv("SUPABASE_KEY"),
        web3_rpc_url=os.getenv("WEB3_RPC_URL", "https://mainnet.base.org")
    )

# ============ Endpoints ============

@app.post("/api/v1/markets/create", response_model=CreateMarketResponse)
async def create_market(
    request: CreateMarketRequest,
    background_tasks: BackgroundTasks,
    service: MarketCreationService = Depends(get_market_service)
):
    """
    Create a single prediction market

    This endpoint:
    1. Analyzes if the question is suitable for a prediction market
    2. Routes to the best oracle provider
    3. Generates market parameters
    4. Creates contract call data for PollyPoll
    5. Logs everything to database

    Example:
    ```
    POST /api/v1/markets/create
    {
        "question": "Will Bitcoin exceed $100,000 by December 31, 2024?",
        "creator_wallet": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
        "initial_liquidity_usdc": 1000.0,
        "resolution_date": "2024-12-31T23:59:59Z"
    }
    ```
    """
    try:
        # Validate question
        if not MarketValidator.validate_question(request.question):
            raise HTTPException(
                status_code=400,
                detail="Invalid question format. Must be 10-500 chars and end with '?'"
            )

        # Validate liquidity
        if not MarketValidator.validate_liquidity(Decimal(str(request.initial_liquidity_usdc))):
            raise HTTPException(
                status_code=400,
                detail="Minimum liquidity is 10 USDC"
            )

        # Create internal request
        internal_request = PredictionMarketRequest(
            text=request.question,
            creator_address=request.creator_wallet,
            initial_liquidity=Decimal(str(request.initial_liquidity_usdc)),
            resolution_time=request.resolution_date
        )

        # Process market creation
        result = await service.create_prediction_market(internal_request)

        if not result.success:
            raise HTTPException(
                status_code=400,
                detail=result.qualification.reasoning
            )

        # Create response
        return CreateMarketResponse(
            success=True,
            market_id=result.market_id,
            transaction_hash=result.contract_data.encoded_data[:66],  # Mock for now
            market_url=f"https://pollypoll.com/markets/{result.market_id}",
            title=result.parameters.market_title,
            outcomes=result.parameters.outcomes,
            oracle_provider=result.routing.oracle_provider,
            resolution_date=result.parameters.resolution_timestamp.isoformat(),
            costs={
                "initial_liquidity": float(request.initial_liquidity_usdc),
                "oracle_fee": float(result.routing.estimated_cost_usd),
                "gas_fee": float(result.contract_data.estimated_gas * 0.000001),
                "total": float(result.estimated_total_cost)
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Market creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/markets/batch", response_model=BatchMarketResponse)
async def create_batch_markets(
    request: BatchMarketRequest,
    service: MarketCreationService = Depends(get_market_service)
):
    """
    Create multiple prediction markets in batch

    Efficiently processes multiple markets with a single API call.
    """
    batch_id = request.batch_id or str(uuid.uuid4())
    results = []
    successful = 0
    failed = 0

    for market_request in request.markets:
        try:
            # Process each market
            result = await create_market(market_request, BackgroundTasks(), service)
            results.append(result)
            successful += 1
        except Exception as e:
            results.append(
                CreateMarketResponse(
                    success=False,
                    error=str(e),
                    error_code="BATCH_ITEM_FAILED",
                    title="",
                    outcomes=[],
                    oracle_provider="",
                    resolution_date="",
                    costs={}
                )
            )
            failed += 1

    return BatchMarketResponse(
        batch_id=batch_id,
        total_markets=len(request.markets),
        successful=successful,
        failed=failed,
        results=results
    )

@app.get("/api/v1/markets/analyze")
async def analyze_text(
    text: str,
    service: MarketCreationService = Depends(get_market_service)
):
    """
    Analyze text to determine if it's suitable for a prediction market

    Returns analysis without creating a market.
    """
    try:
        # Quick qualification check
        qualification = await service._qualify_prediction_market(text)

        if qualification.is_prediction_market:
            # Get routing information
            routing = await service._route_to_oracle(text, qualification)

            return {
                "is_prediction_market": True,
                "confidence": qualification.confidence,
                "reasoning": qualification.reasoning,
                "outcomes": qualification.outcomes,
                "timeframe": qualification.timeframe,
                "oracle_provider": routing.oracle_provider,
                "oracle_reasoning": routing.reasoning,
                "estimated_cost": float(routing.estimated_cost_usd),
                "resolution_sources": routing.resolution_sources
            }
        else:
            return {
                "is_prediction_market": False,
                "confidence": qualification.confidence,
                "reasoning": qualification.reasoning
            }

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/markets/stats/{creator_address}")
async def get_creator_stats(
    creator_address: str,
    service: MarketCreationService = Depends(get_market_service)
):
    """
    Get statistics for a market creator

    Returns aggregated stats from the database.
    """
    try:
        # Call Supabase RPC function
        stats = await service.supabase.rpc(
            "get_market_stats",
            {"address": creator_address}
        )

        if stats:
            return stats[0]
        else:
            return {
                "total_markets": 0,
                "successful_markets": 0,
                "total_liquidity": 0.0,
                "average_confidence": 0.0
            }

    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "OpenOracle Market API"}

# ============ WebSocket for Real-time Updates ============

from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws/markets/{market_id}")
async def market_updates(
    websocket: WebSocket,
    market_id: str,
    service: MarketCreationService = Depends(get_market_service)
):
    """
    WebSocket endpoint for real-time market updates

    Streams oracle data and market status changes.
    """
    await websocket.accept()

    try:
        while True:
            # Get latest market data from database
            market_data = await service.supabase.select(
                "market_analysis_logs",
                filters={"market_id": market_id},
                limit=1
            )

            if market_data:
                await websocket.send_json({
                    "type": "market_update",
                    "data": market_data[0]
                })

            # Wait before next update
            await asyncio.sleep(5)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for market {market_id}")

# ============ Startup and Shutdown Events ============

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("OpenOracle Market API starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("OpenOracle Market API shutting down...")

# ============ Error Handlers ============

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle value errors"""
    return {
        "error": str(exc),
        "error_code": "VALUE_ERROR",
        "success": False
    }

# ============ Documentation ============

@app.get("/")
async def root():
    """Root endpoint with API documentation"""
    return {
        "name": "OpenOracle Prediction Market API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "create_market": "POST /api/v1/markets/create",
            "batch_create": "POST /api/v1/markets/batch",
            "analyze_text": "GET /api/v1/markets/analyze",
            "creator_stats": "GET /api/v1/markets/stats/{address}",
            "websocket": "WS /ws/markets/{market_id}"
        },
        "description": "Create prediction markets with AI-powered oracle routing"
    }

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)