from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import threading
import cv2
import uuid

from pose.pose_tracking_patient import run_exercise_session

# DB imports
from database.connection import get_db
from database.models import Exercise, ExercisePreset, Session, SessionProgress, SessionResult


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


# -----------------------------
# ❗ GLOBAL ERROR HANDLERS
# -----------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    # Catch ANY unhandled exception
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal server error!"}
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    # For HTTP errors you raise manually (like 404)
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    # For FastAPI validation errors
    return JSONResponse(
        status_code=422,
        content={"success": False, "message": "Invalid input!"}
    )



# ---------------------------------------------------
# CAMERA STREAM (same as your original file)
# ---------------------------------------------------
camera = cv2.VideoCapture(0)
lock = threading.Lock()

from routers.auth_router import router as auth_router
from routers.exercises_router import router as exercises_router
from routers.rehab_router import router as rehab_router
from routers.sessions_router import router as sessions_router
from routers.profile_router import router as profile_router
from routers.admin_router import router as admin_router
from routers.subscription_router import router as subscription_router
from routers.physician_router import router as physician_router
from routers.patient_router import router as patient_router
from routers.patient_exercises_router import router as patient_exercises_router
from routers.subscription_request_router import router as subscription_request_router

app.include_router(subscription_request_router)
app.include_router(patient_exercises_router)
app.include_router(patient_router)
app.include_router(physician_router)
app.include_router(subscription_router)
app.include_router(admin_router)
app.include_router(profile_router)
app.include_router(auth_router)
app.include_router(exercises_router)
app.include_router(rehab_router)
app.include_router(sessions_router)


def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break

        _, buffer = cv2.imencode(".jpg", frame)
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            buffer.tobytes() +
            b"\r\n"
        )


@app.get("/video-feed")
def video_feed():
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


# ---------------------------------------------------
# 1️⃣ LIST EXERCISES (NO STATIC EXERCISE_LIBRARY)
# ---------------------------------------------------
@app.get("/exercises")
async def list_exercises(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Exercise))
    rows = result.scalars().all()
    return [{"id": e.id, "name": e.name} for e in rows]


# ---------------------------------------------------
# 2️⃣ GET FULL EXERCISE DEFINITION FROM DB
# ---------------------------------------------------
@app.get("/exercise/{exercise_id}")
async def get_exercise_definition(exercise_id: int, db: AsyncSession = Depends(get_db)):
    # Fetch Exercise
    result = await db.execute(select(Exercise).where(Exercise.id == exercise_id))
    exercise = result.scalar_one_or_none()

    if not exercise:
        raise HTTPException(404, detail="Exercise not found")

    # Fetch Preset
    preset_q = await db.execute(select(ExercisePreset).where(ExercisePreset.exercise_id == exercise_id))
    preset = preset_q.scalar_one_or_none()

    if not preset:
        raise HTTPException(404, detail="Exercise preset not found")

    return {
        "exerciseId": exercise_id,
        "exerciseName": exercise.name,
        "category": exercise.category,
        "difficulty": exercise.difficulty.value if exercise.difficulty else None,
        "targetBodyParts": exercise.target_body_parts,
        "preset": preset.preset,     # contains criticalJoints, angleDefinitions, alignmentRules, etc.
    }


# ---------------------------------------------------
# 3️⃣ START PATIENT SESSION
# ---------------------------------------------------
@app.post("/start-session")
async def start_session(
    exercise_id: int,
    patient_id: int,
    target_reps: int = 5,
    max_duration: int = 30,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db)
):
    # Validate Exercise
    result = await db.execute(select(Exercise).where(Exercise.id == exercise_id))
    exercise = result.scalar_one_or_none()

    if not exercise:
        raise HTTPException(404, detail="Invalid exercise")

    # Load preset (joint rules, alignment rules, etc.)
    preset_q = await db.execute(select(ExercisePreset).where(ExercisePreset.exercise_id == exercise_id))
    preset = preset_q.scalar_one_or_none()

    if not preset:
        raise HTTPException(404, detail="No preset configured for this exercise")

    # Build the definition expected by pose_tracking_patient
    exercise_definition = {
        "exerciseName": exercise.name,
        **preset.preset     # expands: criticalJoints, alignmentRules, angleDefinitions etc.
    }

    # Create session ID
    session_id = str(uuid.uuid4())

    # Store session row in DB (status = ACTIVE)
    new_session = Session(
        id=session_id,
        patient_id=patient_id,
        exercise_id=exercise_id,
        target_reps=target_reps,
        max_duration=max_duration,
    )
    db.add(new_session)
    await db.commit()

    # ----------------------------
    # CALLBACK FOR LIVE PROGRESS
    # ----------------------------
    async def save_progress(event):
        async with get_db() as s:
            progress_row = SessionProgress(
                session_id=session_id,
                event=event
            )
            s.add(progress_row)
            await s.commit()

    # Wrapper to call save_progress safely in thread
    def callback(event):
        import asyncio
        asyncio.run(save_progress(event))

    # ----------------------------
    # SESSION RUN LOGIC
    # ----------------------------
    async def save_final_result(result):
        async with get_db() as s:
            result_row = SessionResult(session_id=session_id, summary=result)
            await s.merge(result_row)

            # Set session complete
            sess = await s.get(Session, session_id)
            sess.status = "COMPLETED"
            await s.commit()

    def run():
        # Run the actual pose tracking session
        result = run_exercise_session(
            exercise_definition=exercise_definition,
            target_reps=target_reps,
            max_duration=max_duration,
            callback=callback,
            show_video=False,
        )

        import asyncio
        asyncio.run(save_final_result(result))

    # Background thread runs the session
    background_tasks.add_task(run)

    return {"sessionId": session_id}


# ---------------------------------------------------
# 4️⃣ GET SESSION STATUS (progress + final result)
# ---------------------------------------------------
@app.get("/session/{session_id}")
async def get_session_status(session_id: str, db: AsyncSession = Depends(get_db)):
    # Get session header
    sess = await db.get(Session, session_id)
    if not sess:
        raise HTTPException(404, detail="Session not found")

    # Latest progress event
    prog_q = await db.execute(
        select(SessionProgress).where(SessionProgress.session_id == session_id).order_by(SessionProgress.id.desc())
    )
    latest_prog = prog_q.scalar_one_or_none()

    # Final result if exists
    final_q = await db.execute(
        select(SessionResult).where(SessionResult.session_id == session_id)
    )
    final_result = final_q.scalar_one_or_none()

    return {
        "session": {
            "id": sess.id,
            "status": sess.status.value,
            "targetReps": sess.target_reps,
            "maxDuration": sess.max_duration,
            "startedAt": sess.started_at,
            "endedAt": sess.ended_at,
        },
        "progress": latest_prog.event if latest_prog else None,
        "final": final_result.summary if final_result else None
    }

from database.connection import engine, Base

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# To run the app:
# python -m uvicorn main:app --reload