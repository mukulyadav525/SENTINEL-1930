from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, Dict, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session
from core.database import get_db
from core.auth import get_current_user
from models.database import User, SystemAction
import logging
import traceback

logger = logging.getLogger("sentinel.actions")

router = APIRouter()

class ActionRequest(BaseModel):
    action_type: str
    target_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@router.post("/perform")
async def perform_action(
    req: ActionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log a system action to the database.
    """
    try:
        logger.info(f"User {current_user.username} (ID: {current_user.id}) performing action: {req.action_type}")
        
        # Generic to User-Friendly mapping
        messages = {
            "VIEW_MAP": "Sentinel Live Threat Map Initialized",
            "FILTER_RISK": f"Risk Filter Applied: {req.target_id or 'Updated'}",
            "BLOCK_NUMBER": f"Telecom Block Sequence Initiated for {req.target_id or 'target'}",
            "VPA_LOOKUP": f"VPA Reputation Analysis for {req.target_id or 'VPA'} Complete",
            "FREEZE_VPA": f"Financial Freeze Request Dispatched for {req.target_id or 'VPA'}",
            "SCAN_VIDEO": "Deepfake Forensic Pipeline Active",
            "GENERATE_FIR": "Digital FIR Packet Compiled & Signed",
            "DOWNLOAD_PLAYBOOK": f"Onboarding Playbook {req.target_id or ''} Downloaded",
            "RESTORE_ACCOUNT": "Account Restoration Workflow Initialized",
            "USE_LE_TOOL": f"Law Enforcement Tool {req.target_id or ''} Authorized",
            "RESET_SCAN": "Forensic Buffer Cleared",
            "VIEW_HISTORY": "Accessing Historical Incident Logs",
            "VIEW_INCIDENT": f"Incident Data Loaded for {req.target_id or 'incident'}",
            "SCAN_QR": "QR Forensic Signature Verified",
            "INTERCEPT_MSG": "WhatsApp Interceptor Payload Active",
            "GENERATE_RECOVERY_BUNDLE": "Legal Restitution Bundle Generated",
            "SUPPORT_TOOL": f"Redirecting to {req.target_id or 'Support Resource'}",
            "OPTIMIZE_STRATEGIES": "AI Strategy Optimization Complete",
            "LAUNCH_PROBE": "Sentinel Agentic Probe Dispatched",
            "VIEW_MAP": "Sentinel Live Threat Map Initialized",
        }

        user_msg = messages.get(req.action_type.upper(), f"Action {req.action_type} executed successfully")

        new_action = SystemAction(
            user_id=current_user.id,
            action_type=req.action_type.upper(),
            target_id=req.target_id,
            metadata_json=req.metadata,
            status="success"
        )
        
        db.add(new_action)
        db.commit()
        db.refresh(new_action)
        
        return {
            "status": "success",
            "message": user_msg,
            "action_id": new_action.id
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Action failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500, 
            detail=f"Backend Sync Error: {str(e)}"
        )

@router.get("/download-sim")
async def download_simulation(
    file_type: str = "pdf",
    category: str = "report",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Simulates a file download by returning mock data or instructions.
    """
    try:
        logger.info(f"User {current_user.username} downloading {category} as {file_type}")
        
        # Simply log the export action
        new_action = SystemAction(
            user_id=current_user.id,
            action_type="EXPORT",
            target_id=f"{category}.{file_type}",
            metadata_json={"category": category, "file_type": file_type}
        )
        db.add(new_action)
        db.commit()
        
        return {
            "status": "success",
            "download_url": f"https://sentinel-mock-storage.gov.in/simulated/{category}.{file_type}",
            "filename": f"SENTINEL_{category.upper().replace('.', '_')}_{current_user.username}.{file_type.lower()}",
            "message": "This is a simulated download link. In production, this would trigger a secure file stream."
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Download failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Report Generation Error: {str(e)}")
