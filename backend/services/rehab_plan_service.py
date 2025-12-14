from sqlalchemy.ext.asyncio import AsyncSession
from database.models import RehabPlan

class RehabPlanService:

    @staticmethod
    async def create_plan(payload, physician_id: int, db: AsyncSession):
        plan = RehabPlan(
            patient_id=payload.patient_id,
            physician_id=physician_id,
            notes=payload.notes
        )
        db.add(plan)
        await db.commit()
        await db.refresh(plan)

        return plan
