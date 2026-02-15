class DriftController:

    def __init__(self):
        self.mode = "STABLE"
        self.drift_score = 0.0

    def update(self, drift_score):
        self.drift_score = drift_score

        if drift_score < 0.15:
            self.mode = "STABLE"
        elif drift_score < 0.35:
            self.mode = "ALERT"
        else:
            self.mode = "DEFENSIVE"

        return self.mode

    def get_weights(self):
        D = self.drift_score

        weight_ann = max(0.2, 1 - D)
        weight_anomaly = max(0.2, D)

        total = weight_ann + weight_anomaly
        weight_ann /= total
        weight_anomaly /= total

        return weight_ann, weight_anomaly

    def get_decay_rate(self):
        base_decay = 0.85
        return base_decay * (1 - self.drift_score)

    def get_threshold_adjustment(self):
        if self.mode == "STABLE":
            return 1.0
        elif self.mode == "ALERT":
            return 0.9
        else:
            return 0.75
