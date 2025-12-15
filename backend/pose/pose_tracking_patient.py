import cv2
import mediapipe as mp
import time
import math
from typing import Dict, Any, Optional, Callable

mp_pose = mp.solutions.pose


# -------------------------------------------------
# Pose helpers
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
def evaluate_frame(exercise_def, joints, state, dt):
    measured_angles = {}
    smoothed = state["smoothedAngles"]

    name = exercise_def["exerciseName"]

    # ------------- SHOULDER RAISE -------------
    if name == "ShoulderRaise":
        raw_left = get_angle(joints, "left_elbow", "left_shoulder", "left_hip")
        raw_right = get_angle(joints, "right_elbow", "right_shoulder", "right_hip")

        smoothed["left_shoulder"] = ema(raw_left, smoothed.get("left_shoulder"))
        smoothed["right_shoulder"] = ema(raw_right, smoothed.get("right_shoulder"))

        measured_angles["left_shoulder"] = smoothed["left_shoulder"]
        measured_angles["right_shoulder"] = smoothed["right_shoulder"]

        if smoothed["left_shoulder"] and smoothed["right_shoulder"]:
            avg = (smoothed["left_shoulder"] + smoothed["right_shoulder"]) / 2.0
        else:
            avg = None

        # ---- Phase detection & reps ----
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

        # ---- Alignment rule (only active in mid/up) ----
        if state["phase"] in ("mid", "up"):
            rule = exercise_def.get("alignmentRules", {}).get("shoulderLevel")
            if rule and "left_shoulder" in joints and "right_shoulder" in joints:
                diff = abs(
                    joints["left_shoulder"]["y"] -
                    joints["right_shoulder"]["y"]
                )

                if diff > rule["maxHeightDifference"]:
                    state["errorTimers"]["shoulderAsymmetry"] += dt
                    state["errorStats"]["shoulderAsymmetry"]["totalTime"] += dt

                    if state["errorTimers"]["shoulderAsymmetry"] > 0.4:
                        state["errorStats"]["shoulderAsymmetry"]["count"] += 1
                        state["errorTimers"]["shoulderAsymmetry"] = 0.0
                else:
                    state["errorTimers"]["shoulderAsymmetry"] = 0.0

    # (Later: add more exercises here branching on exercise_def["exerciseName"])

    return measured_angles


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

def init_session_state(target_reps: int):
    return {
        "phase": "idle",
        "status": "ACTIVE",
        "repCount": 0,
        "targetReps": target_reps,

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

def process_frame(frame_bytes: bytes, exercise_definition: dict, state: dict):
    import numpy as np

    img = cv2.imdecode(
        np.frombuffer(frame_bytes, np.uint8),
        cv2.IMREAD_COLOR
    )

    with mp_pose.Pose(
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as pose:

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = pose.process(rgb)

        if not result.pose_landmarks:
            state["lostTrackingTime"] += 0.03
            return {"status": "PAUSED", "reason": "No pose detected"}

        joints = extract_pose_dictionary(result.pose_landmarks)

        valid, missing = validate_critical_joints(
            joints, exercise_definition["criticalJoints"]
        )
        if not valid:
            return {"status": "PAUSED", "missingJoints": missing}

        evaluate_frame(
            exercise_definition,
            joints,
            state,
            dt=0.03
        )

        if state["repCount"] >= state["targetReps"]:
            state["status"] = "COMPLETED"

        return {
            "status": state["status"],
            "repCount": state["repCount"]
        }

from database.models import ExerciseSession

async def save_exercise_session(
    db,
    patient_id,
    physician_id,
    exercise_id,
    patient_exercise_id,
    state
):
    duration = time.time() - state["startTime"]

    session = ExerciseSession(
        patient_id=patient_id,
        physician_id=physician_id,
        exercise_id=exercise_id,
        patient_exercise_id=patient_exercise_id,
        completed_reps=state["repCount"],
        accuracy_score=1.0,  # refine later
        error_summary=state["errorStats"],
        duration_sec=duration
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session
