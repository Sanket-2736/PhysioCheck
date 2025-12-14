from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.connection import get_db
from database.models import User, Physician, Patient, RehabPlan, Session
from routers.auth_router import require_admin, require_role
from services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"])


# -----------------------------
#  ADMIN DASHBOARD STATS
# -----------------------------
@router.get("/stats")
async def get_admin_stats(user=Depends(require_admin), db: AsyncSession = Depends(get_db)):
    return await AdminService.get_stats(db)


# -----------------------------
#  PENDING PHYSICIANS
# -----------------------------
@router.get("/physicians/pending")
async def get_pending_physicians(user=Depends(require_admin), db: AsyncSession = Depends(get_db)):
    return await AdminService.get_pending_physicians(db)


# -----------------------------
# APPROVE PHYSICIAN
# -----------------------------
@router.post("/physicians/{user_id}/approve")
async def approve_physician(user_id: int, user=Depends(require_admin), db: AsyncSession = Depends(get_db)):
    return await AdminService.approve_physician(user_id, db)


# -----------------------------
# REJECT PHYSICIAN
# -----------------------------
@router.post("/physicians/{user_id}/reject")
async def reject_physician(user_id: int, user=Depends(require_admin), db: AsyncSession = Depends(get_db)):
    return await AdminService.reject_physician(user_id, db)

@router.get("/physician/patients")
async def my_patients(
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
                "user_id": p.user_id,
                "patient_id": p.id
            } for p in patients
        ]
    }
