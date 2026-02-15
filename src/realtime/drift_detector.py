import numpy as np
from collections import deque

class DriftDetector:

    def __init__(self, window_size=1000, threshold=0.15):
        self.window_size = window_size
        self.threshold = threshold

        self.reference_scores = deque(maxlen=window_size)
        self.current_scores = deque(maxlen=window_size)

        self.drift_score = 0
        self.drift_flag = False

    def update(self, risk_score):

        if len(self.reference_scores) < self.window_size:
            self.reference_scores.append(risk_score)
            return False

        self.current_scores.append(risk_score)

        if len(self.current_scores) == self.window_size:
            self.drift_score = self._calculate_drift()

            if self.drift_score > self.threshold:
                self.drift_flag = True
            else:
                self.drift_flag = False

        return self.drift_flag

    def _calculate_drift(self):

        ref = np.array(self.reference_scores)
        cur = np.array(self.current_scores)

        ref_mean = np.mean(ref)
        cur_mean = np.mean(cur)

        ref_std = np.std(ref) + 1e-6
        cur_std = np.std(cur) + 1e-6

        mean_shift = abs(cur_mean - ref_mean) / ref_std
        std_shift = abs(cur_std - ref_std) / ref_std

        return (mean_shift + std_shift) / 2

    def get_drift_score(self):
        return round(self.drift_score, 4)
