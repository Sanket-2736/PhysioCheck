from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

from database.models import Patient, Physician


class SubscriptionService:

    @staticmethod
    async def subscribe_patient(
        patient_user_id: int,
        physician_id: int,
        db: AsyncSession
    ):
        # Check physician exists
        q = await db.execute(
            select(Physician).where(Physician.user_id == physician_id)
        )
        physician = q.scalar_one_or_none()

        if not physician:
            raise HTTPException(404, "Physician not found")

        # Fetch patient
        q = await db.execute(
            select(Patient).where(Patient.user_id == patient_user_id)
        )
        patient = q.scalar_one_or_none()

        if not patient:
            raise HTTPException(404, "Patient not found")

        # Assign physician
        patient.physician_id = physician_id
        await db.commit()

        return {"success": True, "message": "Subscribed successfully"}
