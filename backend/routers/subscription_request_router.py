from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from routers.auth_router import require_role
from services.subscription_request_service import SubscriptionRequestService

router = APIRouter(prefix="/subscription", tags=["Subscription Requests"])


# ------------------------------------------------
# PATIENT → SEND SUBSCRIPTION REQUEST
# ------------------------------------------------
@router.post("/request/{physician_id}")
async def create_request(
    physician_id: int,
    user=Depends(require_role("patient")),
    db: AsyncSession = Depends(get_db)
):
    return await SubscriptionRequestService.create_request(
        patient_id=user["user_id"],
        physician_id=physician_id,
        db=db
    )


# ------------------------------------------------
# PHYSICIAN → VIEW PENDING REQUESTS
# ------------------------------------------------
@router.get("/physician/requests")
async def get_requests(
    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db)
):
    return await SubscriptionRequestService.get_pending_requests(
        physician_id=user["user_id"],
        db=db
    )


# ------------------------------------------------
# PHYSICIAN → ACCEPT REQUEST
# ------------------------------------------------
@router.post("/physician/requests/{request_id}/accept")
async def accept_request(
    request_id: int,
    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db)
):
    return await SubscriptionRequestService.accept_request(
        request_id=request_id,
        physician_id=user["user_id"],
        db=db
    )


# ------------------------------------------------
# PHYSICIAN → REJECT REQUEST
# ------------------------------------------------
@router.post("/physician/requests/{request_id}/reject")
async def reject_request(
    request_id: int,
    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db)
):
    return await SubscriptionRequestService.reject_request(
        request_id=request_id,
        physician_id=user["user_id"],
        db=db
    )
