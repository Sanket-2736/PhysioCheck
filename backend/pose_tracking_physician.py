import cv2
import mediapipe as mp
import time
import math
from typing import Dict, Any, Optional, Callable

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


# -------------------------------------------------
# Pose extraction utilities
# -------------------------------------------------
def extract_pose_dictionary(landmarks) -> Dict[str, Dict[str, float]]:
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
                        critical_joints: list,
                        thr: float = 0.5) -> bool:
    for j in critical_joints:
        if j not in joints or joints[j]["visibility"] < thr:
            return False
    return True


# -------------------------------------------------
# LIVE TRACKING (DB-READY via callback)
# -------------------------------------------------
def run_live_pose_tracking(
    exercise_id: int,
    critical_joints: list,
    angle_map: Dict[str, tuple],
    duration: int = 10,
    callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    show_video: bool = True
):
    """
    Runs live pose tracking and emits frame-by-frame features.
    angle_map example:
    {
        "left_elbow": ("left_shoulder", "left_elbow", "left_wrist"),
        "right_elbow": ("right_shoulder", "right_elbow", "right_wrist")
    }
    """

    cap = cv2.VideoCapture(0)
    start_time = time.time()

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
                joints = extract_pose_dictionary(result.pose_landmarks)

                angles = {}
                for key, (a, b, c) in angle_map.items():
                    angles[key] = get_angle(joints, a, b, c)

                event = {
                    "exercise_id": exercise_id,
                    "timestamp": time.time(),
                    "joints": joints,
                    "angles": angles,
                    "visibility_ok": validate_visibility(joints, critical_joints)
                }

                if callback:
                    callback(event)

                if show_video:
                    mp_drawing.draw_landmarks(
                        frame,
                        result.pose_landmarks,
                        mp_pose.POSE_CONNECTIONS
                    )

            if show_video:
                cv2.imshow("Live Pose Tracking", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            if time.time() - start_time >= duration:
                break

    cap.release()
    cv2.destroyAllWindows()


# -------------------------------------------------
# STATIC CAPTURE (REFERENCE POSE)
# -------------------------------------------------
def capture_reference_pose(
    exercise_id: int,
    critical_joints: list,
    angle_map: Dict[str, tuple],
    capture_time: int = 5
) -> Dict[str, Any]:

    cap = cv2.VideoCapture(0)
    start = time.time()
    final_joints = None

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
                final_joints = extract_pose_dictionary(result.pose_landmarks)
                mp_drawing.draw_landmarks(
                    frame,
                    result.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )

            cv2.imshow("Reference Pose Capture", frame)

            if time.time() - start >= capture_time:
                break

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()

    if not final_joints:
        return {"error": "No pose detected"}

    if not validate_visibility(final_joints, critical_joints):
        return {"error": "Critical joints not visible"}

    reference_angles = {}
    for key, (a, b, c) in angle_map.items():
        reference_angles[key] = get_angle(final_joints, a, b, c)

    return {
        "exercise_id": exercise_id,
        "joints": final_joints,
        "reference_angles": reference_angles,
        "captured_at": time.time()
    }


# -------------------------------------------------
# LOCAL TEST
# -------------------------------------------------
if __name__ == "__main__":

    def debug_callback(event):
        print(
            f"[FRAME] angles={event['angles']} "
            f"visibility={event['visibility_ok']}"
        )

    run_live_pose_tracking(
        exercise_id=1,
        critical_joints=["left_elbow", "right_elbow"],
        angle_map={
            "left_elbow": ("left_shoulder", "left_elbow", "left_wrist"),
            "right_elbow": ("right_shoulder", "right_elbow", "right_wrist")
        },
        duration=10,
        callback=debug_callback,
        show_video=True
    )
