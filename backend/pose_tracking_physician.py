import cv2
import mediapipe as mp
import time
import math
import json
from typing import Dict, Any, Optional

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


# -------------------------------------------------
# EXERCISE DEFINITIONS (physician-facing presets)
# -------------------------------------------------
EXERCISE_LIBRARY: Dict[str, Dict[str, Any]] = {
    "ShoulderRaise": {
        "captureTime": 5,
        "criticalJoints": ["left_shoulder", "right_shoulder"],
        "angleDefinitions": {
            "shoulder": {
                "minAngle": 40,
                "maxAngle": 140,
                "errorIfNotReached": "Raise arms higher"
            }
        },
        "alignmentRules": {
            "shoulderLevel": {
                "maxHeightDifference": 0.03,
                "errorMessage": "Keep shoulders level"
            }
        }
    },

    "BicepCurl": {
        "captureTime": 5,
        "criticalJoints": ["left_elbow", "right_elbow"],
        "angleDefinitions": {
            "elbow": {
                "minAngle": 40,
                "maxAngle": 160,
                "errorIfNotReached": "Complete the curl"
            }
        },
        "alignmentRules": {}
    }
}


# -------------------------------------------------
# Pose extraction / angles
# -------------------------------------------------
def extract_pose_dictionary(landmarks) -> Dict[str, Dict[str, float]]:
    joints: Dict[str, Dict[str, float]] = {}
    for idx, name in enumerate(mp_pose.PoseLandmark):
        lm = landmarks.landmark[idx]
        joints[name.name.lower()] = {
            "x": lm.x,
            "y": lm.y,
            "z": lm.z,
            "visibility": lm.visibility
        }
    return joints


def compute_angle(a, b, c) -> float:
    angle = abs(
        math.degrees(
            math.atan2(c[1] - b[1], c[0] - b[0]) -
            math.atan2(a[1] - b[1], a[0] - b[0])
        )
    )
    return 360 - angle if angle > 180 else angle


def get_angle(joints: Dict[str, Dict[str, float]],
              a: str, b: str, c: str) -> Optional[float]:
    if a in joints and b in joints and c in joints:
        return compute_angle(
            (joints[a]["x"], joints[a]["y"]),
            (joints[b]["x"], joints[b]["y"]),
            (joints[c]["x"], joints[c]["y"])
        )
    return None


def validate_visibility(joints: Dict[str, Dict[str, float]],
                        critical: list,
                        thr: float = 0.5) -> bool:
    for j in critical:
        if j not in joints or joints[j]["visibility"] < thr:
            return False
    return True


# -------------------------------------------------
# Physician static capture → exercise definition JSON
# -------------------------------------------------
def capture_exercise_definition(exercise_name: str) -> Dict[str, Any]:
    if exercise_name not in EXERCISE_LIBRARY:
        return {"error": "Invalid exercise"}

    meta = EXERCISE_LIBRARY[exercise_name]
    capture_time = meta["captureTime"]

    cap = cv2.VideoCapture(0)
    start_time = time.time()
    final_joints: Optional[Dict[str, Dict[str, float]]] = None

    with mp_pose.Pose(
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6
    ) as pose:

        while cap.isOpened():
            ok, frame = cap.read()
            if not ok:
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = pose.process(rgb)

            if result.pose_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    result.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )
                final_joints = extract_pose_dictionary(result.pose_landmarks)

            cv2.imshow("Physician Capture", frame)

            if time.time() - start_time >= capture_time:
                break

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()

    if not final_joints:
        return {"error": "No pose detected"}

    if not validate_visibility(final_joints, meta["criticalJoints"]):
        return {"error": "Critical joints not clearly visible in capture"}

    # -------------------------------------------------
    # Reference angles per exercise (for future advanced use)
    # -------------------------------------------------
    reference_angles: Dict[str, float] = {}

    if exercise_name == "ShoulderRaise":
        reference_angles["left_shoulder"] = get_angle(
            final_joints, "left_elbow", "left_shoulder", "left_hip"
        )
        reference_angles["right_shoulder"] = get_angle(
            final_joints, "right_elbow", "right_shoulder", "right_hip"
        )

    elif exercise_name == "BicepCurl":
        reference_angles["left_elbow"] = get_angle(
            final_joints, "left_shoulder", "left_elbow", "left_wrist"
        )
        reference_angles["right_elbow"] = get_angle(
            final_joints, "right_shoulder", "right_elbow", "right_wrist"
        )

    exercise_definition: Dict[str, Any] = {
        "exerciseName": exercise_name,
        "criticalJoints": meta["criticalJoints"],
        "referenceAngles": reference_angles,
        "jointAngles": meta.get("angleDefinitions", {}),
        "alignmentRules": meta.get("alignmentRules", {}),
        "createdBy": "physician",
        "createdAt": time.time()
    }

    return exercise_definition


# -------------------------------------------------
# LOCAL TEST (physician side)
# -------------------------------------------------
if __name__ == "__main__":
    exercise = "ShoulderRaise"
    definition = capture_exercise_definition(exercise)

    print("\n✅ PHYSICIAN EXERCISE DEFINITION:\n")
    print(json.dumps(definition, indent=2))
