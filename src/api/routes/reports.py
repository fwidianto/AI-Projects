"""Reports API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO

from src.config.database import get_db
from src.services.report_service import ReportService

router = APIRouter()


@router.get("/daily-digest")
async def get_daily_digest(
    profile_id: int,
    days_back: int = Query(1, ge=1, le=7),
    db: Session = Depends(get_db),
):
    """Get daily job digest."""
    service = ReportService(db)
    return service.generate_daily_digest(profile_id, days_back)


@router.get("/weekly")
async def get_weekly_report(
    profile_id: int,
    db: Session = Depends(get_db),
):
    """Get weekly job report."""
    service = ReportService(db)
    return service.generate_weekly_report(profile_id)


@router.get("/dashboard-stats")
async def get_dashboard_stats(
    profile_id: int,
    db: Session = Depends(get_db),
):
    """Get dashboard statistics."""
    service = ReportService(db)
    return service.get_dashboard_stats(profile_id)


@router.get("/pdf")
async def get_pdf_report(
    profile_id: int,
    report_type: str = Query("weekly", regex="^(daily|weekly)$"),
    db: Session = Depends(get_db),
):
    """Generate PDF report."""
    service = ReportService(db)
    
    try:
        pdf_buffer = service.generate_pdf_report(profile_id, report_type)
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=job_report_{report_type}.pdf"
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/csv")
async def get_csv_export(
    profile_id: int,
    min_score: float = Query(0, ge=0, le=100),
    db: Session = Depends(get_db),
):
    """Generate CSV export of jobs."""
    service = ReportService(db)
    csv_content = service.generate_csv_export(profile_id, min_score)
    
    return StreamingResponse(
        BytesIO(csv_content.encode()),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=jobs_export.csv"
        },
    )