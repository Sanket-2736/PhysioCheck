from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from database.models import User, Physician, Patient, RehabPlan, Session
from utils.email_utils import send_email


class AdminService:

    # ------------------------------------
    # WEBSITE STATS
    # ------------------------------------
    @staticmethod
    async def get_stats(db: AsyncSession):
        total_users = (await db.execute(select(User))).scalars().all()
        total_patients = (await db.execute(select(Patient))).scalars().all()
        physicians = (await db.execute(select(Physician))).scalars().all()
        verified_physicians = [p for p in physicians if p.is_verified]
        pending_physicians = [p for p in physicians if not p.is_verified]
        rehab_plans = (await db.execute(select(RehabPlan))).scalars().all()
        sessions = (await db.execute(select(Session))).scalars().all()

        return {
            "total_users": len(total_users),
            "total_patients": len(total_patients),
            "total_physicians": len(physicians),
            "verified_physicians": len(verified_physicians),
            "pending_physicians": len(pending_physicians),
            "total_rehab_plans": len(rehab_plans),
            "total_sessions": len(sessions)
        }

    # ------------------------------------
    # GET PENDING PHYSICIANS
    # ------------------------------------
    @staticmethod
    async def get_pending_physicians(db: AsyncSession):
        q = await db.execute(select(Physician).where(Physician.is_verified == False))
        physicians = q.scalars().all()

        return {
            "success": True,
            "pending_physicians": [
                {
                    "user_id": p.user_id,
                    "full_name": p.user.full_name,
                    "email": p.user.email,
                    "specialization": p.specialization,
                    "license_id": p.license_id,
                    "years_experience": p.years_experience,
                    "profile_photo": p.profile_photo,
                    "credential_photo": p.credential_photo,
                }
                for p in physicians
            ]
        }

    # ------------------------------------
    # APPROVE PHYSICIAN
    # ------------------------------------
    @staticmethod
    async def approve_physician(user_id: int, db: AsyncSession):

        q = await db.execute(select(Physician).where(Physician.user_id == user_id))
        physician = q.scalar_one_or_none()

        if not physician:
            raise HTTPException(404, "Physician not found")

        physician.is_verified = True
        await db.commit()

        # OPTIONAL EMAIL
        send_email(
            to=physician.user.email,
            subject="Your PhysioCheck Account is Approved",
            body="Congratulations! Your physician account has been verified by the admin."
        )

        return {"success": True, "message": "Physician approved"}

    # ------------------------------------
    # REJECT PHYSICIAN
    # ------------------------------------
    @staticmethod
    async def reject_physician(user_id: int, db: AsyncSession):
        q = await db.execute(select(Physician).where(Physician.user_id == user_id))
        physician = q.scalar_one_or_none()

        if not physician:
            raise HTTPException(404, "Physician not found")

        # Remove their account completely
        await db.delete(physician)
        await db.commit()

        return {"success": True, "message": "Physician rejected & removed"}
