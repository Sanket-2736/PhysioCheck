from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.connection import get_db
from database.models import AuditLog, User, Physician, Patient, RehabPlan, Session
from routers.auth_router import require_admin, require_role
from services.admin_service import AdminService
from services.audit_service import AuditService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
async def get_admin_stats(user=Depends(require_admin), db: AsyncSession = Depends(get_db)):
    return await AdminService.get_stats(db)

@router.get("/audit-logs")
async def get_audit_logs(
    user=Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    q = await db.execute(
        select(AuditLog).order_by(AuditLog.created_at.desc())
    )
    logs = q.scalars().all()

    return {
        "success": True,
        "logs": [
            {
                "id": l.id,
                "admin_id": l.admin_id,
                "action": l.action,
                "target_type": l.target_type,
                "target_id": l.target_id,
                "description": l.description,
                "created_at": l.created_at,
            }
            for l in logs
        ]
    }


@router.get("/physicians")
async def get_all_physicians(
    user=Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    q = await db.execute(
        select(Physician)
        .options(selectinload(Physician.user))
    )
    physicians = q.scalars().all()

    data = []
    for p in physicians:
        # Count patients
        pq = await db.execute(
            select(Patient).where(Patient.physician_id == p.user_id)
        )
        patients = pq.scalars().all()

        data.append({
            "user_id": p.user_id,
            "full_name": p.user.full_name,
            "email": p.user.email,
            "specialization": p.specialization,
            "is_verified": p.is_verified,
            "patient_count": len(patients),
        })

    return {
        "success": True,
        "physicians": data
    }

@router.get("/physicians/{user_id}")
async def get_physician_profile(
    user_id: int,
    user=Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    q = await db.execute(
        select(Physician)
        .options(selectinload(Physician.user))
        .where(Physician.user_id == user_id)
    )
    physician = q.scalar_one_or_none()

    if not physician:
        raise HTTPException(404, "Physician not found")

    return {
        "success": True,
        "physician": {
            "user_id": physician.user_id,
            "full_name": physician.user.full_name,
            "email": physician.user.email,
            "specialization": physician.specialization,
            "license_id": physician.license_id,
            "years_experience": physician.years_experience,
            "is_verified": physician.is_verified,
            "profile_photo": physician.profile_photo,
            "credential_photo": physician.credential_photo,
            "created_at": physician.user.created_at
        }
    }

@router.get("/physicians/{user_id}/patients")
async def get_physician_patients_admin(
    user_id: int,
    user=Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    q = await db.execute(
        select(Patient)
        .options(selectinload(Patient.user))
        .where(Patient.physician_id == user_id)
    )
    patients = q.scalars().all()

    return {
        "success": True,
        "patients": [
            {
                "patient_id": p.id,
                "user_id": p.user_id,
                "full_name": p.user.full_name,
                "email": p.user.email,
                "age": p.age,
                "gender": p.gender,
                "injury_description": p.injury_description,
                "goals": p.goals
            }
            for p in patients
        ]
    }


@router.get("/physicians/pending")
async def get_pending_physicians(user=Depends(require_admin), db: AsyncSession = Depends(get_db)):
    return await AdminService.get_pending_physicians(db)

@router.post("/physicians/{user_id}/approve")
async def approve_physician(user_id: int, user=Depends(require_admin), db: AsyncSession = Depends(get_db)):
    from services.audit_service import AuditService

    await AuditService.log(
        db=db,
        admin_id=user["user_id"],
        action="APPROVE_PHYSICIAN",
        target_type="physician",
        target_id=user_id,
        description="Physician approved by admin"
    )

    return await AdminService.approve_physician(user_id, db)

@router.post("/physicians/{user_id}/reject")
async def reject_physician(user_id: int, user=Depends(require_admin), db: AsyncSession = Depends(get_db)):
    from services.audit_service import AuditService

    await AuditService.log(
        db=db,
        admin_id=user["user_id"],
        action="REJECT_PHYSICIAN",
        target_type="physician",
        target_id=user_id,
        description="Physician approved by admin"
    )
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

@router.patch("/users/{user_id}/disable")
async def disable_user(
    user_id: int,
    user=Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    user_obj = await db.get(User, user_id)
    if not user_obj:
        raise HTTPException(404, "User not found")

    user_obj.is_active = False
    await db.commit()

    await AuditService.log(
        db, user["user_id"],
        "DISABLE_USER", "user", user_id,
        "User account disabled"
    )

    return {"success": True}

@router.patch("/users/{user_id}/enable")
async def enable_user(
    user_id: int,
    user=Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    user_obj = await db.get(User, user_id)
    if not user_obj:
        raise HTTPException(404, "User not found")

    user_obj.is_active = True
    await db.commit()

    await AuditService.log(
        db, user["user_id"],
        "ENABLE_USER", "user", user_id,
        "User account enabled"
    )

    return {"success": True}

@router.get("/users")
async def get_all_patients(
    user=Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    q = await db.execute(
        select(Patient)
        .options(selectinload(Patient.user))
    )
    patients = q.scalars().all()

    return {
        "success": True,
        "patients": [
            {
                "user_id": p.user_id,
                "full_name": p.user.full_name,
                "email": p.user.email,
                "age": p.age,
                "gender": p.gender,
                "is_active": p.is_active,
                "physician_id": p.physician_id,
            }
            for p in patients
        ]
    }
