class RepCounter:
    def __init__(self, min_angle, max_angle):
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.state = "START"
        self.reps = 0

    def update(self, angle: float):
        if self.state == "START" and angle <= self.min_angle:
            self.state = "DOWN"

        elif self.state == "DOWN" and angle >= self.max_angle:
            self.state = "UP"

        elif self.state == "UP" and angle <= self.min_angle:
            self.reps += 1
            self.state = "DOWN"
            return True  # rep completed

        return False
