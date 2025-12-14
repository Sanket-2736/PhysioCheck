from typing import List, Dict
import statistics


def compute_joint_jitter(values: List[float]) -> float:
    """
    Average frame-to-frame change.
    Lower = more stable.
    """
    if len(values) < 2:
        return 0.0

    diffs = [
        abs(values[i] - values[i - 1])
        for i in range(1, len(values))
    ]
    return round(sum(diffs) / len(diffs), 3)


def assess_stability(frames: List[Dict]) -> Dict:
    """
    Computes stability metrics across frames.

    Returns:
    {
      "overall": float,
      "perJoint": { joint: jitter }
    }
    """

    joint_series = {}

    for frame in frames:
        for joint, angle in frame.get("angles", {}).items():
            joint_series.setdefault(joint, []).append(angle)

    per_joint = {
        joint: compute_joint_jitter(series)
        for joint, series in joint_series.items()
        if len(series) > 3
    }

    overall = (
        round(statistics.mean(per_joint.values()), 3)
        if per_joint else 0.0
    )

    return {
        "overall": overall,
        "perJoint": per_joint
    }
