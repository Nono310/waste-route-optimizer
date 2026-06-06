from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

router = APIRouter()
from app.utils.store import community_reports

class ReportRequest(BaseModel):
    bin_id: str
    reporter: str
    message: str
    phone: Optional[str] = "N/A"
    fill_level: Optional[float] = 100.0

@router.get("/predict")
def predict(hour: Optional[int] = None, day: Optional[int] = None):
    try:
        from app.services.predictor import predict_waste_levels
        results = predict_waste_levels(hour=hour, day_of_week=day)
        needs_collection = [r for r in results if r["needs_collection"]]
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "total_bins": len(results),
            "bins_need_collection": len(needs_collection),
            "predictions": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/optimize")
def optimize(hour: Optional[int] = None, day: Optional[int] = None):
    try:
        from app.services.predictor import predict_waste_levels
        from app.services.optimizer import run_genetic_algorithm
        predictions = predict_waste_levels(hour=hour, day_of_week=day)
        bins_to_collect = [p for p in predictions if p["needs_collection"]]
        if not bins_to_collect:
            return {
                "status": "success",
                "message": "No bins need collection right now",
                "routes": []
            }
        routes, total_dist = run_genetic_algorithm(bins_to_collect)
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "bins_to_collect": len(bins_to_collect),
            "trucks_used": len(routes),
            "total_distance_km": total_dist,
            "routes": routes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/report")
def report(req: ReportRequest):
    report_entry = {
        "report_id": f"RPT{len(community_reports)+1:04d}",
        "bin_id": req.bin_id,
        "reporter": req.reporter,
        "phone": req.phone,
        "message": req.message,
        "fill_level": req.fill_level,
        "timestamp": datetime.now().isoformat(),
        "status": "received"
    }
    community_reports.append(report_entry)
    try:
        from app.db.database import SessionLocal
        from app.db.models import CommunityReport as CommunityReportModel
        db = SessionLocal()
        db_report = CommunityReportModel(
            report_id=report_entry["report_id"],
            bin_id=req.bin_id,
            reporter=req.reporter,
            phone=req.phone,
            message=req.message,
            fill_level=req.fill_level,
            status="received"
        )
        db.add(db_report)
        db.commit()
        db.close()
    except Exception as e:
        print(f"DB save error: {e}")
    reports_df = pd.DataFrame(community_reports)
    reports_df.to_csv(os.path.join(BASE_DIR, "data/processed/community_reports.csv"), index=False)
    return {
        "status": "success",
        "message": f"Report received for {req.bin_id}. Thank you {req.reporter}!",
        "report_id": report_entry["report_id"]
    }

@router.get("/reports")
def get_reports():
    return {
        "status": "success",
        "total": len(community_reports),
        "reports": community_reports
    }

@router.get("/bins")
def get_bins():
    try:
        bins_df = pd.read_csv(os.path.join(BASE_DIR, "data/raw/bins.csv"))
        return {
            "status": "success",
            "total": len(bins_df),
            "bins": bins_df.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
