from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

from database.models import SubscriptionRequest, Patient


class SubscriptionRequestService:

    # -----------------------------------------
    # PATIENT → CREATE REQUEST
    # -----------------------------------------
    @staticmethod
    async def create_request(patient_id: int, physician_id: int, db: AsyncSession):
        # Prevent duplicate pending request
        q = await db.execute(
            select(SubscriptionRequest).where(
                SubscriptionRequest.patient_id == patient_id,
                SubscriptionRequest.physician_id == physician_id,
                SubscriptionRequest.status == "PENDING"
            )
        )
        if q.scalar_one_or_none():
            raise HTTPException(400, "Request already pending")

        req = SubscriptionRequest(
            patient_id=patient_id,
            physician_id=physician_id
        )
        db.add(req)
        await db.commit()

        return {
            "success": True,
            "message": "Subscription request sent"
        }

    # -----------------------------------------
    # PHYSICIAN → VIEW PENDING REQUESTS
    # -----------------------------------------
    @staticmethod
    async def get_pending_requests(physician_id: int, db: AsyncSession):
        q = await db.execute(
            select(SubscriptionRequest)
            .where(
                SubscriptionRequest.physician_id == physician_id,
                SubscriptionRequest.status == "PENDING"
            )
        )
        requests = q.scalars().all()

        return {
            "success": True,
            "requests": [
                {
                    "request_id": r.id,
                    "patient_id": r.patient_id,
                    "created_at": r.created_at
                }
                for r in requests
            ]
        }

    # -----------------------------------------
    # PHYSICIAN → ACCEPT REQUEST
    # -----------------------------------------
    @staticmethod
    async def accept_request(request_id: int, physician_id: int, db: AsyncSession):
        q = await db.execute(
            select(SubscriptionRequest).where(
                SubscriptionRequest.id == request_id,
                SubscriptionRequest.physician_id == physician_id,
                SubscriptionRequest.status == "PENDING"
            )
        )
        req = q.scalar_one_or_none()

        if not req:
            raise HTTPException(404, "Request not found")

        # Assign patient to physician
        pq = await db.execute(
            select(Patient).where(Patient.user_id == req.patient_id)
        )
        patient = pq.scalar_one_or_none()

        if not patient:
            raise HTTPException(404, "Patient not found")

        patient.physician_id = physician_id
        req.status = "ACCEPTED"

        await db.commit()

        return {
            "success": True,
            "message": "Request accepted"
        }

    # -----------------------------------------
    # PHYSICIAN → REJECT REQUEST
    # -----------------------------------------
    @staticmethod
    async def reject_request(request_id: int, physician_id: int, db: AsyncSession):
        q = await db.execute(
            select(SubscriptionRequest).where(
                SubscriptionRequest.id == request_id,
                SubscriptionRequest.physician_id == physician_id,
                SubscriptionRequest.status == "PENDING"
            )
        )
        req = q.scalar_one_or_none()

        if not req:
            raise HTTPException(404, "Request not found")

        req.status = "REJECTED"
        await db.commit()

        return {
            "success": True,
            "message": "Request rejected"
        }
