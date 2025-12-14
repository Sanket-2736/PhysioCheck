# database/models.py

from sqlalchemy import (
    Column, Integer, String, ForeignKey, Text, JSON, Enum,
    Float, TIMESTAMP, Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base
import enum


# ---------------------------------------------------------
# ENUMS
# ---------------------------------------------------------
class DifficultyLevel(enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class PoseType(enum.Enum):
    start = "start"
    peak = "peak"
    end = "end"
    reference = "reference"


class SessionStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    TIMEOUT = "TIMEOUT"


# ---------------------------------------------------------
# ROLES
# ---------------------------------------------------------
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)


# ---------------------------------------------------------
# USERS
# ---------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(150))
    phone = Column(String(20))
    created_at = Column(TIMESTAMP, server_default=func.now())

    role = relationship("Role")


# ---------------------------------------------------------
# PATIENTS
# ---------------------------------------------------------
class Patient(Base):
    __tablename__ = "patients"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    age = Column(Integer)
    gender = Column(String(20))

    profile_photo = Column(String(500))
    height_cm = Column(Integer)
    weight_kg = Column(Float)
    address = Column(String(500))
    injury_description = Column(String(500))
    goals = Column(String(500))

    user = relationship("User")
    physician_id = Column(
        Integer,
        ForeignKey("physicians.user_id"),
        nullable=True   
    )

    physician = relationship("Physician", back_populates="patients")



# ---------------------------------------------------------
# PHYSICIANS
# ---------------------------------------------------------
class Physician(Base):
    __tablename__ = "physicians"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    specialization = Column(String(150))
    license_id = Column(String(100))
    is_verified = Column(Boolean, default=False)
    years_experience = Column(Integer)
    credential_photo = Column(String(500))


    # NEW: store profile photo url
    profile_photo = Column(String(500))

    user = relationship("User")

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)

    patients = relationship("Patient", back_populates="physician")



# ---------------------------------------------------------
# EXERCISES (master)
# ---------------------------------------------------------
class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True, nullable=False)
    category = Column(String(100))
    difficulty = Column(Enum(DifficultyLevel))
    target_body_parts = Column(JSON)
    created_by = Column(Integer, ForeignKey("physicians.user_id"))
    created_at = Column(TIMESTAMP, server_default=func.now())



class ExercisePreset(Base):
    __tablename__ = "exercise_presets"

    id = Column(Integer, primary_key=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    preset = Column(JSON, nullable=False)   # captureTime, criticalJoints, alignmentRules…
    created_at = Column(TIMESTAMP, server_default=func.now())

    exercise = relationship("Exercise")


# ---------------------------------------------------------
# POSE TEMPLATES (reference/start/peak/end)
# ---------------------------------------------------------
class PoseTemplate(Base):
    __tablename__ = "pose_templates"

    id = Column(Integer, primary_key=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)

    pose_type = Column(Enum(PoseType), default=PoseType.reference)

    joints = Column(JSON, nullable=False)
    reference_angles = Column(JSON, nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now())

    exercise = relationship("Exercise")



# ---------------------------------------------------------
# EXERCISE RULES (joint angles, alignment, thresholds)
# ---------------------------------------------------------
class ExerciseRule(Base):
    __tablename__ = "exercise_rules"

    id = Column(Integer, primary_key=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    rules = Column(JSON, nullable=False)       # thresholds, scoring, alignment rules
    created_at = Column(TIMESTAMP, server_default=func.now())

    exercise = relationship("Exercise")


# ---------------------------------------------------------
# EXERCISE LOGIC (rep counting, phases, errors)
# ---------------------------------------------------------
class ExerciseLogic(Base):
    __tablename__ = "exercise_logic"

    id = Column(Integer, primary_key=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    logic = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    exercise = relationship("Exercise")


# ---------------------------------------------------------
# REHAB PLANS
# ---------------------------------------------------------
class RehabPlan(Base):
    __tablename__ = "rehab_plans"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.user_id"), nullable=False)
    physician_id = Column(Integer, ForeignKey("physicians.user_id"), nullable=False)
    notes = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    patient = relationship("Patient")
    physician = relationship("Physician")


class RehabPlanExercise(Base):
    __tablename__ = "rehab_plan_exercises"

    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey("rehab_plans.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    target_reps = Column(Integer)
    target_sets = Column(Integer)
    max_duration = Column(Integer)
    custom_rules = Column(JSON)

    plan = relationship("RehabPlan")
    exercise = relationship("Exercise")


# ---------------------------------------------------------
# PATIENT SESSIONS
# ---------------------------------------------------------
class Session(Base):
    __tablename__ = "sessions"

    id = Column(String(100), primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.user_id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    target_reps = Column(Integer)
    max_duration = Column(Integer)
    status = Column(Enum(SessionStatus), default=SessionStatus.ACTIVE)
    started_at = Column(TIMESTAMP, server_default=func.now())
    ended_at = Column(TIMESTAMP)

    patient = relationship("Patient")
    exercise = relationship("Exercise")


class SessionProgress(Base):
    __tablename__ = "session_progress"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), ForeignKey("sessions.id"))
    event = Column(JSON)               # repCount, measuredAngles, phase, status
    timestamp = Column(TIMESTAMP, server_default=func.now())

    session = relationship("Session")


class SessionResult(Base):
    __tablename__ = "session_results"

    session_id = Column(String(100), ForeignKey("sessions.id"), primary_key=True)
    summary = Column(JSON, nullable=False)
    completed_at = Column(TIMESTAMP, server_default=func.now())

    session = relationship("Session")


# ---------------------------------------------------------
# ANALYTICS TABLES
# ---------------------------------------------------------
class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.user_id"))
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    session_id = Column(String(100), ForeignKey("sessions.id"))
    metric_key = Column(String(100))
    metric_value = Column(Float)
    timestamp = Column(TIMESTAMP, server_default=func.now())

    patient = relationship("Patient")
    exercise = relationship("Exercise")
    session = relationship("Session")


class CommonError(Base):
    __tablename__ = "common_errors"

    id = Column(Integer, primary_key=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    error_type = Column(String(100))
    occurrences = Column(Integer)

    exercise = relationship("Exercise")


# ---------------------------------------------------------
# AI SUGGESTIONS
# ---------------------------------------------------------
class AIRuleSuggestion(Base):
    __tablename__ = "ai_rule_suggestions"

    id = Column(Integer, primary_key=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    suggestion = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())

    exercise = relationship("Exercise")
