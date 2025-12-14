from typing import List, Tuple


def detect_rep_phases(angle_series: List[float], tolerance: float = 5.0) -> Tuple[int, int, int]:
    """
    Detect start, peak, end indices of a single rep.

    Logic:
    - start = minimum angle
    - peak = maximum angle
    - end = return near start after peak
    """

    if len(angle_series) < 10:
        raise ValueError("Not enough frames to detect rep")

    start_angle = min(angle_series)
    peak_angle = max(angle_series)

    start_idx = angle_series.index(start_angle)
    peak_idx = angle_series.index(peak_angle)

    end_idx = None
    for i in range(peak_idx + 1, len(angle_series)):
        if abs(angle_series[i] - start_angle) <= tolerance:
            end_idx = i
            break

    if end_idx is None:
        raise ValueError("End phase not detected")

    return start_idx, peak_idx, end_idx
