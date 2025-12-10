from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import threading
import cv2

from pose_tracking_patient import run_exercise_session
from pose_tracking_physician import EXERCISE_LIBRARY

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# In-memory session store
# -----------------------------
sessions = {}
lock = threading.Lock()

# -----------------------------
# Camera stream (backend webcam)
# -----------------------------
camera = cv2.VideoCapture(0)

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

# -----------------------------
# APIs
# -----------------------------
@app.get("/exercises")
def list_exercises():
    return list(EXERCISE_LIBRARY.keys())


@app.get("/exercise/{name}")
def get_exercise_definition(name: str):
    if name not in EXERCISE_LIBRARY:
        return {"error": "Invalid exercise"}
    return EXERCISE_LIBRARY[name]


@app.post("/start-session")
def start_session(
    exercise_name: str,
    target_reps: int = 5,
    max_duration: int = 30,
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    if exercise_name not in EXERCISE_LIBRARY:
        return {"error": "Invalid exercise"}

    session_id = f"{exercise_name}_{len(sessions)}"

    def callback(event):
        with lock:
            sessions[session_id]["progress"] = event

    def run():
        result = run_exercise_session(
            exercise_definition={
                "exerciseName": exercise_name,
                **EXERCISE_LIBRARY[exercise_name],
            },
            target_reps=target_reps,
            max_duration=max_duration,
            callback=callback,
            show_video=False,
        )
        with lock:
            sessions[session_id]["final"] = result

    sessions[session_id] = {"progress": None, "final": None}
    background_tasks.add_task(run)

    return {"sessionId": session_id}


@app.get("/session/{session_id}")
def get_session_status(session_id: str):
    if session_id not in sessions:
        return {"error": "Invalid session"}
    return sessions[session_id]

# python -m uvicorn main:app --reload