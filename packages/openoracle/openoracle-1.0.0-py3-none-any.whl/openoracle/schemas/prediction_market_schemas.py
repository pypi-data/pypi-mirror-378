"""
Prediction Market Schemas
Complete Pydantic models for prediction market creation and routing
"""

from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, validator
from enum import Enum

# ============ Enums ============

class MarketStatus(str, Enum):
    """Prediction market status"""
    PENDING = "pending"
    ACTIVE = "active"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"

class MarketCategory(str, Enum):
    """High-level market categories"""
    SPORTS = "Sports"
    POLITICS = "Politics"
    ENTERTAINMENT = "Entertainment"
    CRYPTO = "Crypto"
    FINANCE = "Finance"
    TECHNOLOGY = "Technology"
    CUSTOM = "Custom"

class ResolutionSource(str, Enum):
    """Trusted resolution sources"""
    AP = "Associated Press"
    REUTERS = "Reuters"
    ESPN = "ESPN"
    COINGECKO = "CoinGecko"
    OFFICIAL_GOV = "Official Government"
    CHAINLINK = "Chainlink Oracle"
    PYTH = "Pyth Network"
    UMA = "UMA Oracle"
    CUSTOM = "Custom Source"

# ============ Request Schemas ============

class PredictionMarketRequest(BaseModel):
    """Initial request to create a prediction market"""
    text: str = Field(..., description="The text/question to analyze")
    creator_address: str = Field(..., description="Ethereum address of market creator")
    initial_liquidity: Decimal = Field(..., ge=0, description="Initial liquidity in USDC")
    market_fee: Decimal = Field(default=Decimal("0.02"), ge=0, le=Decimal("0.1"), description="Market fee percentage")
    resolution_time: Optional[datetime] = Field(None, description="When market should resolve")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

# ============ Analysis Schemas ============

class PredictionQualification(BaseModel):
    """Step 1: Qualify if text is suitable for prediction market"""
    is_prediction_market: bool = Field(..., description="Can this be a prediction market?")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    reasoning: str = Field(..., description="Explanation of decision")

    # Qualification criteria
    has_clear_outcome: bool = Field(..., description="Has clear Yes/No or multiple outcomes")
    is_measurable: bool = Field(..., description="Outcome is measurable")
    is_verifiable: bool = Field(..., description="Can be verified by oracle or source")
    has_timeframe: bool = Field(..., description="Has specific timeframe or trigger")

    # Extracted elements
    outcomes: List[str] = Field(..., description="Possible outcomes (e.g., ['Yes', 'No'])")
    timeframe: Optional[str] = Field(None, description="Resolution timeframe")
    verification_method: str = Field(..., description="How to verify outcome")

class OracleRouting(BaseModel):
    """Step 2: Route to best oracle provider"""
    oracle_provider: str = Field(..., description="Selected oracle: chainlink|pyth|uma|band|api3")
    reasoning: str = Field(..., description="Why this oracle was selected")
    confidence: float = Field(..., ge=0, le=1, description="Routing confidence")

    # Oracle configuration
    data_type: str = Field(..., description="Type of data: price|sports|election|event|custom")
    update_frequency: str = Field(..., description="realtime|high_freq|on_demand|optimistic")
    resolution_method: str = Field(..., description="direct|aggregated|optimistic")
    expected_latency_ms: int = Field(..., description="Expected oracle latency")
    estimated_cost_usd: Decimal = Field(..., description="Estimated oracle cost")

    # Data requirements
    required_feeds: List[str] = Field(default_factory=list, description="Required data feeds")
    resolution_sources: List[str] = Field(..., description="Data sources for resolution")

class MarketParameters(BaseModel):
    """Step 3: Generate market parameters for contract"""
    market_title: str = Field(..., description="Short market title")
    market_description: str = Field(..., description="Full description")
    market_category: MarketCategory = Field(..., description="Market category")
    market_labels: List[str] = Field(..., description="Category labels")

    # Market structure
    market_type: Literal["binary", "multiple", "scalar"] = Field(..., description="Market type")
    outcomes: List[str] = Field(..., description="Possible outcomes")

    # Timing
    creation_timestamp: datetime = Field(default_factory=datetime.utcnow)
    resolution_timestamp: datetime = Field(..., description="When market resolves")
    trading_end_timestamp: Optional[datetime] = Field(None, description="When trading stops")

    # Oracle configuration
    oracle_address: str = Field(..., description="Oracle contract address")
    oracle_feed_id: Optional[str] = Field(None, description="Specific oracle feed ID")
    resolution_criteria: str = Field(..., description="Clear resolution criteria")

    # Economics
    initial_odds: Dict[str, float] = Field(..., description="Initial odds for each outcome")
    liquidity_amount: Decimal = Field(..., description="Initial liquidity")
    creator_fee_bps: int = Field(default=200, description="Creator fee in basis points")

# ============ Contract Generation ============

class ContractCallData(BaseModel):
    """Contract call data for creating prediction market"""
    function_name: str = Field(default="createPredictionMarket")
    contract_address: str = Field(..., description="PollyPoll contract address")

    # Function parameters (matching PollyPoll contract)
    parameters: Dict[str, Any] = Field(..., description="Contract function parameters")

    # ABI encoding
    encoded_data: str = Field(..., description="ABI encoded function call")
    estimated_gas: int = Field(..., description="Estimated gas for transaction")

    # Metadata
    chain_id: int = Field(default=8453, description="BASE chain ID")
    value_wei: str = Field(default="0", description="ETH value to send")

# ============ Complete Response ============

class PredictionMarketCreationResponse(BaseModel):
    """Complete response for prediction market creation"""
    # Analysis results
    qualification: PredictionQualification
    routing: OracleRouting
    parameters: MarketParameters
    contract_data: ContractCallData

    # Summary
    success: bool = Field(..., description="Overall success status")
    market_id: Optional[str] = Field(None, description="Generated market ID")
    estimated_total_cost: Decimal = Field(..., description="Total cost including gas and oracle")

    # Tracking
    request_id: str = Field(..., description="Unique request ID for tracking")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")

# ============ Database Models ============

class MarketAnalysisLog(BaseModel):
    """Log entry for Supabase database"""
    id: Optional[str] = None
    request_id: str
    creator_address: str
    input_text: str

    # Analysis results
    is_valid_market: bool
    confidence_score: float
    oracle_provider: str
    market_category: str
    market_labels: List[str]

    # Market details
    market_title: Optional[str] = None
    outcomes: List[str]
    resolution_criteria: str
    resolution_timestamp: Optional[datetime] = None

    # Economics
    initial_liquidity: Decimal
    estimated_volume: Optional[Decimal] = None

    # Contract data
    contract_address: Optional[str] = None
    transaction_hash: Optional[str] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: MarketStatus = Field(default=MarketStatus.PENDING)
    error_message: Optional[str] = None

# ============ API Request/Response Models ============

class CreateMarketRequest(BaseModel):
    """API request to create a prediction market"""
    question: str = Field(..., description="The prediction market question")
    creator_wallet: str = Field(..., description="Creator's wallet address")
    initial_liquidity_usdc: float = Field(..., ge=10, description="Initial liquidity in USDC")
    resolution_date: Optional[str] = Field(None, description="ISO format resolution date")

    class Config:
        schema_extra = {
            "example": {
                "question": "Will Bitcoin exceed $100,000 by December 31, 2024?",
                "creator_wallet": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
                "initial_liquidity_usdc": 1000.0,
                "resolution_date": "2024-12-31T23:59:59Z"
            }
        }

class CreateMarketResponse(BaseModel):
    """API response for market creation"""
    success: bool
    market_id: Optional[str] = None
    transaction_hash: Optional[str] = None
    market_url: Optional[str] = None

    # Market details
    title: str
    outcomes: List[str]
    oracle_provider: str
    resolution_date: str

    # Cost breakdown
    costs: Dict[str, float] = Field(..., description="Cost breakdown in USDC")

    # Error handling
    error: Optional[str] = None
    error_code: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "market_id": "mkt_1234567890",
                "transaction_hash": "0xabc...",
                "market_url": "https://pollypoll.com/markets/mkt_1234567890",
                "title": "Bitcoin $100k by EOY 2024",
                "outcomes": ["Yes", "No"],
                "oracle_provider": "pyth",
                "resolution_date": "2024-12-31T23:59:59Z",
                "costs": {
                    "initial_liquidity": 1000.0,
                    "oracle_fee": 0.5,
                    "gas_fee": 2.3,
                    "total": 1002.8
                }
            }
        }

class BatchMarketRequest(BaseModel):
    """Request to create multiple markets"""
    markets: List[CreateMarketRequest]
    batch_id: Optional[str] = None

class BatchMarketResponse(BaseModel):
    """Response for batch market creation"""
    batch_id: str
    total_markets: int
    successful: int
    failed: int
    results: List[CreateMarketResponse]

# ============ Validation Helpers ============

class MarketValidator:
    """Validation utilities for market creation"""

    @staticmethod
    def validate_question(question: str) -> bool:
        """Check if question is valid for prediction market"""
        if len(question) < 10 or len(question) > 500:
            return False
        if not question.endswith("?"):
            return False
        return True

    @staticmethod
    def validate_liquidity(amount: Decimal, min_amount: Decimal = Decimal("10")) -> bool:
        """Check if liquidity amount is valid"""
        return amount >= min_amount

    @staticmethod
    def validate_resolution_date(date: datetime) -> bool:
        """Check if resolution date is valid"""
        min_date = datetime.utcnow() + timedelta(hours=1)
        max_date = datetime.utcnow() + timedelta(days=365 * 2)
        return min_date <= date <= max_date