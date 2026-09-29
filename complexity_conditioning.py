# Copyright: Anandi Karunaratne
#
# The two functions in this file were taken from Anandi Karunaratne's github project
# "Stability Codebase", found at: https://github.com/AnandiKarunaratne/stability_codebase
# The exact file that contains these functions can be found under the following link:
# https://github.com/AnandiKarunaratne/stability_codebase/blob/main/Analysis/conditioning.py
#
# The paper describing the ideas behind this code was published at the International
# Conference on Advanced Information Systems Engineering (CAiSE) 2026 and can be
# found at: https://doi.org/10.1007/978-3-032-28110-4_18

import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np

def assess_conditioning(df, validation_split=0.3, random_state=42):
    """
    Assess algorithmic conditioning from empirical measurements.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with columns 'dm' (model distance) and 'dl' (log distance)
    validation_split : float
        Fraction of data to hold out for validation
    random_state : int
        Random seed for reproducibility

    Returns:
    --------
    dict with conditioning estimates and diagnostics
    """

    # Remove rows where dl is zero (no perturbation)
    df_filtered = df[df['dl'] > 0].copy()

    # Calculate local conditioning numbers
    df_filtered['kappa'] = df_filtered['dm'] / df_filtered['dl']

    # Split into estimation and validation sets
    df_est, df_val = train_test_split(
        df_filtered,
        test_size=validation_split,
        random_state=random_state
    )

    # Step 4: Aggregation on estimation set
    kappa_hat = df_est['kappa'].max()
    kappa_50 = df_est['kappa'].quantile(0.50)
    kappa_90 = df_est['kappa'].quantile(0.90)
    kappa_95 = df_est['kappa'].quantile(0.95)

    # Check if conditioning is input-dependent
    stability_ratio = kappa_95 / kappa_50 if kappa_50 > 0 else np.inf
    is_stable = stability_ratio <= 10

    # Step 5: Validation
    kappa_hat_val = df_val['kappa'].max()
    relative_error = abs(kappa_hat_val - kappa_hat) / kappa_hat if kappa_hat > 0 else np.inf
    validation_passed = relative_error < 0.5

    # Interpretation
    if kappa_hat < 2:
        interpretation = "well-conditioned"
    elif kappa_hat <= 10:
        interpretation = "moderately conditioned"
    else:
        interpretation = "ill-conditioned"

    # Compile results
    results = {
        # Primary estimate
        'kappa_hat': kappa_hat,

        # Distribution statistics
        'kappa_median': kappa_50,
        'kappa_90': kappa_90,
        'kappa_95': kappa_95,
        'stability_ratio': stability_ratio,
        'is_input_stable': is_stable,

        # Validation
        'kappa_hat_validation': kappa_hat_val,
        'relative_error': relative_error,
        'validation_passed': validation_passed,

        # Interpretation
        'interpretation': interpretation,

        # Sample sizes
        'n_estimation': len(df_est),
        'n_validation': len(df_val),
    }

    return results

def print_conditioning_report(results):
    """Pretty print conditioning assessment results."""
    print("=" * 60)
    print("ALGORITHMIC CONDITIONING ASSESSMENT")
    print("=" * 60)

    print(f"\n📊 AGGREGATION")
    print(f"  Conditioning estimate (κ̂): {results['kappa_hat']:.3f}")
    print(f"  Median conditioning (κ₅₀): {results['kappa_median']:.3f}")
    print(f"  90th percentile (κ₉₀):    {results['kappa_90']:.3f}")
    print(f"  95th percentile (κ₉₅):    {results['kappa_95']:.3f}")
    print(f"  Stability ratio (κ₉₅/κ₅₀): {results['stability_ratio']:.2f}")

    if results['is_input_stable']:
        print(f"  ✓ Conditioning is INPUT-STABLE (ratio ≤ 10)")
        print(f"    → Report: κ̂ = {results['kappa_hat']:.3f}")
    else:
        print(f"  ✗ Conditioning is INPUT-DEPENDENT (ratio > 10)")
        print(f"    → Report range: κ₅₀ = {results['kappa_median']:.3f}, κ̂ = {results['kappa_hat']:.3f}")

    print(f"\n🔬 VALIDATION")
    print(f"  Validation estimate:  {results['kappa_hat_validation']:.3f}")
    print(f"  Relative error:       {results['relative_error']:.2%}")
    print(f"  Sample sizes:         n_est={results['n_estimation']}, n_val={results['n_validation']}")

    if results['validation_passed']:
        print(f"  ✓ VALIDATION PASSED (error < 50%)")
    else:
        print(f"  ✗ VALIDATION FAILED (error ≥ 50%)")
        print(f"    → Expand log diversity and re-assess")

    print(f"\n📋 INTERPRETATION")
    print(f"  Algorithm is: {results['interpretation'].upper()}")
    print("=" * 60)
