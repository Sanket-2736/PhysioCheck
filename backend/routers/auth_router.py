# routers/auth_router.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
import jwt

from database.connection import get_db
from schemas.auth_schemas import (
    PhysicianSignupRequest,
    SignupRequest,
    LoginRequest,
    AuthResponse,
    PhysicianSignupResponse 
)
from services.auth_service import AuthService
from utils.security import SECRET_KEY, ALGORITHM
from utils.cloudinary import upload_profile_photo

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def require_role(required_role: str):
    def role_checker(user=Depends(get_current_user)):
        if user.get("role") != required_role:
            raise HTTPException(status_code=403, detail="Access forbidden")
        return user
    return role_checker


# ----------------------
# AUTH APIs
# ----------------------
@router.post("/register")
async def register_patient(
    profile_photo: UploadFile = File(None),
    body: SignupRequest = Depends(SignupRequest.as_form),
    db: AsyncSession = Depends(get_db)
):

    url = None
    if profile_photo:
        url = upload_profile_photo(profile_photo.file)

    return await AuthService.register_patient(body.dict(), db, profile_photo_url=url)

@router.post("/login-admin")
async def login_admin(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService.login_admin(data.dict(), db)

def require_admin(user=Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(403, "Admin access only")
    return user

@router.get("/physician/status")
async def physician_status(user=Depends(require_role("physician")), db: AsyncSession = Depends(get_db)):
    return await AuthService.get_physician_status(user["user_id"], db)

@router.post("/register-physician", response_model=PhysicianSignupResponse)
async def register_physician(
    profile_photo: UploadFile = File(None),
    credential_photo: UploadFile = File(None),
    body: PhysicianSignupRequest = Depends(PhysicianSignupRequest.as_form),
    db: AsyncSession = Depends(get_db)
):
    profile_url = None
    credential_url = None

    if profile_photo:
        profile_url = upload_profile_photo(profile_photo.file)

    if credential_photo:
        credential_url = upload_profile_photo(credential_photo.file)

    payload = body.dict()
    payload["profile_photo"] = profile_url
    payload["credential_photo"] = credential_url

    return await AuthService.register_physician(payload, db)


@router.post("/login", response_model=AuthResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService.login(body.dict(), db)


@router.get("/me")
async def me(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await AuthService.me(user["user_id"], db)


@router.get("/physician/status")
async def physician_status(email: str, db: AsyncSession = Depends(get_db)):
    return await AuthService.get_physician_status(email, db)

