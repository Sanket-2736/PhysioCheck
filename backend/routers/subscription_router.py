from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.subscription_schema import SubscribeRequest
from services.subscription_service import SubscriptionService
from routers.auth_router import require_role
from database.connection import get_db

router = APIRouter(prefix="/subscription", tags=["Subscription"])


@router.post("/subscribe")
async def subscribe(
    body: SubscribeRequest,
    user=Depends(require_role("patient")),
    db: AsyncSession = Depends(get_db)
):
    return await SubscriptionService.subscribe_patient(
        patient_user_id=user["user_id"],
        physician_id=body.physician_id,
        db=db
    )
