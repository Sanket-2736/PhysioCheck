import cv2
import mediapipe as mp
import time
import math
from typing import Dict, Any, Optional, Callable

from pose_tracking_patient import evaluate_frame

mp_pose = mp.solutions.pose

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


def ema(new: Optional[float], prev: Optional[float], alpha: float = 0.7) -> Optional[float]:
    if new is None:
        return prev
    if prev is None:
        return new
    return alpha * new + (1 - alpha) * prev


# -------------------------------------------------
# Lenient validation (continuous)
# -------------------------------------------------
def validate_critical_joints(joints, critical, vis_thr=0.35):
    missing = []
    for j in critical:
        if j not in joints or joints[j]["visibility"] < vis_thr:
            missing.append(j)
    return len(missing) == 0, missing


# -------------------------------------------------
# Frame evaluation (smoothed + phase-gated)
# -------------------------------------------------
def evaluateframe(exercise_def, joints, state, dt):
    measured_angles = {}
    smoothed = state.get('smoothedAngles', {})
    name = exercise_def['exerciseName']
    
    # GENERIC: Get rep definition from exercise config/DB
    rep_def = exercise_def.get('repDefinition', {})  # {'joint': 'left_shoulder', 'validRange': [50,110], ...}
    if rep_def:
        joint = rep_def['joint']
        raw_angle = get_angle(joints, *rep_def.get('joints', [joint, 'left_shoulder', 'left_hip']))  # Default joints
        smoothed_angle = ema(raw_angle, smoothed.get(joint), alpha=0.7)
        measured_angles[joint] = smoothed_angle
        
        # Generic phase detection (looser thresholds)
        low, high = rep_def.get('validRange', [50, 110])  # Was [40,100]
        exit_low, exit_high = rep_def.get('exitRange', [0, 60])
        
        if smoothed_angle is not None:
            phase = 'down' if smoothed_angle < low else 'up' if smoothed_angle > high else 'mid'
            
            # Rep count on down->up transition
            if state.get('phase') == 'down' and phase == 'up':
                state['repCount'] = state.get('repCount', 0) + 1
            state['phase'] = phase
    
    # Alignment rules (exercise-specific but generic structure)
    if state.get('phase') in ['mid', 'up']:
        rules = exercise_def.get('alignmentRules', {})
        shoulder_rule = rules.get('shoulderLevel')
        if shoulder_rule and 'left_shoulder' in joints and 'right_shoulder' in joints:
            diff = abs(joints['left_shoulder'][1] - joints['right_shoulder'][1])
            if diff > shoulder_rule.get('maxHeightDifference', 0.03):
                state.setdefault('errorTimers', {}).setdefault('shoulderAsymmetry', 0.0)
                state['errorTimers']['shoulderAsymmetry'] += dt
                state.setdefault('errorStats', {}).setdefault('shoulderAsymmetry', {'count': 0, 'totalTime': 0.0})
                state['errorStats']['shoulderAsymmetry']['totalTime'] += dt
                if state['errorTimers']['shoulderAsymmetry'] > 0.4:
                    state['errorStats']['shoulderAsymmetry']['count'] += 1
                    state['errorTimers']['shoulderAsymmetry'] = 0.0
            else:
                state['errorTimers']['shoulderAsymmetry'] = 0.0
    
    # Update joint stats
    for joint, angle in measured_angles.items():
        if angle is None: continue
        js = state.setdefault('jointStats', {}).setdefault(joint, {'min': angle, 'max': angle, 'sum': 0.0, 'count': 0})
        js['min'] = min(js['min'], angle)
        js['max'] = max(js['max'], angle)
        js['sum'] += angle
        js['count'] += 1
    
    return measured_angles  # SAME OUTPUT STRUCTURE



# -------------------------------------------------
# FINAL SUMMARY + LIFECYCLE
# -------------------------------------------------
def build_final_summary(state, exercise_name, target_reps):
    duration = time.time() - state["startTime"]

    penalty = sum(
        e["totalTime"] for e in state["errorStats"].values()
    )
    quality = max(0.0, 1.0 - (penalty / max(duration, 1)))

    return {
        "exerciseName": exercise_name,
        "targetReps": target_reps,
        "completedReps": state["repCount"],
        "duration": round(duration, 2),
        "qualityScore": round(quality, 2),
        "sessionStatus": state["status"],

        "errorsSummary": state["errorStats"],

        "tracking": {
            "lostTime": round(state["lostTrackingTime"], 2),
            "stability": (
                "good" if state["lostTrackingTime"] < 2 else
                "moderate" if state["lostTrackingTime"] < 5 else
                "poor"
            )
        }
    }


# -------------------------------------------------
# PUBLIC API – USER SESSION (HARDENED)
# -------------------------------------------------
def run_exercise_session(
    exercise_definition: Dict[str, Any],
    target_reps: int,
    max_duration: int,
    callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    show_video: bool = False
) -> Dict[str, Any]:

    cap = cv2.VideoCapture(0)

    state = {
        "phase": "idle",
        "status": "ACTIVE",   # ACTIVE / PAUSED / COMPLETED / TIMEOUT

        "repCount": 0,

        "errorTimers": {
            "shoulderAsymmetry": 0.0
        },

        "errorStats": {
            "shoulderAsymmetry": {
                "count": 0,
                "totalTime": 0.0
            }
        },

        "unstableTime": 0.0,
        "lostTrackingTime": 0.0,
        "startTime": time.time(),

        "smoothedAngles": {}
    }

    last_time = state["startTime"]

    with mp_pose.Pose(
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as pose:

        while cap.isOpened():
            now = time.time()

            # ---- TIMEOUT CHECK ----
            if now - state["startTime"] >= max_duration:
                state["status"] = "TIMEOUT"
                break

            ok, frame = cap.read()
            if not ok:
                continue

            dt = now - last_time
            last_time = now

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = pose.process(rgb)

            if not result.pose_landmarks:
                state["lostTrackingTime"] += dt
                state["status"] = "PAUSED"
                continue

            joints = extract_pose_dictionary(result.pose_landmarks)

            valid, _ = validate_critical_joints(
                joints, exercise_definition["criticalJoints"]
            )

            if not valid:
                state["unstableTime"] += dt
                state["lostTrackingTime"] += dt
                state["status"] = "PAUSED"

                if state["unstableTime"] < 0.5:
                    continue
                else:
                    continue
            else:
                state["unstableTime"] = 0.0
                state["status"] = "ACTIVE"

            measured_angles = evaluate_frame(
                exercise_definition, joints, state, dt
            )

            # Optional live progress callback
            if callback and state["phase"] == "up":
                callback({
                    "event": "progress",
                    "repCount": state["repCount"],
                    "status": state["status"],
                    "measuredAngles": measured_angles
                })

            if show_video:
                import cv2 as _cv2
                _cv2.putText(
                    frame,
                    f"Reps: {state['repCount']}  Time: {int(now - state['startTime'])}s  Status: {state['status']}",
                    (10, 30),
                    _cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )
                _cv2.imshow("User Exercise", frame)
                if _cv2.waitKey(1) & 0xFF == ord('q'):
                    state["status"] = "COMPLETED"
                    break

            if state["repCount"] >= target_reps:
                state["status"] = "COMPLETED"
                break

    cap.release()
    if show_video:
        import cv2 as _cv2
        _cv2.destroyAllWindows()

    return build_final_summary(
        state,
        exercise_definition["exerciseName"],
        target_reps
    )


# -------------------------------------------------
# LOCAL TEST – user side
# -------------------------------------------------
if __name__ == "__main__":
    # In real backend, this comes from DB:
    physician_definition = {
        "exerciseName": "ShoulderRaise",
        "criticalJoints": ["left_shoulder", "right_shoulder"],
        "alignmentRules": {
            "shoulderLevel": {
                "maxHeightDifference": 0.03,
                "errorMessage": "Keep shoulders level"
            }
        }
    }

    def cb(ev):
        print(ev)

    summary = run_exercise_session(
        exercise_definition=physician_definition,
        target_reps=5,
        max_duration=20,
        callback=cb,
        show_video=True
    )

    print("\n✅ FINAL SUMMARY:\n", summary)

import time

def init_session_state(target_reps: int):
    return {
        "startTime": time.time(),
        "repCount": 0,
        "phase": "down",
        "status": "ACTIVE",

        "errorSummary": {},
        "jointStats": {},     

        "smoothedAngles": {},
        "errorStats": {},
        "lastTimestamp": None,

        "targetReps": target_reps
    }

import time

def process_frame(
    frame_bytes: bytes,
    exercise_definition: dict,
    state: dict,
    frame: dict | None = None,   # 🔥 NEW: pass frame with angles
):
    """
    Generalised, direction-agnostic rep detection
    Now driven by incoming frame['angles'] instead of time.
    """
    now = time.time()

    # ---- 1) Get raw angle from frame ----
    rep = exercise_definition.get("repDefinition", {
        "joint": "left_shoulder",
        "validRange": [80, 120],
        "exitRange": [0, 60],
        "minHoldTime": 0.25,
    })

    joint_name = rep.get("joint", "left_shoulder")
    angles = (frame or {}).get("angles") or {}

    # if joint missing, keep angle outside valid range to avoid fake reps
    raw_angle = float(angles.get(joint_name, 0.0))

    low, high = rep["validRange"]
    exit_low, exit_high = rep["exitRange"]
    min_hold = rep["minHoldTime"]

    # ---- 2) Init state ----
    state.setdefault("repState", "OUTSIDE")
    state.setdefault("enteredAt", None)
    state.setdefault("lastAngle", raw_angle)
    state.setdefault("targetReps", state.get("targetReps", 5))
    state.setdefault("startTime", state.get("startTime", now))
    state.setdefault("status", state.get("status", "ACTIVE"))

    # ---- 3) Smooth angle ----
    alpha = 0.6
    angle = alpha * raw_angle + (1 - alpha) * state["lastAngle"]
    state["lastAngle"] = angle

    # ---- 4) Rep state machine ----
    if state["repState"] == "OUTSIDE":
        if low <= angle <= high:
            state["repState"] = "ENTERED"
            state["enteredAt"] = now

    elif state["repState"] == "ENTERED":
        if low <= angle <= high:
            if now - state["enteredAt"] >= min_hold:
                state["repCount"] = state.get("repCount", 0) + 1
                state["repState"] = "COUNTED"
        else:
            state["repState"] = "OUTSIDE"
            state["enteredAt"] = None

    elif state["repState"] == "COUNTED":
        if exit_low <= angle <= exit_high:
            state["repState"] = "OUTSIDE"
            state["enteredAt"] = None

    # ---- 5) Session completion ----
    if state.get("repCount", 0) >= state["targetReps"]:
        state["status"] = "COMPLETED"

    return {
        "status": state["status"],
        "repCount": state.get("repCount", 0),
        "angle": round(angle, 1),
        "repState": state["repState"],
    }


from database.models import ExerciseSession
from datetime import datetime

async def save_exercise_session(
    db,
    patient_id: int,
    physician_id: int,
    exercise_id: int,
    patient_exercise_id: int,
    state: dict
):
    session = ExerciseSession(
        patient_id=patient_id,
        physician_id=physician_id,
        exercise_id=exercise_id,
        patient_exercise_id=patient_exercise_id,
        completed_reps=state["repCount"],
        completed_sets=1,
        accuracy_score=0.0,
        error_summary={},
        joint_stats={},
        duration_sec=time.time() - state["startTime"],
        ended_at=datetime.utcnow()
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session
