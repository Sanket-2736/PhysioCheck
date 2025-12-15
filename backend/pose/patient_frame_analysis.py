def compute_accuracy(angle, min_a, max_a):
    if angle < min_a:
        return max(0, 100 - (min_a - angle))
    if angle > max_a:
        return max(0, 100 - (angle - max_a))
    return 100
