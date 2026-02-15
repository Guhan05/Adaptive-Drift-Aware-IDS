class BaselineLearner:

    def __init__(self, alpha=0.05):
        """
        alpha = learning rate (small = stable, large = adaptive)
        """
        self.alpha = alpha
        self.feature_means = {}
        self.initialized = False

    def update(self, features_dict):

        if not self.initialized:
            self.feature_means = features_dict.copy()
            self.initialized = True
            return

        for key, value in features_dict.items():

            if key not in self.feature_means:
                self.feature_means[key] = value
                continue

            old_mean = self.feature_means[key]

            # Exponential moving average
            new_mean = (1 - self.alpha) * old_mean + self.alpha * value
            self.feature_means[key] = new_mean

    def get_baseline(self):
        return self.feature_means
