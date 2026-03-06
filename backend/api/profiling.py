from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from models.database import ScamCluster
from typing import List

router = APIRouter()

@router.get("/clusters")
def get_scam_clusters(db: Session = Depends(get_db)):
    clusters = db.query(ScamCluster).all()
    return [
        {
            "id": c.cluster_id,
            "risk": c.risk_level,
            "location": c.location,
            "linkedVPAs": c.linked_vpas,
            "calls": c.honeypot_hits
        }
        for c in clusters
    ]
