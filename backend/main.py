from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import threading
import cv2
import uuid

from pose.pose_tracking_patient import run_exercise_session

# DB imports
from database.connection import get_db
from database.models import Exercise, ExercisePreset, Session, SessionProgress, SessionResult

# FastAPI app with enhanced documentation
app = FastAPI(
    title="PhysioCheck Backend API",
    description="""
    ## PhysioCheck - AI-Powered Physiotherapy Monitoring System
    
    A comprehensive physiotherapy monitoring system that uses computer vision and pose estimation 
    to track patient exercises in real-time. Built with FastAPI, MediaPipe, and MySQL.
    
    ### Key Features:
    - **Real-time Pose Tracking**: Uses MediaPipe for accurate body pose estimation
    - **Exercise Management**: Physicians can create custom exercises with specific rules
    - **Session Monitoring**: Real-time tracking of patient exercise sessions
    - **Quality Assessment**: Automated scoring based on form, alignment, and completion
    - **Role-based Access**: Separate interfaces for physicians, patients, and administrators
    
    ### Authentication:
    Most endpoints require authentication. Use the `/auth/login` endpoint to obtain a JWT token,
    then include it in the Authorization header as `Bearer <token>`.
    
    ### Getting Started:
    1. Register as a patient or physician using `/auth/register` or `/auth/register-physician`
    2. Login to get your access token
    3. Explore the available exercises with `/exercises`
    4. Start a session with `/start-session`
    """,
    version="1.2.0",
    contact={
        "name": "PhysioCheck Development Team",
        "email": "support@physiocheck.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.physiocheck.com",
            "description": "Production server"
        }
    ]
)

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

# ---------------------------------------------------
# DOCUMENTATION AND INFO ROUTES
# ---------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Root endpoint with API information and documentation links.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PhysioCheck Backend API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
            .links { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 30px 0; }
            .link-card { background: #ecf0f1; padding: 20px; border-radius: 8px; text-align: center; text-decoration: none; color: #2c3e50; transition: transform 0.2s; }
            .link-card:hover { transform: translateY(-2px); background: #d5dbdb; }
            .status { background: #2ecc71; color: white; padding: 10px; border-radius: 5px; text-align: center; margin: 20px 0; }
            .feature { background: #3498db; color: white; padding: 15px; margin: 10px 0; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏥 PhysioCheck Backend API</h1>
            <div class="status">✅ API is running successfully!</div>
            
            <p>Welcome to the PhysioCheck Backend API - an AI-powered physiotherapy monitoring system that uses computer vision and pose estimation to track patient exercises in real-time.</p>
            
            <div class="links">
                <a href="/docs" class="link-card">
                    <h3>📚 Interactive API Docs</h3>
                    <p>Swagger UI with live API testing</p>
                </a>
                <a href="/redoc" class="link-card">
                    <h3>📖 Alternative Docs</h3>
                    <p>ReDoc documentation interface</p>
                </a>
                <a href="/exercises" class="link-card">
                    <h3>🏃‍♂️ Available Exercises</h3>
                    <p>List all available exercises</p>
                </a>
                <a href="/video-feed" class="link-card">
                    <h3>📹 Live Camera Feed</h3>
                    <p>Real-time pose tracking stream</p>
                </a>
            </div>
            
            <h2>🚀 Key Features</h2>
            <div class="feature">Real-time Pose Tracking with MediaPipe</div>
            <div class="feature">Custom Exercise Creation for Physicians</div>
            <div class="feature">Live Session Monitoring & Quality Assessment</div>
            <div class="feature">Role-based Access Control</div>
            
            <h2>🔗 Quick Links</h2>
            <ul>
                <li><strong>Health Check:</strong> <code>GET /health</code></li>
                <li><strong>Login:</strong> <code>POST /auth/login</code></li>
                <li><strong>Register Patient:</strong> <code>POST /auth/register</code></li>
                <li><strong>Register Physician:</strong> <code>POST /auth/register-physician</code></li>
            </ul>
            
            <p><small>Version 1.2.0 | Built with FastAPI, MediaPipe & MySQL</small></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify API status.
    """
    return {
        "status": "healthy",
        "service": "PhysioCheck Backend API",
        "version": "1.2.0",
        "timestamp": "2024-12-18T10:00:00Z"
    }

@app.get("/api-info")
async def api_info():
    """
    Get API information and available endpoints.
    """
    return {
        "name": "PhysioCheck Backend API",
        "version": "1.2.0",
        "description": "AI-powered physiotherapy monitoring system",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        },
        "key_endpoints": {
            "authentication": ["/auth/login", "/auth/register", "/auth/register-physician"],
            "exercises": ["/exercises", "/exercise/{id}"],
            "sessions": ["/start-session", "/session/{id}"],
            "streaming": ["/video-feed"],
            "health": ["/health", "/"]
        },
        "features": [
            "Real-time pose tracking",
            "Exercise management",
            "Session monitoring",
            "Quality assessment",
            "Role-based access"
        ]
    }

# Redirect common documentation paths
@app.get("/documentation")
async def redirect_to_docs():
    """Redirect to main documentation."""
    return RedirectResponse(url="/docs")

@app.get("/api")
async def redirect_to_api_info():
    """Redirect to API information."""
    return RedirectResponse(url="/api-info")

from database.connection import engine, Base

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# To run the app:
# python -m uvicorn main:app --reload
# 
# Available documentation routes:
# - http://localhost:8000/ (Landing page with links)
# - http://localhost:8000/docs (Swagger UI)
# - http://localhost:8000/redoc (ReDoc)
# - http://localhost:8000/health (Health check)
# - http://localhost:8000/api-info (API information)