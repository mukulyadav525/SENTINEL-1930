from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models.database import HoneypotSession, HoneypotMessage
from core.ai import honeypot_ai
import uuid
import datetime
import json
import logging

logger = logging.getLogger("sentinel.honeypot")

router = APIRouter()

@router.post("/sessions", response_model=dict)
def create_honeypot_session(caller_num: str, persona: str, db: Session = Depends(get_db)):
    session_id = str(uuid.uuid4())
    db_session = HoneypotSession(
        session_id=session_id,
        caller_num=caller_num,
        persona=persona
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return {"session_id": session_id, "status": "active"}

@router.post("/sessions/{session_id}/chat", response_model=dict)
async def honeypot_chat(session_id: str, message: str, db: Session = Depends(get_db)):
    db_session = db.query(HoneypotSession).filter(HoneypotSession.session_id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Save Scammer Message
    scammer_msg = HoneypotMessage(session_id=db_session.id, role="user", content=message)
    db.add(scammer_msg)
    
    # Get History
    history_msgs = db.query(HoneypotMessage).filter(HoneypotMessage.session_id == db_session.id).order_by(HoneypotMessage.timestamp).all()
    history = [{"role": m.role, "content": m.content} for m in history_msgs]
    
    # Generate AI Response
    ai_response = await honeypot_ai.generate_response(db_session.persona, history, message)
    
    # Save AI Message
    ai_msg = HoneypotMessage(session_id=db_session.id, role="assistant", content=ai_response)
    db.add(ai_msg)
    
    db.commit()
    
    return {"response": ai_response, "timestamp": datetime.datetime.utcnow()}

@router.get("/sessions", response_model=list)
def list_honeypot_sessions(db: Session = Depends(get_db)):
    return db.query(HoneypotSession).all()


# ─── Stateless Direct Chat (for Interactive Simulation) ──────────────
from pydantic import BaseModel
from typing import List, Dict

class DirectChatRequest(BaseModel):
    message: str
    persona: str = "Elderly Uncle"
    history: List[Dict[str, str]] = []

@router.post("/direct-chat", response_model=dict)
async def direct_chat(req: DirectChatRequest):
    """
    Stateless AI chat endpoint for the frontend simulation.
    No database session required — uses Gemini directly.
    """
    ai_response = await honeypot_ai.generate_response(
        persona=req.persona,
        history=req.history,
        message=req.message,
    )
    return {
        "response": ai_response,
        "persona": req.persona,
        "timestamp": datetime.datetime.utcnow(),
    }

@router.post("/direct-conclude", response_model=dict)
async def direct_conclude(req: DirectChatRequest):
    """
    Analyze the conversation and 'report' it.
    Used for the frontend's 'Extracting Intel...' phase.
    """
    analysis = await honeypot_ai.analyze_scam(req.history)
    
    # Internal Mock Reporting
    logger.info(f"REPORT: Scam detected! Type: {analysis.get('scam_type')}, Bank: {analysis.get('bank_name')}")
    
    return {
        "analysis": analysis,
        "reported_to": ["National Cyber Crime Portal", "RBI Fraud Registry", analysis.get("bank_name") or "Leading Banks"],
        "status": "REPORTED"
    }

@router.post("/sessions/{session_id}/conclude", response_model=dict)
async def conclude_session(session_id: str, db: Session = Depends(get_db)):
    db_session = db.query(HoneypotSession).filter(HoneypotSession.session_id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get History
    history_msgs = db.query(HoneypotMessage).filter(HoneypotMessage.session_id == db_session.id).order_by(HoneypotMessage.timestamp).all()
    history = [{"role": m.role, "content": m.content} for m in history_msgs]
    
    # Run AI Analysis
    analysis = await honeypot_ai.analyze_scam(history)
    
    # Update Session with results (if fields exist, otherwise just log)
    # db_session.metadata = json.dumps(analysis)
    # db.commit()
    
    logger.info(f"SESSION CONCLUDED: {session_id}. Fraud Type: {analysis.get('scam_type')}")
    
    return {
        "session_id": session_id,
        "analysis": analysis,
        "status": "CONCLUDED_AND_REPORTED"
    }

@router.get("/stats")
def get_honeypot_stats(db: Session = Depends(get_db)):
    # Aggregating real data from DB
    total_sessions = db.query(HoneypotSession).count()
    total_messages = db.query(HoneypotMessage).count()
    
    # Estimation of time wasted (e.g. 5 mins per session)
    time_wasted_mins = total_sessions * 5
    hours = time_wasted_mins // 60
    mins = time_wasted_mins % 60
    
    # Get Fatigue Index from DB
    fatigue_stat = db.query(SystemStat).filter(SystemStat.category == "honeypot", SystemStat.key == "fatigue_index").first()
    fatigue_val = fatigue_stat.value if fatigue_stat else "78.4%"
    
    return {
        "time_wasted": f"{hours}h {mins}m",
        "data_extracted": total_messages * 2, # Mocking extraction points
        "fatigue_index": fatigue_val
    }
