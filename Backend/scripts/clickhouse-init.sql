-- Real Estate Platform ClickHouse Initialization
-- ClickHouse latest version required

-- Create database
CREATE DATABASE IF NOT EXISTS realestate_analytics;

USE realestate_analytics;

-- Property views analytics table
CREATE TABLE IF NOT EXISTS property_views (
    property_id String,
    user_id Nullable(String),
    session_id String,
    ip_address String,
    user_agent Nullable(String),
    referrer Nullable(String),
    timestamp DateTime,
    date Date DEFAULT toDate(timestamp)
) ENGINE = MergeTree()
PARTITION BY date
ORDER BY (property_id, timestamp)
SETTINGS allow_nullable_key = 1;

-- Property search analytics table
CREATE TABLE IF NOT EXISTS property_searches (
    search_id String,
    user_id Nullable(String),
    session_id String,
    search_query String,
    filters String, -- JSON string
    results_count UInt32,
    clicked_properties Array(String),
    timestamp DateTime,
    date Date DEFAULT toDate(timestamp)
) ENGINE = MergeTree()
PARTITION BY date
ORDER BY (timestamp);

-- User behavior analytics table
CREATE TABLE IF NOT EXISTS user_behavior (
    user_id Nullable(String),
    session_id String,
    event_type String,
    event_data String, -- JSON string
    page_url String,
    timestamp DateTime,
    date Date DEFAULT toDate(timestamp)
) ENGINE = MergeTree()
PARTITION BY date
ORDER BY (session_id, timestamp);

-- Performance metrics table
CREATE TABLE IF NOT EXISTS performance_metrics (
    endpoint String,
    method String,
    status_code UInt16,
    response_time_ms UInt32,
    user_id Nullable(String),
    ip_address String,
    timestamp DateTime,
    date Date DEFAULT toDate(timestamp)
) ENGINE = MergeTree()
PARTITION BY date
ORDER BY (endpoint, timestamp);

-- Business metrics table
CREATE TABLE IF NOT EXISTS business_metrics (
    metric_name String,
    metric_value Float64,
    dimensions String, -- JSON string
    timestamp DateTime,
    date Date DEFAULT toDate(timestamp)
) ENGINE = MergeTree()
PARTITION BY date
ORDER BY (metric_name, timestamp);
