from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class CallCreate(BaseModel):
    caller_num: str
    receiver_num: str
    duration: Optional[int] = 0
    call_type: str = "incoming"
    metadata: Optional[Dict] = {}

class DetectionResponse(BaseModel):
    call_id: int
    fraud_risk_score: float
    verdict: str
    timestamp: datetime

class SuspiciousNumberSchema(BaseModel):
    phone_number: str
    reputation_score: float
    category: str
    report_count: int

    class Config:
        from_attributes = True
