import cv2
import mediapipe as mp
import time
import math
import numpy as np
from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from database.models import ExerciseSession

mp_pose = mp.solutions.pose


# -------------------------------------------------
# POSE HELPERS
# -------------------------------------------------
def extract_pose_dictionary(landmarks):
    joints = {}
    for idx, name in enumerate(mp_pose.PoseLandmark):
        lm = landmarks.landmark[idx]
        joints[name.name.lower()] = {
            "x": lm.x,
            "y": lm.y,
            "z": lm.z,
            "visibility": lm.visibility
        }
    return joints


def compute_angle(a, b, c):
    angle = abs(
        math.degrees(
            math.atan2(c[1] - b[1], c[0] - b[0]) -
            math.atan2(a[1] - b[1], a[0] - b[0])
        )
    )
    return 360 - angle if angle > 180 else angle


def get_angle(j, a, b, c):
    if a in j and b in j and c in j:
        return compute_angle(
            (j[a]["x"], j[a]["y"]),
            (j[b]["x"], j[b]["y"]),
            (j[c]["x"], j[c]["y"])
        )
    return None


def ema(new, prev, alpha=0.7):
    if new is None:
        return prev
    if prev is None:
        return new
    return alpha * new + (1 - alpha) * prev


# -------------------------------------------------
# VALIDATION
# -------------------------------------------------
def validate_critical_joints(joints, critical, vis_thr=0.35):
    for j in critical:
        if j not in joints or joints[j]["visibility"] < vis_thr:
            return False
    return True


# -------------------------------------------------
# FRAME EVALUATION
# -------------------------------------------------
def evaluate_frame(exercise_def, joints, state, dt):
    smoothed = state["smoothedAngles"]
    alerts = {}
    measured = {}

    if exercise_def["exerciseName"] == "ShoulderRaise":
        raw_l = get_angle(joints, "left_elbow", "left_shoulder", "left_hip")
        raw_r = get_angle(joints, "right_elbow", "right_shoulder", "right_hip")

        smoothed["l"] = ema(raw_l, smoothed.get("l"))
        smoothed["r"] = ema(raw_r, smoothed.get("r"))

        measured["left_shoulder"] = smoothed["l"]
        measured["right_shoulder"] = smoothed["r"]

        avg = None
        if smoothed["l"] and smoothed["r"]:
            avg = (smoothed["l"] + smoothed["r"]) / 2

        if avg is not None:
            if avg < 40:
                phase = "down"
            elif avg > 100:
                phase = "up"
            else:
                phase = "mid"

            if state["phase"] == "down" and phase == "up":
                state["repCount"] += 1

            state["phase"] = phase

        if avg and avg > 165:
            alerts["hyperextension"] = "Shoulder hyperextension risk"

        spine = get_angle(joints, "left_shoulder", "left_hip", "left_knee")
        if spine and spine > 40:
            alerts["spine"] = "Excessive spine bending"

    state["alerts"] = list(alerts.values())
    state["jointStats"].update(measured)

    return measured


# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
def init_session_state(target_reps: int):
    return {
        "phase": "idle",
        "repCount": 0,
        "alerts": [],
        "startTime": time.time(),
        "lastTime": time.time(),
        "smoothedAngles": {},
        "jointStats": {},
        "errorSummary": {},
        "targetReps": target_reps,
        "pose": mp_pose.Pose(
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
    }


# -------------------------------------------------
# FRAME ENTRY POINT
# -------------------------------------------------
def process_frame(
    frame_bytes: bytes,
    exercise_definition: Dict[str, Any],
    state: Dict[str, Any]
) -> Dict[str, Any]:

    now = time.time()
    dt = now - state["lastTime"]
    state["lastTime"] = now

    frame = cv2.imdecode(
        np.frombuffer(frame_bytes, np.uint8),
        cv2.IMREAD_COLOR
    )

    if frame is None:
        return {"status": "INVALID_FRAME"}

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = state["pose"].process(rgb)

    if not result.pose_landmarks:
        return {"status": "NO_POSE"}

    joints = extract_pose_dictionary(result.pose_landmarks)

    if not validate_critical_joints(
        joints, exercise_definition["criticalJoints"]
    ):
        return {"status": "UNSTABLE"}

    evaluate_frame(exercise_definition, joints, state, dt)

    completed = state["repCount"] >= state["targetReps"]

    return {
        "status": "COMPLETED" if completed else "OK",
        "repCount": state["repCount"],
        "alerts": state["alerts"]
    }


# -------------------------------------------------
# SAVE ExerciseSession (CALL ON COMPLETION)
# -------------------------------------------------
async def save_exercise_session(
    *,
    db: AsyncSession,
    patient_id: int,
    physician_id: int,
    exercise_id: int,
    patient_exercise_id: int,
    state: Dict[str, Any]
):
    duration = time.time() - state["startTime"]

    session = ExerciseSession(
        patient_id=patient_id,
        physician_id=physician_id,
        exercise_id=exercise_id,
        patient_exercise_id=patient_exercise_id,
        completed_reps=state["repCount"],
        completed_sets=1,
        accuracy_score=round(
            max(0.0, 1.0 - (len(state["alerts"]) * 0.1)), 2
        ),
        error_summary=state["alerts"],
        joint_stats=state["jointStats"],
        duration_sec=round(duration, 2)
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)

    return session
