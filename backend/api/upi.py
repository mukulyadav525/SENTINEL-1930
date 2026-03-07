from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from core.database import get_db
from models.database import SystemAction, SystemStat
from pydantic import BaseModel
import uuid
import logging
import datetime
import re
import json

logger = logging.getLogger("sentinel.upi")

router = APIRouter()

class UPIRequest(BaseModel):
    vpa: str

class MessageScanRequest(BaseModel):
    message: str

# T5 requirement: Simulated NPCI Blocklist
BLOCKLIST_VPAS = ["scammer@okaxis", "badactor@ybl", "mule@paytm", "fraud@icici"]

@router.post("/verify", response_model=dict)
async def verify_upi(req: UPIRequest, db: Session = Depends(get_db)):
    """
    T5 requirement: Check VPA against National Blocklist.
    """
    vpa = req.vpa.lower()
    is_blocked = vpa in BLOCKLIST_VPAS
    
    # Log the verification action
    new_action = SystemAction(
        action_type="UPI_VERIFY",
        target_id=vpa,
        metadata_json={"is_blocked": is_blocked},
        status="success"
    )
    db.add(new_action)
    db.commit()
    
    logger.info(f"UPI VERIFY: {vpa} | Blocked: {is_blocked}")
    
    return {
        "vpa": vpa,
        "is_flagged": is_blocked,
        "risk_level": "CRITICAL" if is_blocked else "SAFE",
        "timestamp": datetime.datetime.utcnow()
    }

@router.post("/freeze", response_model=dict)
async def request_upi_freeze(req: UPIRequest, db: Session = Depends(get_db)):
    """
    T5 requirement: Immediate account freezing request.
    """
    vpa = req.vpa.lower()
    # Simulate API call to NPCI/Bank
    logger.info(f"UPI FREEZE: Request sent to NPCI for {vpa}")
    
    # Update Stats
    stat = db.query(SystemStat).filter(SystemStat.category == "upi", SystemStat.key == "frozen_accounts").first()
    if stat:
        stat.value = str(int(stat.value) + 1)
    else:
        db.add(SystemStat(category="upi", key="frozen_accounts", value="1"))
    
    db.commit()
    
    return {
        "status": "FREEZE_INITIATED",
        "case_id": f"UPI-FRZ-{uuid.uuid4().hex[:6].upper()}",
        "vpa": vpa,
        "eta": "Immediate (Real-time)"
    }


@router.post("/scan-message", response_model=dict)
async def scan_whatsapp_message(req: MessageScanRequest, db: Session = Depends(get_db)):
    """
    Analyzes a pasted message for phishing patterns and extracts VPAs.
    """
    message_text = req.message
    
    # 1. Regex to extract UP VPAs
    # Looks for shapes like name@bank, phone@upi
    vpa_pattern = r'[a-zA-Z0-9.\-_]+@[a-zA-Z]+'
    found_vpas = list(set(re.findall(vpa_pattern, message_text)))
    
    # 2. Check reputation of extracted VPAs
    vpa_analysis = []
    has_blocked_vpa = False
    for v in found_vpas:
        vl = v.lower()
        is_blocked = vl in BLOCKLIST_VPAS
        if is_blocked:
            has_blocked_vpa = True
        vpa_analysis.append({
            "vpa": v,
            "status": "PHISHING" if is_blocked else "SAFE",
            "risk": "CRITICAL" if is_blocked else "LOW"
        })
        
    # 3. AI Contextual Analysis
    from core.ai import honeypot_ai, SARVAM_CHAT_URL
    import httpx
    
    analysis_prompt = (
        "You are a cybersecurity expert analyzing a suspected phishing message. "
        "Determine if the message is a scam. Respond ONLY with a valid JSON object in this exact format: "
        '{"verdict": "RISK" or "SAFE", "confidence": float between 0-100, "pattern_detected": "Short description of the scam pattern or normal message"}'
    )
    
    try:
        response = await honeypot_ai.client.post(
            SARVAM_CHAT_URL,
            headers={"api-subscription-key": honeypot_ai.api_key, "Content-Type": "application/json"},
            json={
                "model": "sarvam-m",
                "messages": [
                    {"role": "system", "content": analysis_prompt},
                    {"role": "user", "content": message_text}
                ],
                "temperature": 0.1,
                "max_tokens": 150
            }
        )
        data = response.json()
        ai_content = data["choices"][0]["message"]["content"]
        
        # safely parse JSON from the response text
        match = re.search(r'\{.*\}', ai_content, re.DOTALL)
        if match:
            ai_result = json.loads(match.group())
        else:
            ai_result = {"verdict": "RISK", "confidence": 85.0, "pattern_detected": "Suspicious formatting detected (AI Parse Error)"}
            
    except Exception as e:
        logger.error(f"Message Scan AI Error: {e}")
        # Fallback if SARVAM fails but we found a blocked VPA
        if has_blocked_vpa:
             ai_result = {"verdict": "RISK", "confidence": 99.9, "pattern_detected": "Known malicious UPI Collector address detected"}
        else:
            # Basic keyword heuristic fallback
            risk_words = ['lottery', 'prize', 'urgent', 'kyc', 'block', 'win']
            is_risk = any(w in message_text.lower() for w in risk_words)
            ai_result = {
                "verdict": "RISK" if is_risk else "SAFE",
                "confidence": 80.0 if is_risk else 90.0,
                "pattern_detected": "Heuristic Keyword Match" if is_risk else "Standard Communication"
            }
            
    # Force RISK if a known blocked VPA is present, overriding AI if it hallucinated SAFE
    if has_blocked_vpa:
        ai_result["verdict"] = "RISK"
        ai_result["confidence"] = max(ai_result.get("confidence", 0), 99.0)

    # Log action
    new_action = SystemAction(
        action_type="SCAN_MESSAGE",
        metadata_json={
            "verdict": ai_result.get("verdict"),
            "msg_length": len(message_text),
            "vpas_found": len(found_vpas)
        },
        status="success"
    )
    db.add(new_action)
    db.commit()

    return {
        "verdict": ai_result.get("verdict", "SAFE"),
        "confidence": ai_result.get("confidence", 0),
        "pattern_detected": ai_result.get("pattern_detected", ""),
        "extracted_vpas": vpa_analysis
    }
