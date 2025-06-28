"""
MongoDB document models using Beanie ODM.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from beanie import Document, Indexed
from pydantic import BaseModel, Field


class ApplicationLog(Document):
    """Application logs collection."""
    
    level: str = Field(..., description="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    message: str = Field(..., description="Log message")
    logger_name: str = Field(..., description="Logger name")
    module: Optional[str] = Field(None, description="Module name")
    function: Optional[str] = Field(None, description="Function name")
    line_number: Optional[int] = Field(None, description="Line number")
    
    # Request context
    request_id: Optional[str] = Field(None, description="Request ID for tracing")
    user_id: Optional[str] = Field(None, description="User ID if available")
    session_id: Optional[str] = Field(None, description="Session ID")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    
    # Additional data
    extra_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional log data")
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Log timestamp")
    
    class Settings:
        name = "application_logs"
        indexes = [
            [("level", 1), ("timestamp", -1)],
            [("logger_name", 1), ("timestamp", -1)],
            [("user_id", 1), ("timestamp", -1)],
            [("request_id", 1)],
        ]


class AuditLog(Document):
    """Audit logs for tracking user actions."""
    
    event_type: str = Field(..., description="Type of audit event")
    user_id: Optional[str] = Field(None, description="User who performed the action")
    action: str = Field(..., description="Action performed")
    resource: str = Field(..., description="Resource affected")
    resource_id: Optional[str] = Field(None, description="ID of the affected resource")
    
    # Request context
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    session_id: Optional[str] = Field(None, description="Session ID")
    
    # Data
    data: Dict[str, Any] = Field(default_factory=dict, description="Additional audit data")
    changes: Optional[Dict[str, Any]] = Field(None, description="Changes made (before/after)")
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Audit timestamp")
    success: bool = Field(True, description="Whether the action was successful")
    error_message: Optional[str] = Field(None, description="Error message if action failed")
    
    class Settings:
        name = "audit_logs"
        indexes = [
            [("user_id", 1), ("timestamp", -1)],
            [("action", 1), ("timestamp", -1)],
            [("resource", 1), ("timestamp", -1)],
            [("timestamp", -1)],
        ]


class PropertyDocument(Document):
    """Property documents stored in MongoDB."""
    
    property_id: Indexed(str) = Field(..., description="Property ID from PostgreSQL")
    document_type: str = Field(..., description="Type of document (PLAN, CERTIFICATE, etc.)")
    title: str = Field(..., description="Document title")
    description: Optional[str] = Field(None, description="Document description")
    
    # File information
    file_url: str = Field(..., description="Document URL")
    file_name: str = Field(..., description="Original file name")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type")
    file_hash: Optional[str] = Field(None, description="File hash for integrity")
    
    # Metadata
    is_verified: bool = Field(False, description="Whether document is verified")
    is_public: bool = Field(False, description="Whether document is publicly accessible")
    uploaded_by: Optional[str] = Field(None, description="User who uploaded the document")
    
    # OCR and content extraction
    extracted_text: Optional[str] = Field(None, description="Extracted text from document")
    ocr_data: Optional[Dict[str, Any]] = Field(None, description="OCR processing results")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "property_documents"
        indexes = [
            [("property_id", 1), ("created_at", -1)],
            [("document_type", 1)],
            [("is_verified", 1)],
            [("uploaded_by", 1)],
        ]


class UserAnalytics(Document):
    """User behavior analytics."""
    
    user_id: Optional[str] = Field(None, description="User ID (null for anonymous)")
    session_id: Indexed(str) = Field(..., description="Session ID")
    
    # User context
    ip_address: str = Field(..., description="Client IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    country: Optional[str] = Field(None, description="Country from IP")
    city: Optional[str] = Field(None, description="City from IP")
    device_type: Optional[str] = Field(None, description="Device type (mobile, desktop, tablet)")
    
    # Behavior data
    page_views: List[Dict[str, Any]] = Field(default_factory=list, description="Page view events")
    property_views: List[Dict[str, Any]] = Field(default_factory=list, description="Property view events")
    searches: List[Dict[str, Any]] = Field(default_factory=list, description="Search events")
    actions: List[Dict[str, Any]] = Field(default_factory=list, description="User actions")
    
    # Session metadata
    session_start: datetime = Field(default_factory=datetime.utcnow)
    session_end: Optional[datetime] = Field(None)
    session_duration: Optional[int] = Field(None, description="Session duration in seconds")
    
    # Calculated metrics
    total_page_views: int = Field(0, description="Total page views in session")
    total_property_views: int = Field(0, description="Total property views in session")
    total_searches: int = Field(0, description="Total searches in session")
    bounce_rate: Optional[float] = Field(None, description="Bounce rate for session")
    
    class Settings:
        name = "user_analytics"
        indexes = [
            [("user_id", 1), ("session_start", -1)],
            [("session_id", 1)],
            [("ip_address", 1)],
            [("session_start", -1)],
        ]


class SearchQuery(Document):
    """Advanced search query storage and analysis."""
    
    query_id: Indexed(str) = Field(..., description="Unique query ID")
    user_id: Optional[str] = Field(None, description="User ID (null for anonymous)")
    session_id: str = Field(..., description="Session ID")
    
    # Query data
    raw_query: str = Field(..., description="Raw search query")
    processed_query: Optional[str] = Field(None, description="Processed/cleaned query")
    query_vector: Optional[List[float]] = Field(None, description="Query embedding vector")
    
    # Filters applied
    filters: Dict[str, Any] = Field(default_factory=dict, description="Applied filters")
    
    # Results
    results_count: int = Field(0, description="Number of results found")
    results_shown: int = Field(0, description="Number of results actually shown")
    clicked_results: List[str] = Field(default_factory=list, description="IDs of clicked results")
    
    # Performance metrics
    search_time_ms: Optional[float] = Field(None, description="Search execution time")
    relevance_score: Optional[float] = Field(None, description="Average relevance score")
    
    # Context
    page_number: int = Field(1, description="Page number requested")
    page_size: int = Field(20, description="Page size requested")
    sort_order: Optional[str] = Field(None, description="Sort order applied")
    
    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "search_queries"
        indexes = [
            [("user_id", 1), ("timestamp", -1)],
            [("raw_query", "text")],
            [("timestamp", -1)],
            [("results_count", 1)],
        ]


class NotificationLog(Document):
    """Notification delivery logs."""
    
    notification_id: Indexed(str) = Field(..., description="Unique notification ID")
    user_id: str = Field(..., description="Recipient user ID")
    
    # Notification details
    notification_type: str = Field(..., description="Type of notification")
    channel: str = Field(..., description="Delivery channel (email, sms, push)")
    subject: Optional[str] = Field(None, description="Notification subject")
    content: str = Field(..., description="Notification content")
    
    # Delivery status
    status: str = Field("pending", description="Delivery status")
    delivery_attempts: int = Field(0, description="Number of delivery attempts")
    delivered_at: Optional[datetime] = Field(None, description="Delivery timestamp")
    read_at: Optional[datetime] = Field(None, description="Read timestamp")
    
    # Metadata
    priority: str = Field("normal", description="Notification priority")
    scheduled_for: Optional[datetime] = Field(None, description="Scheduled delivery time")
    expires_at: Optional[datetime] = Field(None, description="Expiration time")
    
    # Error tracking
    error_message: Optional[str] = Field(None, description="Error message if delivery failed")
    retry_count: int = Field(0, description="Number of retries")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "notification_logs"
        indexes = [
            [("user_id", 1), ("created_at", -1)],
            [("notification_type", 1)],
            [("status", 1)],
            [("scheduled_for", 1)],
            [("created_at", -1)],
        ]


class PerformanceMetric(Document):
    """Application performance metrics."""
    
    metric_type: str = Field(..., description="Type of metric")
    metric_name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    unit: Optional[str] = Field(None, description="Metric unit")
    
    # Context
    endpoint: Optional[str] = Field(None, description="API endpoint")
    method: Optional[str] = Field(None, description="HTTP method")
    user_id: Optional[str] = Field(None, description="User ID")
    session_id: Optional[str] = Field(None, description="Session ID")
    
    # Additional data
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metric data")
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "performance_metrics"
        indexes = [
            [("metric_type", 1), ("metric_name", 1), ("timestamp", -1)],
            [("endpoint", 1), ("timestamp", -1)],
            [("timestamp", -1)],
        ]


class ErrorLog(Document):
    """Application error logs."""
    
    error_id: Indexed(str) = Field(..., description="Unique error ID")
    error_type: str = Field(..., description="Error type/class")
    error_message: str = Field(..., description="Error message")
    
    # Stack trace and context
    stack_trace: Optional[str] = Field(None, description="Full stack trace")
    module: Optional[str] = Field(None, description="Module where error occurred")
    function: Optional[str] = Field(None, description="Function where error occurred")
    line_number: Optional[int] = Field(None, description="Line number")
    
    # Request context
    request_id: Optional[str] = Field(None, description="Request ID")
    user_id: Optional[str] = Field(None, description="User ID")
    session_id: Optional[str] = Field(None, description="Session ID")
    endpoint: Optional[str] = Field(None, description="API endpoint")
    method: Optional[str] = Field(None, description="HTTP method")
    
    # Error metadata
    severity: str = Field("error", description="Error severity")
    is_handled: bool = Field(True, description="Whether error was handled")
    resolution_status: str = Field("new", description="Resolution status")
    
    # Additional data
    context_data: Dict[str, Any] = Field(default_factory=dict, description="Additional context data")
    
    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")
    
    class Settings:
        name = "error_logs"
        indexes = [
            [("error_type", 1), ("timestamp", -1)],
            [("severity", 1), ("timestamp", -1)],
            [("user_id", 1), ("timestamp", -1)],
            [("endpoint", 1), ("timestamp", -1)],
            [("timestamp", -1)],
        ]
