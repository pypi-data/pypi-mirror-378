"""
Interactive Market Creation Service for Python SDK
Two-step process: Propose → Confirm
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import uuid
import asyncio
import aiohttp

from pydantic import BaseModel, Field
from ..ai.pure_ai_router import PureAIRouter


class MarketType(str, Enum):
    BINARY = "binary"
    MULTIPLE = "multiple"
    SCALAR = "scalar"


class OracleProvider(str, Enum):
    CHAINLINK = "chainlink"
    PYTH = "pyth"
    UMA = "uma"
    BAND = "band"
    API3 = "api3"


class MarketAnalysis(BaseModel):
    """Analysis of user input"""
    is_valid: bool
    confidence: float = Field(ge=0, le=1)
    issues: List[str] = []
    improvements: List[str] = []


class OracleInfo(BaseModel):
    """Oracle information for a suggestion"""
    provider: OracleProvider
    reasoning: str
    confidence: float = Field(ge=0, le=1)
    data_source: str
    expected_latency: str


class ResolutionInfo(BaseModel):
    """Resolution information for a suggestion"""
    method: str
    criteria: str
    date: datetime
    source: str


class MarketSuggestion(BaseModel):
    """A single market suggestion"""
    index: int
    title: str
    description: str
    question: str
    outcomes: List[str]
    oracle: OracleInfo
    resolution: ResolutionInfo
    estimated_odds: Dict[str, float]
    market_type: MarketType
    tags: List[str]
    confidence: float = Field(ge=0, le=1)
    reasoning: str


class CostBreakdown(BaseModel):
    """Cost breakdown for market creation"""
    gas_fees: float
    protocol_fee: float
    oracle_fee: float
    total_cost: float
    subsidized_amount: float
    user_pays: float


class MarketProposal(BaseModel):
    """Complete market proposal with suggestions"""
    proposal_id: str
    original_text: str
    analysis: MarketAnalysis
    suggestions: List[MarketSuggestion]
    recommended_index: int
    expires_at: datetime
    estimated_costs: CostBreakdown


class MarketConfirmation(BaseModel):
    """User confirmation for market creation"""
    proposal_id: str
    selected_suggestion_index: int
    user_modifications: Optional[Dict[str, Any]] = None
    agreed_to_terms: bool = True
    signature: Optional[str] = None


class MarketCreationResult(BaseModel):
    """Result of market creation"""
    success: bool
    market_id: Optional[str] = None
    transaction_hash: Optional[str] = None
    market_url: Optional[str] = None
    error: Optional[str] = None
    receipt: Optional[Dict[str, Any]] = None


class InteractiveMarketService:
    """
    Interactive market creation service with two-step flow:
    1. Generate proposals from user input
    2. Confirm and create market
    """

    def __init__(
        self,
        openrouter_api_key: str,
        proxy_url: Optional[str] = None,
        api_key: Optional[str] = None,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        proposal_ttl_minutes: int = 5
    ):
        """
        Initialize the interactive market service

        Args:
            openrouter_api_key: API key for OpenRouter
            proxy_url: URL of proxy service
            api_key: API key for proxy service
            supabase_url: Supabase URL for caching
            supabase_key: Supabase API key
            proposal_ttl_minutes: Time-to-live for proposals in minutes
        """
        self.ai_router = PureAIRouter(openrouter_api_key)
        self.proxy_url = proxy_url
        self.api_key = api_key
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.proposal_ttl = timedelta(minutes=proposal_ttl_minutes)
        self.proposal_cache: Dict[str, MarketProposal] = {}

        # Oracle addresses on BASE
        self.oracle_addresses = {
            OracleProvider.CHAINLINK: "0xChainlinkBASE",
            OracleProvider.PYTH: "0xPythBASE",
            OracleProvider.UMA: "0xUMABASE",
            OracleProvider.BAND: "0xBandBASE",
            OracleProvider.API3: "0xAPI3BASE"
        }

    async def generate_proposals(
        self,
        user_input: str,
        user_address: str,
        max_suggestions: int = 3,
        preferred_oracle: Optional[str] = None,
        budget: Optional[float] = None,
        timeframe: Optional[str] = None
    ) -> MarketProposal:
        """
        Step 1: Generate proposals from user input

        Args:
            user_input: The user's market idea
            user_address: User's wallet address
            max_suggestions: Number of suggestions to generate
            preferred_oracle: Preferred oracle provider
            budget: Budget for market creation
            timeframe: Preferred timeframe

        Returns:
            MarketProposal with analysis and suggestions
        """
        proposal_id = self._generate_proposal_id()

        try:
            # Analyze the input
            analysis = await self._analyze_input(user_input)

            # Generate suggestions
            suggestions = await self._generate_suggestions(
                user_input,
                analysis,
                max_suggestions,
                preferred_oracle
            )

            # Calculate costs
            costs = await self._calculate_costs(user_address)

            # Find best suggestion
            recommended_index = self._select_best_suggestion(suggestions)

            # Create proposal
            proposal = MarketProposal(
                proposal_id=proposal_id,
                original_text=user_input,
                analysis=analysis,
                suggestions=suggestions,
                recommended_index=recommended_index,
                expires_at=datetime.now() + self.proposal_ttl,
                estimated_costs=costs
            )

            # Cache the proposal
            self.proposal_cache[proposal_id] = proposal

            # Store in database if configured
            if self.supabase_url:
                await self._store_proposal(proposal, user_address)

            # Clean up expired proposals
            self._cleanup_expired_proposals()

            return proposal

        except Exception as e:
            print(f"Failed to generate proposals: {e}")
            raise

    async def confirm_and_create(
        self,
        confirmation: MarketConfirmation
    ) -> MarketCreationResult:
        """
        Step 2: Confirm and create the market

        Args:
            confirmation: User's confirmation with selected suggestion

        Returns:
            Result of market creation
        """
        # Retrieve cached proposal
        proposal = self.proposal_cache.get(confirmation.proposal_id)

        if not proposal:
            # Try to fetch from database
            if self.supabase_url:
                proposal = await self._fetch_proposal(confirmation.proposal_id)
                if proposal:
                    self.proposal_cache[confirmation.proposal_id] = proposal
                else:
                    return MarketCreationResult(
                        success=False,
                        error="Proposal not found or expired"
                    )
            else:
                return MarketCreationResult(
                    success=False,
                    error="Proposal not found or expired"
                )

        # Check expiration
        if datetime.now() > proposal.expires_at:
            del self.proposal_cache[confirmation.proposal_id]
            return MarketCreationResult(
                success=False,
                error="Proposal has expired. Please generate a new proposal."
            )

        # Get selected suggestion
        if confirmation.selected_suggestion_index >= len(proposal.suggestions):
            return MarketCreationResult(
                success=False,
                error="Invalid suggestion index"
            )

        suggestion = proposal.suggestions[confirmation.selected_suggestion_index]

        # Apply user modifications
        final_market_data = self._apply_user_modifications(
            suggestion,
            confirmation.user_modifications
        )

        # Create market via proxy or direct
        if self.proxy_url and self.api_key:
            result = await self._create_via_proxy(
                final_market_data,
                confirmation
            )
        else:
            result = await self._create_direct(final_market_data)

        # Clean up proposal if successful
        if result.success:
            del self.proposal_cache[confirmation.proposal_id]

        return result

    async def _analyze_input(self, user_input: str) -> MarketAnalysis:
        """Analyze user input for prediction market suitability"""
        prompt = f"""
        Analyze this text for prediction market suitability:
        "{user_input}"

        Identify:
        1. Is this valid for a prediction market?
        2. What issues exist? (vague, subjective, no timeframe, etc.)
        3. What improvements would make it better?
        4. Confidence score (0-1)

        Return JSON:
        {{
            "is_valid": boolean,
            "confidence": 0.0-1.0,
            "issues": ["issue1", "issue2"],
            "improvements": ["improvement1", "improvement2"]
        }}
        """

        response = await self.ai_router.analyze(prompt, MarketAnalysis)
        return response

    async def _generate_suggestions(
        self,
        user_input: str,
        analysis: MarketAnalysis,
        count: int,
        preferred_oracle: Optional[str] = None
    ) -> List[MarketSuggestion]:
        """Generate multiple market suggestions"""
        oracle_context = f"Preferred oracle: {preferred_oracle}" if preferred_oracle else ""

        prompt = f"""
        Generate {count} different prediction market suggestions for:
        "{user_input}"

        Issues to address: {json.dumps(analysis.issues)}
        {oracle_context}

        For each suggestion create a DIFFERENT approach:
        1. Different oracle providers (chainlink, pyth, uma, band, api3)
        2. Different resolution methods
        3. Different phrasings/outcomes
        4. Different timeframes if applicable

        Each suggestion should be:
        - Clear and measurable
        - Objectively resolvable
        - Time-bounded
        - Suitable for the selected oracle

        Return JSON array of {count} suggestions with format:
        [
            {{
                "title": "short catchy title",
                "description": "detailed description",
                "question": "clear yes/no or multiple choice question",
                "outcomes": ["outcome1", "outcome2"],
                "oracle": {{
                    "provider": "chainlink|pyth|uma|band|api3",
                    "reasoning": "why this oracle is best",
                    "confidence": 0.0-1.0,
                    "data_source": "specific data source",
                    "expected_latency": "1 second|1 hour|2 hours"
                }},
                "resolution": {{
                    "method": "how it will be resolved",
                    "criteria": "specific criteria",
                    "date": "ISO date string",
                    "source": "data source for resolution"
                }},
                "estimated_odds": {{"outcome1": 0.5, "outcome2": 0.5}},
                "market_type": "binary|multiple|scalar",
                "tags": ["tag1", "tag2"],
                "confidence": 0.0-1.0,
                "reasoning": "why this formulation works"
            }}
        ]
        """

        try:
            suggestions_data = await self.ai_router.analyze(prompt, List[Dict])

            # Convert to MarketSuggestion objects
            suggestions = []
            for i, data in enumerate(suggestions_data):
                # Parse resolution date
                resolution_date = datetime.fromisoformat(
                    data['resolution']['date'].replace('Z', '+00:00')
                )

                suggestion = MarketSuggestion(
                    index=i,
                    title=data['title'],
                    description=data['description'],
                    question=data['question'],
                    outcomes=data['outcomes'],
                    oracle=OracleInfo(**data['oracle']),
                    resolution=ResolutionInfo(
                        method=data['resolution']['method'],
                        criteria=data['resolution']['criteria'],
                        date=resolution_date,
                        source=data['resolution']['source']
                    ),
                    estimated_odds=data['estimated_odds'],
                    market_type=MarketType(data['market_type']),
                    tags=data['tags'],
                    confidence=data['confidence'],
                    reasoning=data['reasoning']
                )
                suggestions.append(suggestion)

            return suggestions

        except Exception as e:
            print(f"Failed to generate suggestions: {e}")
            return []

    async def _calculate_costs(self, user_address: str) -> CostBreakdown:
        """Calculate costs based on user's plan"""
        subsidy_amount = 0

        # Check user's plan if proxy configured
        if self.api_key and self.proxy_url:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.proxy_url}/api/v1/user/{user_address}/plan",
                        headers={"X-API-Key": self.api_key}
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            subsidy_amount = data.get('gas_subsidy', 0)
            except Exception as e:
                print(f"Failed to fetch user plan: {e}")

        total_cost = 0.85  # Base cost estimate

        return CostBreakdown(
            gas_fees=0.50,
            protocol_fee=0.10,
            oracle_fee=0.25,
            total_cost=total_cost,
            subsidized_amount=min(subsidy_amount, total_cost),
            user_pays=max(0, total_cost - subsidy_amount)
        )

    def _select_best_suggestion(self, suggestions: List[MarketSuggestion]) -> int:
        """Select the best suggestion based on confidence scores"""
        if not suggestions:
            return 0

        best_index = 0
        best_score = 0

        for i, suggestion in enumerate(suggestions):
            score = suggestion.confidence * suggestion.oracle.confidence
            if score > best_score:
                best_score = score
                best_index = i

        return best_index

    def _apply_user_modifications(
        self,
        suggestion: MarketSuggestion,
        modifications: Optional[Dict[str, Any]]
    ) -> MarketSuggestion:
        """Apply user modifications to selected suggestion"""
        if not modifications:
            return suggestion

        # Create a copy with modifications
        modified = suggestion.model_copy()

        if 'title' in modifications:
            modified.title = modifications['title']
        if 'outcomes' in modifications:
            modified.outcomes = modifications['outcomes']
        if 'resolution_date' in modifications:
            modified.resolution.date = modifications['resolution_date']

        return modified

    async def _create_via_proxy(
        self,
        market_data: MarketSuggestion,
        confirmation: MarketConfirmation
    ) -> MarketCreationResult:
        """Create market via proxy service"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    'marketData': {
                        'title': market_data.title,
                        'description': market_data.description,
                        'outcomes': market_data.outcomes,
                        'resolutionTime': int(market_data.resolution.date.timestamp()),
                        'oracleAddress': self.oracle_addresses[market_data.oracle.provider],
                        'initialOdds': [
                            int(odds * 10000)
                            for odds in market_data.estimated_odds.values()
                        ],
                        'liquidityAmount': confirmation.user_modifications.get(
                            'initial_liquidity', 100
                        ) if confirmation.user_modifications else 100,
                        'creatorFeeBps': 200
                    },
                    'signature': confirmation.signature
                }

                async with session.post(
                    f"{self.proxy_url}/api/v1/market/create",
                    json=payload,
                    headers={
                        'Content-Type': 'application/json',
                        'X-API-Key': self.api_key
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return MarketCreationResult(
                            success=True,
                            market_id=result.get('marketId'),
                            transaction_hash=result.get('txHash'),
                            market_url=f"https://openoracle.xyz/market/{result.get('marketId')}",
                            receipt=result
                        )
                    else:
                        error_data = await response.json()
                        return MarketCreationResult(
                            success=False,
                            error=error_data.get('message', 'Market creation failed')
                        )

        except Exception as e:
            return MarketCreationResult(
                success=False,
                error=str(e)
            )

    async def _create_direct(self, market_data: MarketSuggestion) -> MarketCreationResult:
        """Direct market creation (requires wallet)"""
        return MarketCreationResult(
            success=False,
            error="Direct creation requires wallet configuration"
        )

    async def _store_proposal(self, proposal: MarketProposal, user_address: str):
        """Store proposal in Supabase"""
        # Implementation would store in Supabase
        pass

    async def _fetch_proposal(self, proposal_id: str) -> Optional[MarketProposal]:
        """Fetch proposal from Supabase"""
        # Implementation would fetch from Supabase
        return None

    def _generate_proposal_id(self) -> str:
        """Generate unique proposal ID"""
        return f"prop_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"

    def _cleanup_expired_proposals(self):
        """Remove expired proposals from cache"""
        now = datetime.now()
        expired_ids = [
            pid for pid, proposal in self.proposal_cache.items()
            if now > proposal.expires_at
        ]
        for pid in expired_ids:
            del self.proposal_cache[pid]

    def get_proposal(self, proposal_id: str) -> Optional[MarketProposal]:
        """Get a cached proposal"""
        return self.proposal_cache.get(proposal_id)

    def list_proposals(self) -> List[MarketProposal]:
        """List all cached proposals"""
        return list(self.proposal_cache.values())