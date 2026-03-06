-- ============================================================
-- SENTINEL 1930 — Master Schema & Demo Data Seed
-- Complete Project Setup for Supabase SQL Editor
-- ============================================================

-- I. SCHEMA SETUP (IDEMPOTENT)
-- ------------------------------------------------------------

-- 1. Users & RBAC
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR,
    role VARCHAR NOT NULL DEFAULT 'common',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 2. Call Records
CREATE TABLE IF NOT EXISTS call_records (
    id SERIAL PRIMARY KEY,
    caller_num TEXT NOT NULL,
    receiver_num TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    duration INTEGER,
    call_type TEXT,
    metadata_json JSONB,
    fraud_risk_score FLOAT,
    verdict TEXT
);

-- 3. Detection Details
CREATE TABLE IF NOT EXISTS detection_details (
    id SERIAL PRIMARY KEY,
    call_id INTEGER REFERENCES call_records(id) ON DELETE CASCADE,
    feature_name TEXT NOT NULL,
    feature_value FLOAT,
    impact_score FLOAT
);

-- 4. Suspicious Numbers
CREATE TABLE IF NOT EXISTS suspicious_numbers (
    id SERIAL PRIMARY KEY,
    phone_number TEXT UNIQUE NOT NULL,
    reputation_score FLOAT DEFAULT 0.0,
    category TEXT,
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    report_count INTEGER DEFAULT 0
);

-- 5. Honeypot Sessions
CREATE TABLE IF NOT EXISTS honeypot_sessions (
    id SERIAL PRIMARY KEY,
    session_id TEXT UNIQUE NOT NULL,
    caller_num TEXT,
    persona TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Honeypot Messages
CREATE TABLE IF NOT EXISTS honeypot_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES honeypot_sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- 7. System Stats
CREATE TABLE IF NOT EXISTS system_stats (
    id SERIAL PRIMARY KEY,
    category TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    metadata_json JSONB,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. System Actions (Audit Log for Dashboard Interactions)
CREATE TABLE IF NOT EXISTS system_actions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action_type TEXT NOT NULL, -- 'BLOCK', 'FREEZE', 'FLAG', 'EXPORT', etc.
    target_id TEXT, -- Phone number, VPA, Session ID
    metadata_json JSONB,
    status TEXT DEFAULT 'success',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- II. DEMO DATA SEEDING
-- ------------------------------------------------------------

-- 1. Demo Users (bcrypt hashed passwords)
INSERT INTO users (username, email, hashed_password, full_name, role, is_active) VALUES
('admin', 'admin@sentinel1930.gov.in', '$2b$12$Z1SL43d4O7vf2uUXGwOjnO1riRM/uk1ykOzJCqKaWRtqm4D3yUyR2', 'System Administrator', 'admin', TRUE),
('police_officer', 'sharma@police.gov.in', '$2b$12$o5yX1fECCbKFvUTPq56cC.ShuuLkIqPKv5znOcY9vqRWflnMFNntW', 'Inspector Sharma', 'police', TRUE),
('sbi_bank', 'fraud@sbi.co.in', '$2b$12$0lJywZiEJbYfiJz.XJn0wuMPJjEjnGkGBpyBxSv3dxTVgacfNdvkW', 'SBI Fraud Cell', 'bank', TRUE),
('citizen', 'ravi@gmail.com', '$2b$12$kd5k21LeGXaS/GyrzkF62.UlmTrOyEvJQMdb3Q7nMaG/oY3VGSHnW', 'Ravi Kumar', 'common', TRUE),
('govt_analyst', 'analyst@mha.gov.in', '$2b$12$6WLXToWBey3MND/MFEjAt.S7YAPINaekqtsBKBerP5SYuCGJgD6BK', 'MHA Analyst', 'government', TRUE),
('jio_telecom', 'security@jio.com', '$2b$12$AOAPD5xR7BSfUBZRkcCJduR4iks/K7ghoekJkyC6NJkd.NNHBJW42', 'Jio Security', 'telecom', TRUE),
('court_clerk', 'clerk@hc.gov.in', '$2b$12$e7gibOUTFTmBh9AAtYFKKOV9cAsfvZ/OOV/WbiTN5B/AqD0sdpiVO', 'HC Clerk', 'court', TRUE)
ON CONFLICT (username) DO NOTHING;

-- 2. Demo Call Records
INSERT INTO call_records (caller_num, receiver_num, duration, call_type, metadata_json, fraud_risk_score, verdict) VALUES
('+91 9876543210', '+91 8888888888', 124, 'incoming', '{"location": "Mumbai, MH", "device": "Android", "carrier": "Jio"}', 0.12, 'safe'),
('+91 9123456789', '+91 7777777777', 45, 'incoming', '{"location": "Delhi, NCR", "device": "iPhone", "carrier": "Airtel"}', 0.89, 'scam'),
('+91 8234567890', '+91 6666666666', 210, 'incoming', '{"location": "Bangalore, KA", "device": "Android", "carrier": "Vi"}', 0.45, 'suspicious');

-- 3. Demo Detection Details (Linked to call_id 2 - the scam one)
INSERT INTO detection_details (call_id, feature_name, feature_value, impact_score) VALUES
(2, 'Voice Stress', 0.85, 0.4),
(2, 'Number Velocity', 0.92, 0.3),
(2, 'Script Matching', 0.78, 0.2);

-- 4. Demo Suspicious Numbers
INSERT INTO suspicious_numbers (phone_number, reputation_score, category, report_count) VALUES
('+91 9123456789', 0.92, 'Lottery Scam', 54),
('+91 8234567890', 0.48, 'Bank Rep Impersonation', 12),
('+91 7011223344', 0.81, 'Mule Recruitment', 31);

-- 5. Demo Honeypot Sessions
INSERT INTO honeypot_sessions (session_id, caller_num, persona, status) VALUES
('SES-9921', '+91 9123456789', 'Retired Teacher', 'completed'),
('SES-9922', '+91 7011223344', 'College Student', 'active');

-- 6. Demo Honeypot Messages
INSERT INTO honeypot_messages (session_id, role, content) VALUES
(1, 'user', 'Hello, I am calling from KBC department regarding your prize.'),
(1, 'assistant', 'Oh really? A prize for me? How much is it?'),
(1, 'user', 'It is 25 lakhs, but first you need to pay tax of 5000.'),
(1, 'assistant', 'I don''t have 5000 right now, can you deduct it from the prize?');

-- 7. System Stats (Fixes Dashboard Crashes)
INSERT INTO system_stats (category, key, value, metadata_json) VALUES
('deepfake', 'incidents', NULL, '[{"type": "Video Overlay", "risk": "High", "status": "Deepfake"}, {"type": "Voice Synth", "risk": "Medium", "status": "Suspicious"}]'),
('deepfake', 'model_status', NULL, '{"liveness": "Active", "gan_detector": "Operational", "false_positive_rate": "0.02%"}'),
('mule', 'ads', NULL, '[{"id": 1, "title": "Data Entry Specialist", "salary": "₹50k", "platform": "Telegram", "risk": 0.85, "status": "Mule Campaign"}]'),
('mule', 'patterns', NULL, '[{"label": "Remote Job Scam", "value": 82}, {"label": "Commission Based", "value": 65}]'),
('inoculation', 'scenarios', NULL, '{"bank_kyc": {"name": "Bank KYC", "desc": "Fake KYC drill", "steps": ["SMS Sent", "Link Clicked"]}}'),
('inoculation', 'impact', NULL, '{"prevented": "12,402", "velocity": "+14.2%"}'),
('upi', 'dashboard', NULL, '{"vpa_checks_24h": "45,201", "flags": "1,042", "vpa_risk_percent": 12}'),
('upi', 'threat_feed', NULL, '[{"id": "VPA-8921", "time": "2m ago", "risk": "High", "type": "Collect Request"}]'),
('score', 'national', NULL, '{"value": 742, "change": "+12.4", "nodes": 4520, "heatmap": [45, 62, 38, 55, 72, 48, 65, 50, 42, 58, 70, 45]}'),
('score', 'factors', NULL, '[{"label": "Identity Trust", "value": "High", "percent": 92}, {"label": "Behavioral Risk", "value": "Medium", "percent": 74}]');

-- 8. Overview Stats
INSERT INTO system_stats (category, key, value) VALUES
('overview', 'scams_blocked', '1,24,502'),
('overview', 'citizens_protected', '89,210'),
('overview', 'estimated_savings', '142'),
('overview', 'active_threats', '1,042');
