import numpy as np

class FeatureExplainer:

    def __init__(self, baseline_means):
        self.baseline = baseline_means

    def explain(self, features):

        contributions = []

        for key, value in features.items():
            if key in self.baseline:
                deviation = abs(value - self.baseline[key])

                if deviation > self.baseline[key] * 0.5:
                    contributions.append((key, round(deviation, 2)))

        contributions.sort(key=lambda x: x[1], reverse=True)

        return contributions[:3]
