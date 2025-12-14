from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.connection import get_db
from routers.auth_router import require_role
from database.models import Patient

router = APIRouter(prefix="/physician", tags=["Physician"])


@router.get("/patients")
async def get_my_patients(
    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db)
):
    q = await db.execute(
        select(Patient).where(Patient.physician_id == user["user_id"])
    )
    patients = q.scalars().all()

    return {
        "success": True,
        "patients": [
            {
                "patient_id": p.user_id
            }
            for p in patients
        ]
    }
