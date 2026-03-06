-- Supabase Initial Schema Migration
-- Created: 2026-03-06

-- 1. Call Records
CREATE TABLE IF NOT EXISTS call_records (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    caller_num TEXT NOT NULL,
    receiver_num TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    duration INTEGER,
    call_type TEXT,
    metadata_json JSONB,
    fraud_risk_score FLOAT,
    verdict TEXT
);

CREATE INDEX IF NOT EXISTS idx_call_records_caller_num ON call_records(caller_num);

-- 2. Detection Details
CREATE TABLE IF NOT EXISTS detection_details (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    call_id BIGINT REFERENCES call_records(id) ON DELETE CASCADE,
    feature_name TEXT NOT NULL,
    feature_value FLOAT,
    impact_score FLOAT
);

-- 3. Suspicious Numbers
CREATE TABLE IF NOT EXISTS suspicious_numbers (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    phone_number TEXT UNIQUE NOT NULL,
    reputation_score FLOAT DEFAULT 0.0,
    category TEXT,
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    report_count INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_suspicious_numbers_phone ON suspicious_numbers(phone_number);

-- 4. Honeypot Sessions
CREATE TABLE IF NOT EXISTS honeypot_sessions (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    session_id TEXT UNIQUE NOT NULL,
    caller_num TEXT,
    persona TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_honeypot_sessions_sid ON honeypot_sessions(session_id);

-- 5. Honeypot Messages
CREATE TABLE IF NOT EXISTS honeypot_messages (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    session_id BIGINT REFERENCES honeypot_sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- 6. System Stats
CREATE TABLE IF NOT EXISTS system_stats (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    category TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    metadata_json JSONB,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS (Optional, can be configured in Supabase Dashboard)
-- ALTER TABLE call_records ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Allow read for authenticated users" ON call_records FOR SELECT USING (auth.role() = 'authenticated');
