from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from routers.auth_router import require_role
from services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/patient")
async def patient_report(
    user=Depends(require_role("patient")),
    db: AsyncSession = Depends(get_db)
):
    report = await ReportService.patient_report(
        patient_id=user["user_id"],
        db=db
    )
    return {"success": True, "report": report}
