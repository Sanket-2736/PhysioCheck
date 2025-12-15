import statistics

def assess_stability(frames):
    if not frames:
        return {"stability": "unknown"}

    variances = []

    for frame in frames:
        if not frame.angles:
            continue

        values = list(frame.angles.values())
        if len(values) > 1:
            variances.append(statistics.pstdev(values))

    if not variances:
        return {"stability": "poor"}

    avg = sum(variances) / len(variances)

    if avg < 3:
        return {"stability": "excellent"}
    elif avg < 6:
        return {"stability": "good"}
    else:
        return {"stability": "poor"}
