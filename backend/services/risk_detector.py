class RiskDetector:

    @staticmethod
    def detect(joint_angles, velocity):
        alerts = []

        if joint_angles["knee"] > 175:
            alerts.append("Knee hyperextension risk")

        if joint_angles["spine"] > 40:
            alerts.append("Excessive spine bending")

        if velocity > 2.5:
            alerts.append("Jerky movement detected")

        return alerts
