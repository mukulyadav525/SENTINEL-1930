-- ============================================================
-- SENTINEL 1930 — System Statistics Seed Data
-- Paste this in Supabase SQL Editor to fix the 404/Crash errors
-- ============================================================

-- DEEPFAKE STATS
INSERT INTO system_stats (category, key, metadata_json) VALUES
('deepfake', 'incidents', '[
    {"type": "Video Call Overlay", "risk": "High", "status": "Deepfake"},
    {"type": "Voice Synthesis", "risk": "Medium", "status": "Suspicious"},
    {"type": "Face Swap", "risk": "High", "status": "Deepfake"},
    {"type": "Liveness Bypass", "risk": "Low", "status": "Verified"}
]'),
('deepfake', 'model_status', '{
    "liveness": "Active",
    "gan_detector": "Operational",
    "false_positive_rate": "0.02%"
}');

-- MULE INTERCEPTOR STATS
INSERT INTO system_stats (category, key, metadata_json) VALUES
('mule', 'ads', '[
    {"id": 1, "title": "Data Entry Specialist (Remote)", "salary": "₹50k/month", "platform": "Telegram", "risk": 0.85, "status": "Mule Campaign"},
    {"id": 2, "title": "International Funds Manager", "salary": "15% Comm.", "platform": "WhatsApp", "risk": 0.95, "status": "High Risk"},
    {"id": 3, "title": "Crypto Arbitrage Assistant", "salary": "₹5k/day", "platform": "Facebook", "risk": 0.72, "status": "Suspicious"}
]'),
('mule', 'patterns', '[
    {"label": "Remote Job Scam", "value": 82},
    {"label": "Commission Based", "value": 65},
    {"label": "Urgent Hiring", "value": 41}
]');

-- INOCULATION ENGINE STATS
INSERT INTO system_stats (category, key, metadata_json) VALUES
('inoculation', 'scenarios', '{
    "bank_kyc": {
        "name": "Bank KYC Update",
        "desc": "Simulates a fake bank representative asking for KYC details via SMS link.",
        "steps": ["SMS DISPATCHED", "LINK CLICKED", "CREDENTIALS ENTERED", "INTERCEPTED"]
    },
    "lottery_win": {
        "name": "KBC Lottery Win",
        "desc": "Simulates a WhatsApp message claiming a big lottery win with a processing fee.",
        "steps": ["MSG DISPATCHED", "VPA REQUESTED", "FEE PAID", "INTERCEPTED"]
    }
}'),
('inoculation', 'impact', '{
    "prevented": "12,402",
    "velocity": "+14.2%"
}');

-- UPI SHIELD STATS
INSERT INTO system_stats (category, key, metadata_json) VALUES
('upi', 'dashboard', '{
    "vpa_checks_24h": "45,201",
    "flags": "1,042",
    "vpa_risk_percent": 12
}'),
('upi', 'threat_feed', '[
    {"id": "VPA-8921", "time": "2m ago", "risk": "High", "type": "Collect Request"},
    {"id": "VPA-6612", "time": "5m ago", "risk": "Medium", "type": "Duplicate Merchant"},
    {"id": "VPA-1109", "time": "12m ago", "risk": "High", "type": "Cashback Trap"}
]');

-- SCORE ENGINE STATS
INSERT INTO system_stats (category, key, metadata_json) VALUES
('score', 'national', '{
    "value": 742,
    "change": "+12.4",
    "nodes": 4520,
    "heatmap": [45, 62, 38, 55, 72, 48, 65, 50, 42, 58, 70, 45]
}'),
('score', 'factors', '[
    {"label": "Identity Trust", "value": "High", "percent": 92},
    {"label": "Behavioral Risk", "value": "Medium", "percent": 74},
    {"label": "Network Safety", "value": "Normal", "percent": 88}
]');
