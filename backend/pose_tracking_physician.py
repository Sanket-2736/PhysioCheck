import cv2
import time
import math
from typing import List, Dict, Any

import mediapipe as mp

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


# ----------------------------
# UTILS
# ----------------------------
def extract_pose_dictionary(pose_landmarks) -> Dict[str, Dict[str, float]]:
    joints = {}

    for idx, name in enumerate(mp_pose.PoseLandmark):
        lm = pose_landmarks.landmark[idx]
        joints[name.name.lower()] = {
            "x": lm.x,
            "y": lm.y,
            "z": lm.z,
            "visibility": lm.visibility
        }

    return joints


def calculate_angle(a, b, c) -> float:
    ab = (a["x"] - b["x"], a["y"] - b["y"])
    cb = (c["x"] - b["x"], c["y"] - b["y"])

    dot = ab[0] * cb[0] + ab[1] * cb[1]
    mag_ab = math.sqrt(ab[0] ** 2 + ab[1] ** 2)
    mag_cb = math.sqrt(cb[0] ** 2 + cb[1] ** 2)

    if mag_ab * mag_cb == 0:
        return 0.0

    cos_angle = max(-1, min(1, dot / (mag_ab * mag_cb)))
    return round(math.degrees(math.acos(cos_angle)), 2)


def compute_joint_angles(joints: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    angles = {}

    try:
        angles["left_shoulder"] = calculate_angle(
            joints["left_elbow"],
            joints["left_shoulder"],
            joints["left_hip"]
        )
        angles["right_shoulder"] = calculate_angle(
            joints["right_elbow"],
            joints["right_shoulder"],
            joints["right_hip"]
        )
        angles["left_elbow"] = calculate_angle(
            joints["left_shoulder"],
            joints["left_elbow"],
            joints["left_wrist"]
        )
        angles["right_elbow"] = calculate_angle(
            joints["right_shoulder"],
            joints["right_elbow"],
            joints["right_wrist"]
        )
    except KeyError:
        pass

    return angles


# ----------------------------
# CORE: VIDEO-BASED REP CAPTURE
# ----------------------------
def capture_rep_video(
    duration_sec: int = 6,
    min_visibility: float = 0.7,
    show_video: bool = True
) -> List[Dict[str, Any]]:

    cap = cv2.VideoCapture(0)
    frames: List[Dict[str, Any]] = []

    if not cap.isOpened():
        raise RuntimeError("Could not open webcam")

    start_time = time.time()

    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6,
    ) as pose:

        while time.time() - start_time < duration_sec:
            ok, frame = cap.read()
            if not ok:
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = pose.process(rgb)

            if not result.pose_landmarks:
                continue

            joints = extract_pose_dictionary(result.pose_landmarks)

            if any(j["visibility"] < min_visibility for j in joints.values()):
                continue

            angles = compute_joint_angles(joints)

            frames.append({
                "timestamp": time.time(),
                "joints": joints,
                "angles": angles
            })

            if show_video:
                mp_drawing.draw_landmarks(
                    frame,
                    result.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )
                cv2.putText(
                    frame,
                    "Recording demo rep...",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )
                cv2.imshow("Physician Rep Capture", frame)

                if cv2.waitKey(1) & 0xFF == 27:
                    break

    cap.release()
    cv2.destroyAllWindows()

    if len(frames) < 10:
        raise RuntimeError("Insufficient pose data captured")

    return frames
