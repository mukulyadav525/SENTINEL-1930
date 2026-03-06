-- ============================================================
-- SENTINEL 1930 — RBAC Users Table & Demo Data
-- Paste this in Supabase SQL Editor
-- ============================================================

-- 1. Create the users table
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

-- Create indexes
CREATE INDEX IF NOT EXISTS ix_users_id ON users (id);
CREATE INDEX IF NOT EXISTS ix_users_username ON users (username);
CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);

-- 2. Insert demo users (one per role)
-- Passwords are bcrypt-hashed

INSERT INTO users (username, email, hashed_password, full_name, role, is_active) VALUES
-- admin / sentinel1930
('admin', 'admin@sentinel1930.gov.in', '$2b$12$Z1SL43d4O7vf2uUXGwOjnO1riRM/uk1ykOzJCqKaWRtqm4D3yUyR2', 'System Administrator', 'admin', TRUE),

-- police_officer / police123
('police_officer', 'sharma@police.gov.in', '$2b$12$o5yX1fECCbKFvUTPq56cC.ShuuLkIqPKv5znOcY9vqRWflnMFNntW', 'Inspector Sharma', 'police', TRUE),

-- sbi_bank / bank123
('sbi_bank', 'fraud@sbi.co.in', '$2b$12$0lJywZiEJbYfiJz.XJn0wuMPJjEjnGkGBpyBxSv3dxTVgacfNdvkW', 'SBI Fraud Cell', 'bank', TRUE),

-- citizen / citizen123
('citizen', 'ravi@gmail.com', '$2b$12$kd5k21LeGXaS/GyrzkF62.UlmTrOyEvJQMdb3Q7nMaG/oY3VGSHnW', 'Ravi Kumar', 'common', TRUE),

-- govt_analyst / govt123
('govt_analyst', 'analyst@mha.gov.in', '$2b$12$6WLXToWBey3MND/MFEjAt.S7YAPINaekqtsBKBerP5SYuCGJgD6BK', 'MHA Analyst', 'government', TRUE),

-- jio_telecom / telecom123
('jio_telecom', 'security@jio.com', '$2b$12$AOAPD5xR7BSfUBZRkcCJduR4iks/K7ghoekJkyC6NJkd.NNHBJW42', 'Jio Security', 'telecom', TRUE),

-- court_clerk / court123
('court_clerk', 'clerk@hc.gov.in', '$2b$12$e7gibOUTFTmBh9AAtYFKKOV9cAsfvZ/OOV/WbiTN5B/AqD0sdpiVO', 'HC Clerk', 'court', TRUE)

ON CONFLICT (username) DO NOTHING;
