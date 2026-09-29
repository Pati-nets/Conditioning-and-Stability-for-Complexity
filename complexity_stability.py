# Copyright: Anandi Karunaratne
#
# The function in this file were taken from Anandi Karunaratne's github project
# "Stability Codebase", found at: https://github.com/AnandiKarunaratne/stability_codebase
# The exact file that contains this function can be found under the following link:
# https://github.com/AnandiKarunaratne/stability_codebase/blob/main/Analysis/stability.py
#
# The paper describing the ideas behind this code was published at the International
# Conference on Advanced Information Systems Engineering (CAiSE) 2026 and can be
# found at: https://doi.org/10.1007/978-3-032-28110-4_18

import numpy as np

def stability(dm_values, confidence=0.95, coverage=0.95, n_bootstrap=10000):
    """
    dm_values: your observed dm values
    confidence: 95% confidence
    coverage: want to cover 95% of future observations
    """
    percentile = coverage * 100  # 95th percentile

    bootstrap_percentiles = []
    n = len(dm_values)

    for _ in range(n_bootstrap):
        # Resample with replacement
        sample = np.random.choice(dm_values, size=n, replace=True)
        # Compute the coverage percentile
        p = np.percentile(sample, percentile)
        bootstrap_percentiles.append(p)

    # Upper prediction bound at confidence level
    upper_bound = np.percentile(bootstrap_percentiles, confidence * 100)

    return upper_bound
