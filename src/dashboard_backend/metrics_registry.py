class MetricsRegistry:

    def __init__(self):
        self.total_flows = 0
        self.total_attacks = 0
        self.total_blocks = 0
        self.drift_score = 0.0
        self.risk_sum = 0.0

    def increment_flows(self):
        self.total_flows += 1

    def increment_attacks(self):
        self.total_attacks += 1

    def increment_blocks(self):
        self.total_blocks += 1

    def update_drift(self, drift):
        self.drift_score = drift

    def update_avg_risk(self, risk):
        self.risk_sum += risk

    def get_stats(self):
        avg_risk = (
            self.risk_sum / self.total_flows
            if self.total_flows > 0 else 0
        )

        return {
            "total_flows": self.total_flows,
            "total_attacks": self.total_attacks,
            "total_blocks": self.total_blocks,
            "drift": round(self.drift_score, 4),
            "avg_risk": round(avg_risk, 2)
        }


# 🔥 Global singleton instance
metrics_registry = MetricsRegistry()
