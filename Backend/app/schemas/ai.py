"""
AI schemas for API requests and responses.
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Property recommendation schemas
class AIPropertyRecommendationRequest(BaseModel):
    """Schema for AI property recommendation request."""
    
    # Budget constraints
    budget_min: Optional[Decimal] = Field(None, ge=0, description="Minimum budget")
    budget_max: Optional[Decimal] = Field(None, ge=0, description="Maximum budget")
    
    # Location preferences
    preferred_regions: Optional[List[str]] = Field(None, description="Preferred regions/cities")
    preferred_cities: Optional[List[str]] = Field(None, description="Preferred cities")
    avoid_regions: Optional[List[str]] = Field(None, description="Regions to avoid")
    
    # Property preferences
    property_type: Optional[str] = Field(None, description="Preferred property type")
    rooms_count: Optional[List[int]] = Field(None, description="Preferred number of rooms")
    min_area: Optional[float] = Field(None, ge=0, description="Minimum area")
    max_area: Optional[float] = Field(None, ge=0, description="Maximum area")
    
    # Must-have features
    must_have_features: Optional[List[str]] = Field(None, description="Required features")
    nice_to_have_features: Optional[List[str]] = Field(None, description="Optional features")
    
    # Lifestyle preferences
    lifestyle_preferences: Optional[List[str]] = Field(None, description="Lifestyle preferences")
    commute_preferences: Optional[Dict[str, Any]] = Field(None, description="Commute requirements")
    
    # Investment goals
    investment_goals: Optional[List[str]] = Field(None, description="Investment goals")
    deal_type: Optional[str] = Field(None, description="Deal type (SALE, RENT)")
    
    # AI context
    user_history: Optional[Dict[str, Any]] = Field(None, description="User search/view history")
    urgency_level: Optional[str] = Field(None, description="Urgency level (LOW, MEDIUM, HIGH)")


class PropertyRecommendation(BaseModel):
    """Schema for a single property recommendation."""
    
    property_id: UUID
    compatibility_score: float = Field(ge=0, le=100, description="Compatibility score (0-100)")
    reasoning: str = Field(description="AI reasoning for recommendation")
    
    # Matching factors
    matching_factors: List[str] = Field(description="Factors that match user preferences")
    potential_concerns: Optional[List[str]] = Field(None, description="Potential concerns")
    
    # Investment insights
    investment_potential: Optional[str] = Field(None, description="Investment potential assessment")
    roi_estimate: Optional[float] = Field(None, description="Estimated ROI percentage")


class AIPropertyRecommendationResponse(BaseModel):
    """Schema for AI property recommendation response."""
    
    recommended_properties: List[PropertyRecommendation]
    total_analyzed: int = Field(description="Total properties analyzed")
    
    # AI insights
    market_insights: List[str] = Field(description="Relevant market insights")
    alternative_suggestions: Optional[List[str]] = Field(None, description="Alternative suggestions")
    
    # Recommendation metadata
    recommendation_confidence: float = Field(ge=0, le=100, description="Overall confidence score")
    analysis_timestamp: str = Field(description="Analysis timestamp")


# Chat schemas
class AIChatRequest(BaseModel):
    """Schema for AI chat request."""
    
    message: str = Field(..., min_length=1, description="User message/question")
    context: Optional[Dict[str, Any]] = Field(None, description="Context information")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for multi-turn chat")
    
    # Additional context
    property_id: Optional[UUID] = Field(None, description="Property context")
    search_filters: Optional[Dict[str, Any]] = Field(None, description="Current search filters")
    user_intent: Optional[str] = Field(None, description="Detected user intent")


class AIChatResponse(BaseModel):
    """Schema for AI chat response."""
    
    response: str = Field(description="AI assistant response")
    conversation_id: str = Field(description="Conversation ID")
    
    # Suggested actions
    suggested_actions: Optional[List[Dict[str, Any]]] = Field(None, description="Suggested next actions")
    related_properties: Optional[List[UUID]] = Field(None, description="Related property IDs")
    
    # Response metadata
    confidence_score: float = Field(ge=0, le=100, description="Response confidence")
    response_type: str = Field(description="Response type (answer, suggestion, question)")


# Demand analysis schemas
class AIDemandAnalysisRequest(BaseModel):
    """Schema for AI demand analysis request."""
    
    # Target analysis
    property_id: Optional[UUID] = Field(None, description="Specific property to analyze")
    complex_id: Optional[UUID] = Field(None, description="Specific complex to analyze")
    
    # Geographic scope
    region: Optional[str] = Field(None, description="Region to analyze")
    city: Optional[str] = Field(None, description="City to analyze")
    district: Optional[str] = Field(None, description="District to analyze")
    
    # Property filters
    property_type: Optional[str] = Field(None, description="Property type filter")
    price_range: Optional[Dict[str, float]] = Field(None, description="Price range to analyze")
    
    # Analysis parameters
    time_period: int = Field(default=90, ge=7, le=365, description="Analysis period in days")
    analysis_depth: str = Field(default="STANDARD", description="Analysis depth (BASIC, STANDARD, DEEP)")


class AIDemandAnalysisResponse(BaseModel):
    """Schema for AI demand analysis response."""
    
    # Overall demand assessment
    demand_score: float = Field(ge=0, le=100, description="Overall demand score")
    demand_trend: str = Field(description="Trend direction (INCREASING, STABLE, DECREASING)")
    
    # Temporal analysis
    peak_periods: List[Dict[str, Any]] = Field(description="Peak demand periods")
    seasonal_patterns: Optional[Dict[str, Any]] = Field(None, description="Seasonal patterns")
    
    # Key factors
    key_factors: List[str] = Field(description="Key factors affecting demand")
    market_drivers: List[str] = Field(description="Main market drivers")
    
    # Predictions
    predictions: Dict[str, Any] = Field(description="Future demand predictions")
    
    # Recommendations
    recommendations: List[str] = Field(description="AI recommendations for optimization")
    
    # Analysis metadata
    analysis_timestamp: str
    confidence_level: float = Field(ge=0, le=100, description="Analysis confidence")


# Pricing analysis schemas
class AIPricingAnalysisRequest(BaseModel):
    """Schema for AI pricing analysis request."""
    
    property_id: UUID = Field(..., description="Property to analyze")
    current_price: Decimal = Field(..., ge=0, description="Current property price")
    
    # Comparable properties
    comparable_properties: Optional[List[UUID]] = Field(None, description="Comparable property IDs")
    
    # Market context
    market_conditions: Optional[Dict[str, Any]] = Field(None, description="Current market conditions")
    target_timeline: Optional[int] = Field(None, ge=1, description="Target sales timeline (days)")
    
    # Analysis options
    include_market_analysis: bool = Field(default=True, description="Include market analysis")
    include_competition_analysis: bool = Field(default=True, description="Include competition analysis")


class AIPricingAnalysisResponse(BaseModel):
    """Schema for AI pricing analysis response."""
    
    # Price recommendations
    suggested_price: Decimal = Field(description="AI-suggested optimal price")
    price_range: Dict[str, Decimal] = Field(description="Recommended price range (min, max)")
    confidence_score: float = Field(ge=0, le=100, description="Confidence in recommendation")
    
    # Analysis factors
    price_factors: List[Dict[str, Any]] = Field(description="Factors affecting the price")
    market_position: str = Field(description="Position vs. market (BELOW, AT, ABOVE)")
    
    # Strategy recommendations
    pricing_strategy: str = Field(description="Recommended pricing strategy")
    revenue_projections: Dict[str, Any] = Field(description="Revenue impact projections")
    
    # Market insights
    comparable_analysis: Optional[List[Dict[str, Any]]] = Field(None, description="Comparable properties analysis")
    market_trends: Optional[Dict[str, Any]] = Field(None, description="Relevant market trends")
    
    # Analysis metadata
    analysis_timestamp: str
    properties_analyzed: int = Field(description="Number of properties analyzed")


# Market analysis schemas
class AIMarketAnalysisRequest(BaseModel):
    """Schema for AI market analysis request."""
    
    # Geographic scope
    region: str = Field(..., description="Region to analyze")
    city: Optional[str] = Field(None, description="City to analyze")
    districts: Optional[List[str]] = Field(None, description="Specific districts")
    
    # Analysis scope
    property_types: Optional[List[str]] = Field(None, description="Property types to include")
    price_segments: Optional[List[str]] = Field(None, description="Price segments to analyze")
    
    # Analysis parameters
    analysis_depth: str = Field(default="DETAILED", description="Analysis depth")
    time_horizon: int = Field(default=12, ge=1, le=60, description="Analysis horizon (months)")
    
    # Special focuses
    focus_areas: Optional[List[str]] = Field(None, description="Special focus areas")
    include_predictions: bool = Field(default=True, description="Include future predictions")


class AIMarketAnalysisResponse(BaseModel):
    """Schema for AI market analysis response."""
    
    # Overall market assessment
    market_health: float = Field(ge=0, le=100, description="Overall market health score")
    market_phase: str = Field(description="Market phase (GROWTH, PEAK, DECLINE, RECOVERY)")
    
    # Trend analysis
    trend_analysis: Dict[str, Any] = Field(description="Market trend analysis")
    price_movements: Dict[str, Any] = Field(description="Price movement analysis")
    
    # Opportunities and risks
    opportunity_areas: List[Dict[str, Any]] = Field(description="Identified opportunities")
    risk_factors: List[Dict[str, Any]] = Field(description="Key risk factors")
    
    # Predictions
    price_predictions: Optional[Dict[str, Any]] = Field(None, description="Price predictions")
    volume_predictions: Optional[Dict[str, Any]] = Field(None, description="Volume predictions")
    
    # Strategic insights
    investment_recommendations: List[str] = Field(description="Investment recommendations")
    strategic_insights: List[str] = Field(description="Strategic insights for developers")
    
    # Market data
    market_statistics: Dict[str, Any] = Field(description="Key market statistics")
    competitive_landscape: Optional[Dict[str, Any]] = Field(None, description="Competitive analysis")
    
    # Analysis metadata
    analysis_timestamp: str
    data_sources_count: int = Field(description="Number of data sources analyzed")
    confidence_level: float = Field(ge=0, le=100, description="Overall analysis confidence")
