import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import generate_data as gd
import analysis as an


def test_reproducible():
    assert gd.generate(300, seed=1).equals(gd.generate(300, seed=1))


def test_naive_is_biased_and_adjustment_helps():
    res = an.run_all(gd.generate(3000, seed=7))
    e = res["effects"].set_index(["key", "method"])
    for k in ["bmi", "sbp", "hba1c", "ldl"]:
        naive_err = abs(e.loc[(k, "Naive"), "pct_of_true"] - 100)
        adj_err = abs(e.loc[(k, "Adjusted"), "pct_of_true"] - 100)
        assert naive_err > adj_err
        assert adj_err < 15


def test_matching_balances_covariates():
    res = an.run_all(gd.generate(2000, seed=3))
    assert res["smd"]["after"].abs().max() < 0.15
