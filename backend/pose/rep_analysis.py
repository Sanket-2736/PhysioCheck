def detect_rep_phases(angle_series):
    start_idx = angle_series.index(min(angle_series))
    peak_idx = angle_series.index(max(angle_series))

    end_idx = None
    for i in range(peak_idx + 1, len(angle_series)):
        if abs(angle_series[i] - angle_series[start_idx]) < 5:
            end_idx = i
            break

    if end_idx is None:
        end_idx = len(angle_series) - 1

    return start_idx, peak_idx, end_idx
