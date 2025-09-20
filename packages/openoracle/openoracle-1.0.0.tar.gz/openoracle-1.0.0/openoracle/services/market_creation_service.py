"""
Market Creation Service
Complete service for creating prediction markets with AI routing and contract interaction
"""

import json
import logging
import time
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import httpx
from web3 import Web3

from ..schemas.prediction_market_schemas import (
    PredictionMarketRequest,
    PredictionQualification,
    OracleRouting,
    MarketParameters,
    ContractCallData,
    PredictionMarketCreationResponse,
    MarketAnalysisLog,
    MarketStatus,
    MarketCategory
)
from ..database.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)

class MarketCreationService:
    """
    Complete service for creating prediction markets
    Handles: Analysis → Routing → Contract Generation → Database Logging
    """

    POLLYPOLL_CONTRACT = "0x1234567890abcdef1234567890abcdef12345678"  # Update with actual address
    ORACLE_ADDRESSES = {
        "chainlink": "0xChainlinkOracleAddress",
        "pyth": "0xPythOracleAddress",
        "uma": "0xUMAOracleAddress",
        "band": "0xBandOracleAddress",
        "api3": "0xAPI3OracleAddress"
    }

    def __init__(
        self,
        openrouter_api_key: str,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        web3_rpc_url: str = "https://mainnet.base.org",
        enable_database: bool = False
    ):
        self.openrouter_api_key = openrouter_api_key
        self.enable_database = enable_database and supabase_url and supabase_key

        if self.enable_database:
            self.supabase = SupabaseClient(supabase_url, supabase_key)
        else:
            self.supabase = None

        self.w3 = Web3(Web3.HTTPProvider(web3_rpc_url))
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "openai/gpt-4o-mini"

    async def create_prediction_market(
        self,
        request: PredictionMarketRequest
    ) -> PredictionMarketCreationResponse:
        """
        Complete flow for creating a prediction market

        Steps:
        1. Qualify the question
        2. Route to best oracle
        3. Generate market parameters
        4. Create contract call data
        5. Log to database
        """
        start_time = time.time()
        request_id = str(uuid.uuid4())

        try:
            # Step 1: Qualify the question
            qualification = await self._qualify_prediction_market(request.text)

            if not qualification.is_prediction_market:
                await self._log_failed_attempt(request, request_id, qualification.reasoning)
                return self._error_response(
                    request_id,
                    f"Not suitable for prediction market: {qualification.reasoning}"
                )

            # Step 2: Route to oracle
            routing = await self._route_to_oracle(
                request.text,
                qualification
            )

            # Step 3: Generate market parameters
            parameters = await self._generate_market_parameters(
                request,
                qualification,
                routing
            )

            # Step 4: Create contract call data
            contract_data = await self._generate_contract_call(
                parameters,
                request.initial_liquidity
            )

            # Step 5: Log to database (optional)
            if self.enable_database:
                await self._log_to_database(
                    request,
                    request_id,
                    qualification,
                    routing,
                    parameters,
                    contract_data
                )

            # Calculate costs
            total_cost = (
                request.initial_liquidity +
                routing.estimated_cost_usd +
                Decimal(str(contract_data.estimated_gas * 0.000001))  # Estimate gas cost
            )

            # Create response
            processing_time = int((time.time() - start_time) * 1000)

            return PredictionMarketCreationResponse(
                qualification=qualification,
                routing=routing,
                parameters=parameters,
                contract_data=contract_data,
                success=True,
                market_id=f"mkt_{request_id[:8]}",
                estimated_total_cost=total_cost,
                request_id=request_id,
                processing_time_ms=processing_time
            )

        except Exception as e:
            logger.error(f"Market creation failed: {e}")
            await self._log_failed_attempt(request, request_id, str(e))
            return self._error_response(request_id, str(e))

    async def _qualify_prediction_market(self, text: str) -> PredictionQualification:
        """
        Step 1: Qualify if text is suitable for prediction market
        """
        # Get the Pydantic schema for validation
        schema = PredictionQualification.model_json_schema()

        prompt = f"""
        Analyze if this text is suitable for a prediction market.

        Text: "{text}"

        Evaluate:
        1. Has clear, discrete outcomes (Yes/No, multiple choice, or scalar)
        2. Is measurable and verifiable
        3. Has specific timeframe or trigger event
        4. Can be resolved objectively

        Return a JSON object matching this EXACT Pydantic schema:
        {json.dumps(schema, indent=2)}

        IMPORTANT: All fields are required. Use these exact field names and types.
        """

        try:
            response = await self._call_ai(prompt, schema)
            return PredictionQualification.model_validate(response)
        except Exception as e:
            logger.error(f"Qualification failed: {e}")
            return PredictionQualification(
                is_prediction_market=False,
                confidence=0.0,
                reasoning=f"Analysis failed: {str(e)}",
                has_clear_outcome=False,
                is_measurable=False,
                is_verifiable=False,
                has_timeframe=False,
                outcomes=[],
                verification_method="unknown"
            )

    async def _route_to_oracle(
        self,
        text: str,
        qualification: PredictionQualification
    ) -> OracleRouting:
        """
        Step 2: Route to best oracle provider
        """
        # Get the Pydantic schema for validation
        schema = OracleRouting.model_json_schema()

        prompt = f"""
        Select the best oracle for this prediction market.

        Question: "{text}"
        Outcomes: {json.dumps(qualification.outcomes)}
        Timeframe: {qualification.timeframe}

        Oracle options:
        - chainlink: Sports (TheRundown), prices, weather (AccuWeather)
        - pyth: Real-time crypto/stock prices (fastest, 100ms)
        - uma: Elections, events needing human verification (2hr resolution)
        - band: Cross-chain, custom APIs, social media
        - api3: Weather (NOAA), NFT prices, first-party APIs

        Return JSON matching this EXACT Pydantic schema:
        {json.dumps(schema, indent=2)}

        IMPORTANT:
        - oracle_provider must be one of: chainlink, pyth, uma, band, api3
        - estimated_cost_usd must be a decimal string like "0.50"
        - All fields are required
        """

        try:
            response = await self._call_ai(prompt, schema)
            # Convert string to Decimal for cost
            if isinstance(response.get('estimated_cost_usd'), str):
                response['estimated_cost_usd'] = Decimal(response['estimated_cost_usd'])
            return OracleRouting.model_validate(response)
        except Exception as e:
            logger.error(f"Oracle routing failed: {e}")
            return OracleRouting(
                oracle_provider="chainlink",
                reasoning="Default to Chainlink due to error",
                confidence=0.5,
                data_type="custom",
                update_frequency="on_demand",
                resolution_method="direct",
                expected_latency_ms=1000,
                estimated_cost_usd=Decimal("1.00"),
                resolution_sources=["Manual verification"]
            )

    async def _generate_market_parameters(
        self,
        request: PredictionMarketRequest,
        qualification: PredictionQualification,
        routing: OracleRouting
    ) -> MarketParameters:
        """
        Step 3: Generate market parameters
        """
        # Get the Pydantic schema for validation
        schema = MarketParameters.model_json_schema()

        # Calculate resolution timestamp
        resolution_time = request.resolution_time or (datetime.utcnow() + timedelta(days=30))

        prompt = f"""
        Generate market parameters for this prediction market.

        Question: "{request.text}"
        Outcomes: {json.dumps(qualification.outcomes)}
        Oracle: {routing.oracle_provider}
        Resolution: {qualification.timeframe or resolution_time.isoformat()}

        Create:
        1. Market title (short, catchy, max 100 chars)
        2. Description (clear, detailed)
        3. Category and labels
        4. Initial odds (must sum to 1.0)
        5. Resolution criteria

        Return JSON matching this EXACT Pydantic schema:
        {json.dumps(schema, indent=2)}

        REQUIRED VALUES:
        - market_category: Must be one of: Sports, Politics, Entertainment, Crypto, Finance, Technology, Custom
        - market_type: Must be one of: binary, multiple, scalar
        - oracle_address: "{self.ORACLE_ADDRESSES.get(routing.oracle_provider, "0x0000000000000000000000000000000000000000")}"
        - liquidity_amount: "{str(request.initial_liquidity)}"
        - resolution_timestamp: "{resolution_time.isoformat()}"
        - creator_fee_bps: 200

        IMPORTANT: All fields are required. Initial odds must be a dict with outcome names as keys.
        """

        try:
            response = await self._call_ai(prompt, schema)

            # Convert string values to proper types
            if isinstance(response.get('liquidity_amount'), str):
                response['liquidity_amount'] = Decimal(response['liquidity_amount'])

            # Ensure resolution timestamp is datetime
            if isinstance(response.get('resolution_timestamp'), str):
                response['resolution_timestamp'] = datetime.fromisoformat(
                    response['resolution_timestamp'].replace('Z', '+00:00')
                )

            return MarketParameters.model_validate(response)
        except Exception as e:
            logger.error(f"Parameter generation failed: {e}")
            # Return default parameters on error
            return MarketParameters(
                market_title=request.text[:100],
                market_description=request.text,
                market_category=MarketCategory.CUSTOM,
                market_labels=["Custom"],
                market_type="binary",
                outcomes=qualification.outcomes or ["Yes", "No"],
                resolution_timestamp=resolution_time,
                oracle_address=self.ORACLE_ADDRESSES.get(routing.oracle_provider, "0x0"),
                resolution_criteria="To be determined",
                initial_odds={"Yes": 0.5, "No": 0.5},
                liquidity_amount=request.initial_liquidity,
                creator_fee_bps=200
            )

    async def _generate_contract_call(
        self,
        parameters: MarketParameters,
        liquidity: Decimal
    ) -> ContractCallData:
        """
        Step 4: Generate contract call data for PollyPoll
        """
        # Prepare function parameters
        function_params = {
            "title": parameters.market_title,
            "description": parameters.market_description,
            "outcomes": parameters.outcomes,
            "resolutionTime": int(parameters.resolution_timestamp.timestamp()),
            "oracleAddress": parameters.oracle_address,
            "initialOdds": [int(o * 10000) for o in parameters.initial_odds.values()],
            "liquidityAmount": int(liquidity * 10**6),  # Convert to USDC decimals
            "creatorFeeBps": parameters.creator_fee_bps
        }

        # ABI encode the function call
        # This would use the actual PollyPoll contract ABI
        encoded_data = self._encode_function_call(
            "createPredictionMarket",
            function_params
        )

        # Estimate gas
        estimated_gas = 500000  # Rough estimate, would calculate actual

        return ContractCallData(
            contract_address=self.POLLYPOLL_CONTRACT,
            parameters=function_params,
            encoded_data=encoded_data,
            estimated_gas=estimated_gas
        )

    def _encode_function_call(
        self,
        function_name: str,
        params: Dict[str, Any]
    ) -> str:
        """
        ABI encode function call
        In production, this would use the actual contract ABI
        """
        # Simplified encoding for demonstration
        return "0x" + json.dumps(params).encode().hex()

    async def _log_to_database(
        self,
        request: PredictionMarketRequest,
        request_id: str,
        qualification: PredictionQualification,
        routing: OracleRouting,
        parameters: MarketParameters,
        contract_data: ContractCallData
    ):
        """
        Step 5: Log everything to Supabase
        """
        log_entry = MarketAnalysisLog(
            request_id=request_id,
            creator_address=request.creator_address,
            input_text=request.text,
            is_valid_market=qualification.is_prediction_market,
            confidence_score=qualification.confidence,
            oracle_provider=routing.oracle_provider,
            market_category=parameters.market_category.value,
            market_labels=parameters.market_labels,
            market_title=parameters.market_title,
            outcomes=parameters.outcomes,
            resolution_criteria=parameters.resolution_criteria,
            resolution_timestamp=parameters.resolution_timestamp,
            initial_liquidity=request.initial_liquidity,
            contract_address=contract_data.contract_address,
            status=MarketStatus.PENDING
        )

        await self.supabase.insert("market_analysis_logs", log_entry.dict())

    async def _log_failed_attempt(
        self,
        request: PredictionMarketRequest,
        request_id: str,
        error: str
    ):
        """Log failed market creation attempt (if database enabled)"""
        if not self.enable_database:
            return

        log_entry = {
            "request_id": request_id,
            "creator_address": request.creator_address,
            "input_text": request.text,
            "is_valid_market": False,
            "confidence_score": 0.0,
            "error_message": error,
            "status": MarketStatus.CANCELLED.value,
            "created_at": datetime.utcnow().isoformat()
        }

        await self.supabase.insert("market_analysis_logs", log_entry)

    async def _call_ai(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Call OpenRouter AI API with Pydantic schema enforcement

        Args:
            prompt: The prompt to send to AI
            schema: Optional Pydantic JSON schema for validation

        Returns:
            Validated JSON response
        """
        # Build system message with schema awareness
        system_message = "You are a prediction market expert. Always return valid JSON."
        if schema:
            system_message += f" Your response MUST exactly match the provided Pydantic schema. All fields are required unless marked optional."

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": system_message
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
                ai_response = json.loads(result["choices"][0]["message"]["content"])

                # Validate against schema if provided
                if schema:
                    # Basic validation - check required fields
                    required_fields = schema.get('required', [])
                    for field in required_fields:
                        if field not in ai_response:
                            logger.warning(f"Missing required field: {field}")
                            # Try to add default values for missing fields
                            if field in schema.get('properties', {}):
                                field_schema = schema['properties'][field]
                                if field_schema.get('type') == 'string':
                                    ai_response[field] = ""
                                elif field_schema.get('type') == 'number':
                                    ai_response[field] = 0
                                elif field_schema.get('type') == 'boolean':
                                    ai_response[field] = False
                                elif field_schema.get('type') == 'array':
                                    ai_response[field] = []

                return ai_response
            else:
                raise Exception(f"AI API error: {response.status_code}")

    def _error_response(
        self,
        request_id: str,
        error: str
    ) -> PredictionMarketCreationResponse:
        """Create error response"""
        return PredictionMarketCreationResponse(
            qualification=PredictionQualification(
                is_prediction_market=False,
                confidence=0.0,
                reasoning=error,
                has_clear_outcome=False,
                is_measurable=False,
                is_verifiable=False,
                has_timeframe=False,
                outcomes=[],
                verification_method="N/A"
            ),
            routing=OracleRouting(
                oracle_provider="chainlink",
                reasoning="N/A",
                confidence=0.0,
                data_type="custom",
                update_frequency="on_demand",
                resolution_method="direct",
                expected_latency_ms=0,
                estimated_cost_usd=Decimal("0"),
                resolution_sources=[]
            ),
            parameters=MarketParameters(
                market_title="",
                market_description="",
                market_category=MarketCategory.CUSTOM,
                market_labels=[],
                market_type="binary",
                outcomes=[],
                resolution_timestamp=datetime.utcnow(),
                oracle_address="",
                resolution_criteria="",
                initial_odds={},
                liquidity_amount=Decimal("0"),
                creator_fee_bps=0
            ),
            contract_data=ContractCallData(
                contract_address="",
                parameters={},
                encoded_data="",
                estimated_gas=0
            ),
            success=False,
            estimated_total_cost=Decimal("0"),
            request_id=request_id,
            processing_time_ms=0
        )