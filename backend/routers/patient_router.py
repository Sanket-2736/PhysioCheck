from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from services.report_service import ReportService
from services.live_feedback_service import LiveFeedbackService
from services.patient_progress_service import PatientProgressService
from database.connection import get_db
from routers.auth_router import require_role
from services.patient_session_service import PatientSessionService

router = APIRouter(prefix="/patient", tags=["Patient"])

from sqlalchemy.future import select
from database.models import PatientExercise


@router.post("/session/{session_id}/frame")
async def live_feedback(
    session_id: int,
    payload: dict,
    user=Depends(require_role("patient")),
    db: AsyncSession = Depends(get_db)
):
    return await LiveFeedbackService.evaluate_frame(
        session_id=session_id,
        frame=payload["frame"],
        db=db
    )


@router.post("/end-session/{session_id}")
async def end_session(
    session_id: int,
    payload: dict | None = None,
    user=Depends(require_role("patient")),
    db: AsyncSession = Depends(get_db)
):
    # 🔥 always use live state from LiveFeedbackService as source of truth
    payload = payload or {}
    state = payload.get("state", {})

    live_entry = LiveFeedbackService.SESSION_STORE.get(session_id)
    if live_entry:
        live_state = live_entry["state"]
        # copy the live repCount and startTime into the payload state
        state["repCount"] = live_state.get("repCount", 0)
        state["startTime"] = live_state.get("startTime", state.get("startTime"))
        state.setdefault("jointStats", live_state.get("jointStats", {}))
        state.setdefault("errorSummary", live_state.get("errorSummary", {}))

    payload["state"] = state

    return await PatientSessionService.end_session(
        session_id=session_id,
        payload=payload,
        db=db
    )


from services.analytics_service import AnalyticsService


@router.get("/analytics/errors")
async def error_frequency(
    user=Depends(require_role("patient")),
    db: AsyncSession = Depends(get_db)
):
    return {
        "success": True,
        "errorFrequency": await AnalyticsService.get_error_frequency(
            patient_id=user["user_id"],
            db=db
        )
    }


@router.get("/analytics/common-mistakes")
async def common_mistakes(
    user=Depends(require_role("patient")),
    db: AsyncSession = Depends(get_db)
):
    return {
        "success": True,
        "mistakes": await AnalyticsService.get_common_mistakes(
            patient_id=user["user_id"],
            db=db
        )
    }


@router.get("/analytics/risks")
async def risk_alerts(
    user=Depends(require_role("patient")),
    db: AsyncSession = Depends(get_db)
):
    return {
        "success": True,
        "riskAlerts": await AnalyticsService.get_risk_summary(
            patient_id=user["user_id"],
            db=db
        )
    }


@router.get("/progress")
async def get_my_progress(
    user=Depends(require_role("patient")),
    db: AsyncSession = Depends(get_db)
):
    return {
        "daily": await PatientProgressService.get_daily_progress(user["user_id"], db),
        "weekly": await PatientProgressService.get_weekly_progress(user["user_id"], db)
    }


@router.get("/report")
async def get_patient_report(
    user=Depends(require_role("patient")),
    db: AsyncSession = Depends(get_db)
):
    return {
        "success": True,
        "report": await ReportService.patient_report(
            patient_id=user["user_id"],
            db=db
        )
    }
