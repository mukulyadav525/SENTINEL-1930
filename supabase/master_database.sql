-- ============================================================
-- SENTINEL 1930 — MASTER OF MASTER SCHEMA & ENRICHED SEED
-- Version: 3.0 (Final Sync)
-- Description: Complete Project Setup for Supabase SQL Editor
-- This script reconstructs the database for 100% dashboard connectivity.
-- ============================================================

-- I. CLEANUP & SCHEMA (IDEMPOTENT)
-- ------------------------------------------------------------

DROP TABLE IF EXISTS scam_clusters CASCADE;
DROP TABLE IF EXISTS scam_clusters CASCADE;
DROP TABLE IF EXISTS system_actions CASCADE;
DROP TABLE IF EXISTS honeypot_messages CASCADE;
DROP TABLE IF EXISTS honeypot_sessions CASCADE;
DROP TABLE IF EXISTS honeypot_personas CASCADE;
DROP TABLE IF EXISTS detection_details CASCADE;
DROP TABLE IF EXISTS call_records CASCADE;
DROP TABLE IF EXISTS suspicious_numbers CASCADE;
DROP TABLE IF EXISTS system_stats CASCADE;
DROP TABLE IF EXISTS users CASCADE;

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

-- 4. Suspicious Numbers Registry
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

-- 7. System Stats (Unified Data Store)
CREATE TABLE IF NOT EXISTS system_stats (
    id SERIAL PRIMARY KEY,
    category TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    metadata_json JSONB,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. System Actions Audit Log
CREATE TABLE IF NOT EXISTS system_actions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action_type VARCHAR(50) NOT NULL,
    target_id VARCHAR(100),
    metadata_json JSONB,
    status VARCHAR(20) DEFAULT 'success',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. Honeypot Personas
CREATE TABLE IF NOT EXISTS honeypot_personas (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE,
    language VARCHAR(50),
    speaker VARCHAR(50),
    pace FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. Scam Clusters
CREATE TABLE IF NOT EXISTS scam_clusters (
    id SERIAL PRIMARY KEY,
    cluster_id VARCHAR(50) UNIQUE,
    risk_level VARCHAR(20),
    location VARCHAR(100),
    linked_vpas INTEGER DEFAULT 0,
    honeypot_hits INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- II. ENRICHED DEMO DATA SEEDING
-- ------------------------------------------------------------

-- 1. Demo Users (Password: password123)
-- bcrypt hash for 'password123'
INSERT INTO users (username, email, hashed_password, full_name, role) VALUES
('admin', 'admin@sentinel.gov.in', '$2b$12$rZ2e19sttSddtNJINi5LTey0l9ikpRSVvKFfPV/g9r7SybHkGdCN2', 'System Administrator', 'admin'),
('inspector', 'sharma@police.gov.in', '$2b$12$rZ2e19sttSddtNJINi5LTey0l9ikpRSVvKFfPV/g9r7SybHkGdCN2', 'Inspector Sharma', 'police'),
('sbi_fraud', 'cell@sbi.co.in', '$2b$12$rZ2e19sttSddtNJINi5LTey0l9ikpRSVvKFfPV/g9r7SybHkGdCN2', 'SBI Fraud Desk', 'bank'),
('analyst', 'analyst@mha.gov.in', '$2b$12$rZ2e19sttSddtNJINi5LTey0l9ikpRSVvKFfPV/g9r7SybHkGdCN2', 'MHA Data Analyst', 'government'),
('jio_security', 'security@jio.com', '$2b$12$rZ2e19sttSddtNJINi5LTey0l9ikpRSVvKFfPV/g9r7SybHkGdCN2', 'Jio Security Lead', 'telecom'),
('registrar', 'registrar@hc.gov.in', '$2b$12$rZ2e19sttSddtNJINi5LTey0l9ikpRSVvKFfPV/g9r7SybHkGdCN2', 'Court Registrar', 'court'),
('citizen', 'citizen@outlook.com', '$2b$12$rZ2e19sttSddtNJINi5LTey0l9ikpRSVvKFfPV/g9r7SybHkGdCN2', 'Common Man', 'common')
ON CONFLICT (username) DO NOTHING;

-- Additional users from instruction
INSERT INTO users (username, hashed_password, full_name, role) VALUES 
('admin@sentinel.gov.in', '$2b$12$rZ2e19sttSddtNJINi5LTey0l9ikpRSVvKFfPV/g9r7SybHkGdCN2', 'System Administrator', 'admin'),
('bank_officer@sbi.co.in', '$2b$12$rZ2e19sttSddtNJINi5LTey0l9ikpRSVvKFfPV/g9r7SybHkGdCN2', 'SBI Branch Manager', 'bank')
ON CONFLICT (username) DO NOTHING;

-- 2. Call Records (Scam & Safe Samples)
INSERT INTO call_records (caller_num, receiver_num, duration, call_type, metadata_json, fraud_risk_score, verdict) VALUES
('+91 9123456789', '+91 9876543210', 45, 'incoming', '{"location": "Delhi", "carrier": "Airtel"}', 0.92, 'scam'),
('+91 8234567890', '+91 8888888888', 120, 'incoming', '{"location": "Mumbai", "carrier": "Jio"}', 0.12, 'safe'),
('+91 7011223344', '+91 7777777777', 15, 'incoming', '{"location": "Jamtara", "carrier": "Vi"}', 0.88, 'scam');

-- 3. Detection Details
INSERT INTO detection_details (call_id, feature_name, feature_value, impact_score) VALUES
(1, 'Voice Stress', 0.85, 0.4), (1, 'Velocity', 12.0, 0.3), (1, 'Script Match', 0.78, 0.2),
(3, 'Location Anomaly', 1.0, 0.5), (3, 'Reputation', 0.9, 0.4);

-- 4. SYSTEM STATS MASTER LOG (Frontend Sync)

-- OVERVIEW
INSERT INTO system_stats (category, key, value) VALUES
('overview', 'scams_blocked', '1,54,201'),
('overview', 'citizens_protected', '1,12,450'),
('overview', 'estimated_savings', '₹452 Cr'),
('overview', 'active_threats', '1,042');

-- SCORE ENGINE
INSERT INTO system_stats (category, key, metadata_json) VALUES
('score', 'national', '{"value": 742, "change": "+12.4%", "nodes": 4520, "heatmap": [45, 62, 38, 55, 72, 48, 65, 50, 42, 58, 70, 45]}'),
('score', 'factors', '[{"label": "Identity Trust", "value": "High", "percent": 92}, {"label": "Behavioral Risk", "value": "Medium", "percent": 74}, {"label": "Network Reputation", "value": "High", "percent": 88}]');

-- DEEPFAKE DEFENSE
INSERT INTO system_stats (category, key, metadata_json) VALUES
('deepfake', 'incidents', '[{"type": "Video Overlay", "risk": "High", "status": "Deepfake"}, {"type": "Voice Synth", "risk": "Medium", "status": "Suspicious"}, {"type": "Face Swap", "risk": "Critical", "status": "Detected"}]'),
('deepfake', 'model_status', '{"liveness": "Active", "gan_detector": "Operational", "false_positive_rate": "0.02%"}');

-- MULE DETECTION
INSERT INTO system_stats (category, key, metadata_json) VALUES
('mule', 'ads', '[{"id": 1, "title": "Commission Agent", "salary": "₹50k/mo", "platform": "Telegram", "risk": 0.85, "status": "Mule Recruitment"}, {"id": 2, "title": "Data Entry Remote", "salary": "₹25k/mo", "platform": "WhatsApp", "risk": 0.72, "status": "Suspicious"}]'),
('mule', 'patterns', '[{"label": "Remote Job Scam", "value": 82}, {"label": "Rental Scam", "value": 45}, {"label": "Investment", "value": 31}]');

-- UPI PROTECTION
INSERT INTO system_stats (category, key, metadata_json) VALUES
('upi', 'dashboard', '{"vpa_checks_24h": "45,201", "flags": "1,042", "vpa_risk_percent": 12}'),
('upi', 'threat_feed', '[{"id": "VPA-8921", "time": "2m ago", "risk": "High", "type": "Collect Request", "vpa": "airtel.pay@ybl"}, {"id": "VPA-1102", "time": "15m ago", "risk": "Critical", "type": "Fraudulent Link", "vpa": "lottery.99@okhdfc"}]');

-- BHARAT LAYER (Corrected for Dynamic Load)
INSERT INTO system_stats (category, key, metadata_json) VALUES
('bharat', 'regions', '[{"id": "north", "name": "North India (Haryana/Punjab)", "towers": 1240, "reach": "8.2M"}, {"id": "east", "name": "East India (Bihar/WB)", "towers": 2150, "reach": "12.4M"}, {"id": "west", "name": "West India (Rajasthan/Gujarat)", "towers": 1890, "reach": "10.1M"}]');

-- INOCULATION SCRIPTS (Corrected to Dictionary for Frontend)
INSERT INTO system_stats (category, key, metadata_json) VALUES
('inoculation', 'scenarios', '{
    "bank_kyc": {"name": "Bank KYC Scam", "desc": "Simulated phishing message asking for KYC update via suspicious link.", "steps": ["Dispatching SMS", "Simulating Click-through", "Capturing Awareness Index"]},
    "lottery_win": {"name": "Lottery Win Scam", "desc": "Message claiming lottery win to test user report-first behavior.", "steps": ["Dispatching WhatsApp", "Monitoring Response", "Reporting to 1930 Simulation"]},
    "upi_refund": {"name": "UPI Refund Trap", "desc": "Collect-request trap simulation for mobile payment education.", "steps": ["Sending VPA Link", "Verifying Denial Rate", "Issuing Safety Certificate"]}
}'),
('inoculation', 'impact', '{"prevented": "12,402", "velocity": "+14.2%"}');

-- 5. Scam Clusters Seed
INSERT INTO scam_clusters (cluster_id, risk_level, location, linked_vpas, honeypot_hits) VALUES
('POD-72X', 'CRITICAL', 'Noida, Sector 62', 42, 1205),
('POD-11M', 'HIGH', 'Jamtara, Jharkhand', 18, 450),
('POD-09K', 'MEDIUM', 'Bharatpur, Rajasthan', 12, 210)
ON CONFLICT (cluster_id) DO NOTHING;

-- 6. Constant Metrics (Fatigue, etc.)
INSERT INTO system_stats (category, key, value) VALUES
('honeypot', 'fatigue_index', '78.4%');

-- III. SECURITY POLICIES (RLS)
-- ------------------------------------------------------------
ALTER TABLE system_actions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow authenticated inserts" ON system_actions;
CREATE POLICY "Allow authenticated inserts" 
ON system_actions FOR INSERT 
TO authenticated 
WITH CHECK (true);

DROP POLICY IF EXISTS "Allow authenticated selects" ON system_actions;
CREATE POLICY "Allow authenticated selects" 
ON system_actions FOR SELECT 
TO authenticated 
USING (true);

COMMIT;
