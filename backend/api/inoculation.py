"""
Inoculation Module — Real SMS/WhatsApp simulation delivery.
Sends real inoculation messages to citizens via configured channels.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.config import settings
from core.services_hub import backend_service
import datetime
import logging

logger = logging.getLogger("sentinel.inoculation")

router = APIRouter()


class InoculationRequest(BaseModel):
    phone_number: str
    scenario: str
    channel: str = "SMS"  # SMS, WHATSAPP, PUSH


@router.post("/trigger", response_model=dict)
async def trigger_inoculation(req: InoculationRequest):
    """Send a real inoculation message to train citizens against scams."""
    scenarios = {
        "bank_kyc": {
            "title": "KYC Expiry Scam Training",
            "message": "[SENTINEL TRAINING] Dear Customer, your SBI account KYC has expired. Update now: bit.ly/sbi-kyc-verify — THIS IS A TEST. Real banks never send such links. Report 1930.",
        },
        "lottery_win": {
            "title": "Lottery Scam Training",
            "message": "[SENTINEL TRAINING] CONGRATS! You won KBC Lottery of ₹25 Lakhs. WhatsApp 90XXXXXX to claim. — THIS IS A TEST. No real lottery contacts you. Report 1930.",
        },
        "upi_refund": {
            "title": "UPI Refund Scam Training",
            "message": "[SENTINEL TRAINING] Your UPI refund of ₹4,999 is pending. Click to claim: bit.ly/upi-refund — THIS IS A TEST. UPI refunds are automatic. Report 1930.",
        },
        "job_offer": {
            "title": "Job Offer Scam Training",
            "message": "[SENTINEL TRAINING] Earn ₹5000/day from home! No investment needed. Join now: t.me/easywork — THIS IS A TEST. Real jobs don't recruit via unsolicited messages. Report 1930.",
        },
    }

    if req.scenario not in scenarios:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid scenario. Available: {list(scenarios.keys())}"
        )

    scenario_data = scenarios[req.scenario]

    # Dispatch via real notification service
    result = await backend_service.dispatch_notification(
        target=req.phone_number,
        message=scenario_data["message"],
        channel=req.channel,
    )

    logger.info(f"INOCULATION: Sent '{req.scenario}' to {req.phone_number} via {req.channel}")

    return {
        "status": result["status"],
        "msg_id": result["msg_id"],
        "scenario": req.scenario,
        "title": scenario_data["title"],
        "channel": req.channel,
        "target": req.phone_number,
        "timestamp": datetime.datetime.utcnow(),
    }


@router.get("/scenarios", response_model=dict)
def list_scenarios():
    """List all available inoculation scenarios."""
    return {
        "scenarios": [
            {"id": "bank_kyc", "title": "KYC Expiry Scam", "severity": "high"},
            {"id": "lottery_win", "title": "Lottery Win Scam", "severity": "medium"},
            {"id": "upi_refund", "title": "UPI Refund Scam", "severity": "high"},
            {"id": "job_offer", "title": "Job Offer Scam", "severity": "medium"},
        ]
    }
