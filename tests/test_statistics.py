import numpy as np
from cltd.analysis.statistics import cliffs_delta, bootstrap_median_ci, run_paired_test, holm_bonferroni_correction


def test_cliffs_delta():
    x = np.array([1, 2, 3])
    y = np.array([4, 5, 6])
    # x contains values all smaller than y, so Cliff's delta should be -1.0
    assert cliffs_delta(x, y) == -1.0


def test_bootstrap_median_ci():
    rng = np.random.default_rng(42)
    # Generate some ratios around 1.5
    ratios = rng.normal(loc=1.5, scale=0.1, size=100)
    lower, upper = bootstrap_median_ci(ratios)
    assert 1.4 < lower < 1.6
    assert 1.4 < upper < 1.6
    assert lower <= upper


def test_bootstrap_median_ci_insufficient_data():
    ratios = np.array([1.5, 1.4])
    lower, upper = bootstrap_median_ci(ratios)
    assert np.isnan(lower)
    assert np.isnan(upper)


def test_run_paired_test():
    x = np.array([1] * 25)
    y = np.array([2] * 25)
    p_val = run_paired_test(x, y)
    # p_val should be float and very small (significantly different)
    assert isinstance(p_val, float)
    assert p_val < 0.01


def test_run_paired_test_insufficient_sample():
    x = np.array([1] * 10)
    y = np.array([2] * 10)
    assert run_paired_test(x, y) == "insufficient_sample"


def test_holm_bonferroni_correction():
    # Example p-values: [0.01, 0.04, 0.03, 0.005]
    # Sorted: [0.005, 0.01, 0.03, 0.04] (n=4)
    # Adjusted calculations:
    # i=0: 0.005 * 4 = 0.02
    # i=1: max(0.02, 0.01 * 3) = 0.03
    # i=2: max(0.03, 0.03 * 2) = 0.06
    # i=3: max(0.06, 0.04 * 1) = 0.06
    # Expected in sorted order: [0.02, 0.03, 0.06, 0.06]
    # In original order: [0.03, 0.06, 0.06, 0.02]
    p_vals = [0.01, 0.04, 0.03, 0.005]
    corrected = holm_bonferroni_correction(p_vals)
    expected = np.array([0.03, 0.06, 0.06, 0.02])
    np.testing.assert_allclose(corrected, expected)

    # Empty test
    assert len(holm_bonferroni_correction([])) == 0

