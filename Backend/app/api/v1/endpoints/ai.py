"""
AI API endpoints for intelligent property recommendations and analysis.
"""

from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import User
from app.schemas.ai import (
    AIPropertyRecommendationRequest,
    AIPropertyRecommendationResponse,
    AIDemandAnalysisRequest,
    AIDemandAnalysisResponse,
    AIPricingAnalysisRequest,
    AIPricingAnalysisResponse,
    AIChatRequest,
    AIChatResponse,
    AIMarketAnalysisRequest,
    AIMarketAnalysisResponse,
)
from app.services.ai_service import AIService
from app.utils.security import (
    get_current_admin_user,
    get_current_developer_user,
    get_current_user,
)

router = APIRouter(prefix="/ai", tags=["AI Services"])

# Initialize the AI service
ai_service = AIService()


@router.post(
    "/recommend-properties",
    response_model=AIPropertyRecommendationResponse,
    summary="Get AI property recommendations",
    description="Get personalized property recommendations using AI",
)
async def recommend_properties(
    request: AIPropertyRecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AIPropertyRecommendationResponse:
    """
    Get personalized property recommendations using AI.

    **Requirements:**
    - Must be logged in
    - Valid access token in Authorization header

    **Request body:**
    - **budget_min/max**: Budget range
    - **preferred_regions**: Preferred regions/cities
    - **property_type**: Preferred property type (APARTMENT, HOUSE, COMMERCIAL)
    - **rooms_count**: Preferred number of rooms
    - **must_have_features**: Required features (parking, balcony, etc.)
    - **nice_to_have_features**: Optional features
    - **lifestyle_preferences**: Lifestyle preferences (quiet, central, family-friendly)
    - **commute_preferences**: Commute requirements
    - **investment_goals**: Investment goals (rental income, appreciation, etc.)

    **AI Analysis:**
    - Analyzes user preferences and behavior
    - Considers market trends and pricing
    - Evaluates property features and location
    - Calculates compatibility scores
    - Provides personalized recommendations

    **Response includes:**
    - **recommended_properties**: List of recommended properties with scores
    - **reasoning**: AI explanation for recommendations
    - **market_insights**: Relevant market insights
    - **alternative_suggestions**: Alternative options to consider
    """
    return await ai_service.recommend_properties(db, request, str(current_user.id))


@router.post(
    "/chat",
    response_model=AIChatResponse,
    summary="AI property assistant chat",
    description="Chat with AI property assistant for questions and advice",
)
async def ai_chat(
    request: AIChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AIChatResponse:
    """
    Chat with AI property assistant for questions and advice.

    **Requirements:**
    - Must be logged in
    - Valid access token in Authorization header

    **Request body:**
    - **message**: User message/question
    - **context**: Optional context (property_id, search_filters, etc.)
    - **conversation_id**: Optional conversation ID for multi-turn chat

    **AI Capabilities:**
    - Property search assistance
    - Market analysis and insights
    - Investment advice
    - Legal and process guidance
    - Neighborhood information
    - Financing options
    - Comparison between properties

    **Response includes:**
    - **response**: AI assistant response
    - **suggested_actions**: Suggested next actions
    - **related_properties**: Related property suggestions
    - **conversation_id**: Conversation ID for follow-up
    """
    return await ai_service.chat(db, request, str(current_user.id))


@router.post(
    "/analyze-demand",
    response_model=AIDemandAnalysisResponse,
    summary="AI demand analysis",
    description="Analyze property demand using AI (developer/admin only)",
)
async def analyze_demand(
    request: AIDemandAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AIDemandAnalysisResponse:
    """
    Analyze property demand using AI.

    **Requirements:**
    - Must be a developer or admin
    - Valid access token in Authorization header

    **Request body:**
    - **property_id**: Property to analyze (optional)
    - **complex_id**: Complex to analyze (optional)
    - **location**: Geographic area to analyze
    - **property_type**: Property type filter
    - **price_range**: Price range to analyze
    - **time_period**: Analysis time period (days)

    **AI Analysis:**
    - Historical demand patterns
    - Seasonal trends
    - Market saturation analysis
    - Competitor analysis
    - Price sensitivity analysis
    - Demographic trends
    - Economic indicators impact

    **Response includes:**
    - **demand_score**: Overall demand score (0-100)
    - **demand_trend**: Trend direction (INCREASING, STABLE, DECREASING)
    - **peak_periods**: Identified peak demand periods
    - **key_factors**: Key factors affecting demand
    - **predictions**: Future demand predictions
    - **recommendations**: AI recommendations for optimization
    """
    # Check permissions
    if not current_user.is_admin and not current_user.developer_profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "ACCESS_DENIED",
                    "message": "Доступ разрешен только застройщикам и администраторам",
                    "details": {},
                }
            },
        )

    return await ai_service.analyze_demand(db, request, str(current_user.id))


@router.post(
    "/analyze-pricing",
    response_model=AIPricingAnalysisResponse,
    summary="AI pricing analysis",
    description="Analyze property pricing using AI (developer/admin only)",
)
async def analyze_pricing(
    request: AIPricingAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AIPricingAnalysisResponse:
    """
    Analyze property pricing using AI.

    **Requirements:**
    - Must be a developer or admin
    - Valid access token in Authorization header

    **Request body:**
    - **property_id**: Property to analyze
    - **current_price**: Current property price
    - **comparable_properties**: Comparable properties for analysis
    - **market_conditions**: Current market conditions
    - **target_timeline**: Sales timeline target

    **AI Analysis:**
    - Comparable properties analysis
    - Market price trends
    - Feature-based pricing
    - Location value assessment
    - Demand-supply dynamics
    - Optimal pricing strategies
    - Price elasticity analysis

    **Response includes:**
    - **suggested_price**: AI-suggested optimal price
    - **price_range**: Recommended price range
    - **confidence_score**: Confidence in the recommendation
    - **price_factors**: Factors affecting the price
    - **market_position**: Position vs. market
    - **pricing_strategy**: Recommended pricing strategy
    - **revenue_projections**: Revenue impact projections
    """
    # Check permissions
    if not current_user.is_admin and not current_user.developer_profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "ACCESS_DENIED",
                    "message": "Доступ разрешен только застройщикам и администраторам",
                    "details": {},
                }
            },
        )

    return await ai_service.analyze_pricing(db, request, str(current_user.id))


@router.post(
    "/analyze-market",
    response_model=AIMarketAnalysisResponse,
    summary="AI market analysis",
    description="Comprehensive market analysis using AI (developer/admin only)",
)
async def analyze_market(
    request: AIMarketAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AIMarketAnalysisResponse:
    """
    Comprehensive market analysis using AI.

    **Requirements:**
    - Must be a developer or admin
    - Valid access token in Authorization header

    **Request body:**
    - **region**: Region to analyze
    - **city**: City to analyze
    - **property_types**: Property types to include
    - **analysis_depth**: Analysis depth (BASIC, DETAILED, COMPREHENSIVE)
    - **time_horizon**: Analysis time horizon (months)

    **AI Analysis:**
    - Market trends and cycles
    - Supply and demand dynamics
    - Price movements and projections
    - Investment opportunities
    - Risk assessment
    - Competitive landscape
    - Economic indicators impact
    - Demographic analysis

    **Response includes:**
    - **market_health**: Overall market health score
    - **trend_analysis**: Market trend analysis
    - **opportunity_areas**: Identified opportunities
    - **risk_factors**: Key risk factors
    - **price_predictions**: Price movement predictions
    - **investment_recommendations**: Investment recommendations
    - **strategic_insights**: Strategic insights for developers
    """
    # Check permissions
    if not current_user.is_admin and not current_user.developer_profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "ACCESS_DENIED",
                    "message": "Доступ разрешен только застройщикам и администраторам",
                    "details": {},
                }
            },
        )

    return await ai_service.analyze_market(db, request, str(current_user.id))


@router.get(
    "/property/{property_id}/insights",
    response_model=Dict,
    summary="Get AI property insights",
    description="Get AI-generated insights for a specific property",
)
async def get_property_insights(
    property_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict:
    """
    Get AI-generated insights for a specific property.

    **Requirements:**
    - Must be logged in
    - Valid access token in Authorization header

    **Path parameters:**
    - **property_id**: Property UUID

    **AI Insights:**
    - Property value assessment
    - Investment potential
    - Rental yield estimates
    - Market comparison
    - Location advantages
    - Future value projections
    - Risk assessment
    - Best time to buy/sell

    **Response includes:**
    - **value_assessment**: Current value assessment
    - **investment_score**: Investment potential score
    - **rental_yield**: Estimated rental yield
    - **market_position**: Position vs. similar properties
    - **growth_potential**: Future growth potential
    - **risks**: Identified risks
    - **recommendations**: AI recommendations
    """
    return await ai_service.get_property_insights(db, property_id, str(current_user.id))


@router.get(
    "/market-trends",
    response_model=Dict,
    summary="Get AI market trends",
    description="Get AI-analyzed market trends and predictions",
)
async def get_market_trends(
    region: Optional[str] = Query(None, description="Region filter"),
    city: Optional[str] = Query(None, description="City filter"),
    property_type: Optional[str] = Query(None, description="Property type filter"),
    time_period: int = Query(30, ge=7, le=365, description="Time period in days"),
    db: AsyncSession = Depends(get_db),
) -> Dict:
    """
    Get AI-analyzed market trends and predictions.

    **Query parameters:**
    - **region**: Filter by region
    - **city**: Filter by city
    - **property_type**: Filter by property type
    - **time_period**: Analysis time period (days)

    **AI Analysis:**
    - Price trend analysis
    - Market momentum
    - Supply/demand balance
    - Popular areas identification
    - Emerging trends
    - Seasonal patterns
    - Investment hotspots

    **Response includes:**
    - **price_trends**: Price movement trends
    - **hot_areas**: Trending areas
    - **market_momentum**: Overall market momentum
    - **predictions**: Short-term predictions
    - **investment_opportunities**: Investment opportunities
    - **market_insights**: Key market insights
    """
    return await ai_service.get_market_trends(
        db, region, city, property_type, time_period
    )


@router.get(
    "/investment-opportunities",
    response_model=Dict,
    summary="Get AI investment opportunities",
    description="Get AI-identified investment opportunities",
)
async def get_investment_opportunities(
    budget_min: Optional[float] = Query(None, description="Minimum budget"),
    budget_max: Optional[float] = Query(None, description="Maximum budget"),
    region: Optional[str] = Query(None, description="Region filter"),
    investment_type: Optional[str] = Query(
        None, description="Investment type (RENTAL, APPRECIATION, FLIP)"
    ),
    risk_tolerance: Optional[str] = Query(
        None, description="Risk tolerance (LOW, MEDIUM, HIGH)"
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict:
    """
    Get AI-identified investment opportunities.

    **Requirements:**
    - Must be logged in
    - Valid access token in Authorization header

    **Query parameters:**
    - **budget_min/max**: Budget range
    - **region**: Geographic filter
    - **investment_type**: Type of investment goal
    - **risk_tolerance**: Risk tolerance level

    **AI Analysis:**
    - ROI potential analysis
    - Market timing assessment
    - Risk-reward evaluation
    - Cash flow projections
    - Exit strategy options
    - Market cycle positioning

    **Response includes:**
    - **opportunities**: List of investment opportunities
    - **roi_projections**: ROI projections
    - **risk_assessment**: Risk analysis
    - **timing_recommendations**: Timing recommendations
    - **portfolio_suggestions**: Portfolio diversification suggestions
    """
    return await ai_service.get_investment_opportunities(
        db, str(current_user.id), budget_min, budget_max, region, investment_type, risk_tolerance
    )


@router.post(
    "/optimize-pricing",
    response_model=Dict,
    summary="AI price optimization",
    description="Optimize property pricing using AI (developer only)",
)
async def optimize_pricing(
    property_id: str,
    target_timeline: Optional[int] = Query(
        None, description="Target sales timeline (days)"
    ),
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
) -> Dict:
    """
    Optimize property pricing using AI.

    **Requirements:**
    - Must be a developer
    - Must own the property
    - Valid access token in Authorization header

    **Query parameters:**
    - **target_timeline**: Target sales timeline in days

    **AI Optimization:**
    - Dynamic pricing analysis
    - Market demand assessment
    - Competitive positioning
    - Sales velocity optimization
    - Revenue maximization
    - Time-to-sale optimization

    **Response includes:**
    - **optimized_price**: AI-optimized price
    - **pricing_strategy**: Recommended strategy
    - **expected_timeline**: Expected sales timeline
    - **revenue_impact**: Revenue impact analysis
    - **market_factors**: Key market factors
    - **confidence_score**: Confidence in recommendations
    """
    if not current_user.developer_profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "NO_DEVELOPER_PROFILE",
                    "message": "Профиль застройщика не найден",
                    "details": {},
                }
            },
        )

    return await ai_service.optimize_pricing(
        db, property_id, str(current_user.developer_profile.id), target_timeline
    )
