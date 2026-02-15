from collections import defaultdict
import threading

class MetricsRegistry:

    def __init__(self):
        self.lock = threading.Lock()

        self.total_flows = 0
        self.total_blocks = 0
        self.attack_type_counts = defaultdict(int)
        self.current_drift_score = 0
        self.avg_risk = 0
        self.risk_samples = 0

    def record_flow(self, risk_score):
        with self.lock:
            self.total_flows += 1
            self.risk_samples += 1
            self.avg_risk = (
                (self.avg_risk * (self.risk_samples - 1) + risk_score)
                / self.risk_samples
            )

    def record_block(self):
        with self.lock:
            self.total_blocks += 1

    def record_attack_type(self, attack_type):
        if attack_type != "NONE":
            with self.lock:
                self.attack_type_counts[attack_type] += 1

    def update_drift(self, drift_score):
        with self.lock:
            self.current_drift_score = drift_score

    def export_metrics(self):
        with self.lock:
            lines = []

            lines.append(f"ids_total_flows {self.total_flows}")
            lines.append(f"ids_total_blocks {self.total_blocks}")
            lines.append(f"ids_current_drift_score {self.current_drift_score}")
            lines.append(f"ids_average_risk {round(self.avg_risk,2)}")

            for attack, count in self.attack_type_counts.items():
                lines.append(f'ids_attack_type_total{{type="{attack}"}} {count}')

            return "\n".join(lines)
