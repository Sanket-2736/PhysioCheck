from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

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
    payload: dict,
    user=Depends(require_role("patient")),
    db: AsyncSession = Depends(get_db)
):
    return await PatientSessionService.end_session(
        session_id=session_id,
        payload=payload,
        db=db
    )

@router.post("/start-session/{patient_exercise_id}")
async def start_exercise_session(
    patient_exercise_id: int,
    user=Depends(require_role("patient")),
    db: AsyncSession = Depends(get_db)
):
    return await PatientSessionService.start_session(
        patient_exercise_id=patient_exercise_id,
        patient_id=user["user_id"],
        db=db
    )


@router.get("/progress")
async def get_my_progress(
    user=Depends(require_role("patient")),
    db: AsyncSession = Depends(get_db)
):
    return await PatientProgressService.get_progress(
        patient_id=user["user_id"],
        db=db
    )
