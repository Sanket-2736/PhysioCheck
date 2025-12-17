# services/auth_service.py

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from typing import Dict, Any

from database.models import User, Patient, Physician, Role
from utils.security import hash_password, verify_password, create_access_token


class AuthService:

    # -------------------------------------------------------
    # REGISTER PATIENT
    # -------------------------------------------------------
    @staticmethod
    async def register_patient(payload: Dict[str, Any], db: AsyncSession, profile_photo_url: str | None = None) -> Dict[str, Any]:

        # Check if email already exists
        q = await db.execute(select(User).where(User.email == payload["email"]))
        if q.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")

        # Fetch patient role
        role_q = await db.execute(select(Role).where(Role.name == "patient"))
        role = role_q.scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=500, detail="Patient role not found")

        # Create User
        user = User(
            email=payload["email"],
            full_name=payload.get("full_name"),
            password_hash=hash_password(payload["password"]),
            role_id=role.id
        )
        db.add(user)
        await db.flush()

        # Create Patient
        patient = Patient(
            user_id=user.id,
            age=payload.get("age"),
            gender=payload.get("gender"),
            height_cm=payload.get("height_cm"),
            weight_kg=payload.get("weight_kg"),
            address=payload.get("address"),
            injury_description=payload.get("injury_description"),
            goals=payload.get("goals"),
            profile_photo=profile_photo_url
        )
        db.add(patient)
        await db.commit()

        token = create_access_token({"user_id": user.id, "role": "patient"})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user.id,
            "role": "patient"
        }

    # -------------------------------------------------------
    # REGISTER PHYSICIAN
    # -------------------------------------------------------
    @staticmethod
    async def register_physician(payload: Dict[str, Any], db: AsyncSession, profile_photo_url: str | None = None) -> Dict[str, Any]:

        # Check email
        q = await db.execute(select(User).where(User.email == payload["email"]))
        if q.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")

        # Role
        role_q = await db.execute(select(Role).where(Role.name == "physician"))
        role = role_q.scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=500, detail="Physician role not found")

        # Create User
        user = User(
            email=payload["email"],
            full_name=payload.get("full_name"),
            password_hash=hash_password(payload["password"]),
            role_id=role.id
        )
        db.add(user)
        await db.flush()

        # Create Physician profile
        physician = Physician(
            user_id=user.id,
            specialization=payload.get("specialization"),
            license_id=payload.get("license_id"),
            years_experience=payload.get("years_experience"),
            profile_photo=payload.get("profile_photo"),
            credential_photo=payload.get("credential_photo"),
        )

        db.add(physician)
        await db.commit()

        token = create_access_token({"user_id": user.id, "role": "physician"})
        return {
            "success": True,
            "message": "Physician registered. Pending admin approval.",
            "user_id": user.id,
            "role": "physician",
            "is_verified": False
        }
    
    @staticmethod
    async def get_physician_status(user_id: int, db: AsyncSession):
        q = await db.execute(select(Physician).where(Physician.user_id == user_id))
        physician = q.scalar_one_or_none()

        if not physician:
            raise HTTPException(404, "Physician profile not found")

        return {
            "success": True,
            "user_id": user_id,
            "is_verified": physician.is_verified,
            "profile_photo": physician.profile_photo,
            "credential_photo": physician.credential_photo,
            "specialization": physician.specialization,
            "license_id": physician.license_id,
            "years_experience": physician.years_experience,
            "message": "Approved" if physician.is_verified else "Pending admin approval"
        }

    @staticmethod
    async def get_physician_status(email: str, db: AsyncSession):

        # Find the user
        q = await db.execute(select(User).where(User.email == email))
        user = q.scalar_one_or_none()

        if not user:
            return {"status": "not_found", "message": "Email not registered"}

        # Check if this user is a physician
        q2 = await db.execute(select(Physician).where(Physician.user_id == user.id))
        physician = q2.scalar_one_or_none()

        if not physician:
            return {"status": "not_physician", "message": "This email belongs to a non-physician user"}

        # Return status
        if physician.is_verified:
            return {
                "status": "approved",
                "message": "Your account is approved",
                "user_id": user.id
            }
        else:
            return {
                "status": "pending",
                "message": "Your verification is still pending",
                "user_id": user.id
            }


    # -------------------------------------------------------
    # LOGIN
    # -------------------------------------------------------
    @staticmethod
    async def login(payload: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:

        q = await db.execute(select(User).where(User.email == payload["email"]))
        user = q.scalar_one_or_none()

        if not user or not verify_password(payload["password"], user.password_hash):
            raise HTTPException(status_code=400, detail="Invalid email or password")

        role_q = await db.execute(select(Role).where(Role.id == user.role_id))
        role = role_q.scalar_one_or_none()

        if not user.is_active:
            raise HTTPException(403, "Account suspended")


        token = create_access_token({
            "user_id": user.id,
            "role": role.name if role else "unknown"
        })

        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user.id,
            "role": role.name if role else "unknown"
        }

    # -------------------------------------------------------
    # ME
    # -------------------------------------------------------
    @staticmethod
    async def me(user_id: int, db: AsyncSession) -> Dict[str, Any]:

        q = await db.execute(select(User).where(User.id == user_id))
        user = q.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Return role name instead of role_id
        role_q = await db.execute(select(Role).where(Role.id == user.role_id))
        role = role_q.scalar_one_or_none()

        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "role_id": user.role_id,
            "role": role.name if role else None,
            "created_at": user.created_at
        }
    
    @staticmethod
    async def login_admin(payload, db: AsyncSession):

        q = await db.execute(select(User).where(User.email == payload["email"]))
        user = q.scalar_one_or_none()

        if not user:
            raise HTTPException(400, "Invalid credentials")

        role_q = await db.execute(select(Role).where(Role.id == user.role_id))
        role = role_q.scalar_one_or_none()

        if role.name != "admin":
            raise HTTPException(403, "Not an admin account")

        if not verify_password(payload["password"], user.password_hash):
            raise HTTPException(400, "Invalid credentials")

        token = create_access_token({"user_id": user.id, "role": "admin"})

        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user.id,
            "role": "admin"
        }