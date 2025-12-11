# routers/sessions_router.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from services.sessions_service import SessionService
from database.connection import get_db
from routers.auth_router import get_current_user

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("/start")
async def start_session(body: dict,
                        db: AsyncSession = Depends(get_db),
                        user=Depends(get_current_user)):
    return {
        "sessionId": await SessionService.start_session(
            exercise_id=body["exercise_id"],
            patient_id=user["user_id"],
            target_reps=body.get("target_reps", 5),
            max_duration=body.get("max_duration", 30),
            db=db
        )
    }


@router.get("/{session_id}/status")
async def get_status(session_id: str, db: AsyncSession = Depends(get_db)):
    return await SessionService.get_session_status(session_id, db)


@router.get("/{session_id}/summary")
async def get_summary(session_id: str, db: AsyncSession = Depends(get_db)):
    return await SessionService.get_session_summary(session_id, db)
