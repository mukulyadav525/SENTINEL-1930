from typing import Dict
from models.database import CallRecord, DetectionDetail

def calculate_fraud_risk(caller_num: str, metadata: Dict) -> Dict:
    features = []
    base_score = 0.0
    
    # 1. Check Caller Reputation (Simulated)
    if caller_num.startswith("+919000"): 
        features.append({"name": "reputation_match", "value": 1.0, "impact": 0.4})
        base_score += 0.4
        
    # 2. Call Velocity (Simulated)
    velocity = metadata.get("velocity", 1)
    if velocity > 50:
        features.append({"name": "high_velocity", "value": float(velocity), "impact": 0.3})
        base_score += 0.3
        
    # 3. Geographic Anomaly (Simulated)
    if metadata.get("location") == "Overseas" and caller_num.startswith("+91"):
        features.append({"name": "geo_spoofing", "value": 1.0, "impact": 0.5})
        base_score += 0.5
        
    final_score = min(1.0, base_score)
    
    verdict = "safe"
    if final_score > 0.7:
        verdict = "scam"
    elif final_score > 0.3:
        verdict = "suspicious"
        
    return {
        "score": final_score,
        "verdict": verdict,
        "features": features
    }
