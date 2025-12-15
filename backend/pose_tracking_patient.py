import cv2
import mediapipe as mp
import time
import math
import numpy as np
from typing import Dict, Any, Optional

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
# FRAME EVALUATION (REPS + ALERTS)
# -------------------------------------------------
def evaluate_frame(exercise_def, joints, state, dt):
    smoothed = state["smoothedAngles"]
    measured = {}
    alerts = []

    name = exercise_def["exerciseName"]

    # ---------- SHOULDER RAISE ----------
    if name == "ShoulderRaise":
        raw_l = get_angle(joints, "left_elbow", "left_shoulder", "left_hip")
        raw_r = get_angle(joints, "right_elbow", "right_shoulder", "right_hip")

        smoothed["left"] = ema(raw_l, smoothed.get("left"))
        smoothed["right"] = ema(raw_r, smoothed.get("right"))

        measured["left_shoulder"] = smoothed["left"]
        measured["right_shoulder"] = smoothed["right"]

        avg = None
        if smoothed["left"] and smoothed["right"]:
            avg = (smoothed["left"] + smoothed["right"]) / 2

        # ---- PHASE + AUTO REP COUNT ----
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

        # ---- RISK DETECTION ----
        if avg and avg > 165:
            alerts.append("Shoulder hyperextension risk")

        spine = get_angle(joints, "left_shoulder", "left_hip", "left_knee")
        if spine and spine > 40:
            alerts.append("Excessive spine bending")

        # ---- ALIGNMENT ERROR ----
        rule = exercise_def.get("alignmentRules", {}).get("shoulderLevel")
        if rule:
            diff = abs(
                joints["left_shoulder"]["y"] -
                joints["right_shoulder"]["y"]
            )
            if diff > rule["maxHeightDifference"]:
                state["errorStats"]["shoulderAsymmetry"]["totalTime"] += dt
                alerts.append(rule["errorMessage"])

    state["alerts"] = alerts
    return measured


# -------------------------------------------------
# SESSION INITIALIZER (CALL ON SESSION START)
# -------------------------------------------------
def init_session_state():
    return {
        "phase": "idle",
        "repCount": 0,
        "alerts": [],
        "lostTrackingTime": 0.0,
        "startTime": time.time(),
        "lastTime": time.time(),
        "smoothedAngles": {},
        "errorStats": {
            "shoulderAsymmetry": {
                "count": 0,
                "totalTime": 0.0
            }
        },
        "pose": mp_pose.Pose(
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
    }


# -------------------------------------------------
# FRAME API ENTRY POINT
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
        state["lostTrackingTime"] += dt
        return {"status": "NO_POSE"}

    joints = extract_pose_dictionary(result.pose_landmarks)

    if not validate_critical_joints(
        joints, exercise_definition["criticalJoints"]
    ):
        state["lostTrackingTime"] += dt
        return {"status": "UNSTABLE"}

    measured = evaluate_frame(
        exercise_definition, joints, state, dt
    )

    return {
        "status": "OK",
        "repCount": state["repCount"],
        "phase": state["phase"],
        "measuredAngles": measured,
        "alerts": state["alerts"]
    }
