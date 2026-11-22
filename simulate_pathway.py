"""Synthetic TAVI referral-to-procedure pathway simulation.

All patient-level data here is SYNTHETIC. Parameters are assumptions, not measurements.
The baseline is calibrated so the mean referral-to-procedure time is about 142 days, the
UK estimate reported in Cardiovascular News (an advocacy source, treat as an estimate).

Pathway: referral -> assessment (echo, CT, clinic) -> heart team -> pre-procedure -> TAVI slot.
Each stage has a weekly capacity. Patients are served first come, first served.
Run from the repository root:  python simulate_pathway.py
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---- Assumptions (change these and re-run) -------------------------------------------
REFERRALS_PER_WEEK = 12.0      # about 620 referrals a year: a regional program, not one hospital
CAP_ASSESS = 14.0              # assessment slots per week
CAP_HEART_TEAM = 14.0          # heart team cases per week
CAP_PROCEDURE = 12.5           # TAVI procedure slots per week (the tightest stage, see README)
ASSESS_LAG_WEEKS = 10.6        # mean weeks from assessment slot to heart team readiness (assumption)
PREPROC_LAG_WEEKS = 8.7        # mean weeks from heart team decision to procedure readiness (assumption)
LAG_SHAPE = 4.0                # gamma shape: higher means less spread in stage delays
TARGET_MEAN_DAYS = 142         # published UK estimate used for calibration
WARMUP_WEEKS = 52
GROWTH_START_WEEK = 52         # referral growth begins here in the stress test
HORIZON_WEEKS = 208
WINDOW = (156, 208)            # patients referred in this window are measured in the stress test
REPLICATIONS = 40
RTT_DAYS = 18 * 7              # the 18-week RTT reference used in NHS England waiting-time data


def _serve(ready, cap):
    """FIFO service with a weekly capacity that may be fractional (e.g. 12.5 slots a week)."""
    order = np.argsort(ready, kind="stable")
    out = np.empty_like(ready)
    cw = lambda w: int(np.floor(cap * (w + 1)) - np.floor(cap * w))
    w = int(ready.min())
    avail = cw(w)
    for i in order:
        r = ready[i]
        if r > w:
            w, avail = int(r), cw(int(r))
        while avail <= 0:
            w += 1
            avail = cw(w)
        out[i] = w
        avail -= 1
    return out


def simulate(seed, growth=0.0, extra_slots=0.0, assess_lag_cut=0.0, extra_other=0.0, horizon=HORIZON_WEEKS):
    """One run. growth: extra referral share from GROWTH_START_WEEK.
    extra_slots: added procedure slots a week. extra_other: added weekly capacity at assessment and heart team."""
    rng = np.random.default_rng(seed)
    lam = np.full(horizon, REFERRALS_PER_WEEK)
    lam[GROWTH_START_WEEK:] *= 1 + growth
    arrivals = rng.poisson(lam)
    ref_week = np.repeat(np.arange(horizon), arrivals)
    n = len(ref_week)
    ref_day = ref_week * 7 + rng.integers(0, 7, n)

    a_mean = ASSESS_LAG_WEEKS * (1 - assess_lag_cut)
    lag_a = np.round(rng.gamma(LAG_SHAPE, a_mean / LAG_SHAPE, n)).astype(int)
    lag_p = np.round(rng.gamma(LAG_SHAPE, PREPROC_LAG_WEEKS / LAG_SHAPE, n)).astype(int)

    s_assess = _serve(ref_week, CAP_ASSESS + extra_other)
    s_team = _serve(s_assess + lag_a, CAP_HEART_TEAM + extra_other)
    s_proc = _serve(s_team + lag_p, CAP_PROCEDURE + extra_slots)

    df = pd.DataFrame({
        "referral_week": ref_week,
        "referral_day": ref_day,
        "assessment_day": s_assess * 7 + rng.integers(0, 7, n),
        "heart_team_day": s_team * 7 + rng.integers(0, 7, n),
        "procedure_day": s_proc * 7 + rng.integers(0, 7, n),
    })
    df["wait_days"] = df.procedure_day - df.referral_day
    return df


def summarise(df, lo, hi):
    d = df[(df.referral_week >= lo) & (df.referral_week < hi)].wait_days
    return d.mean(), np.percentile(d, 90), (d > RTT_DAYS).mean() * 100


def main():
    for folder in ("data", "results", "charts"):
        os.makedirs(folder, exist_ok=True)
    # 1. Calibration check: baseline, no growth, steady-state window
    base = [summarise(simulate(s), WARMUP_WEEKS, 156) for s in range(REPLICATIONS)]
    base_mean = np.mean([b[0] for b in base])
    print(f"Baseline mean referral-to-procedure: {base_mean:.0f} days (target {TARGET_MEAN_DAYS})")

    # 2. One synthetic patient-level dataset (baseline, one year of referrals after warm-up)
    one = simulate(seed=2026)
    one = one[(one.referral_week >= WARMUP_WEEKS) & (one.referral_week < WARMUP_WEEKS + 52)].copy()
    one.insert(0, "patient_id", [f"SYN-{i+1:04d}" for i in range(len(one))])
    one["synthetic"] = True
    one = one.drop(columns=["referral_week"])
    one.to_csv("data/synthetic_tavi_pathway_baseline.csv", index=False)

    # 3. Stress test: referral growth x added capacity, procedure slots only vs all three stages
    rows = []
    for growth in [0.0, 0.10, 0.20, 0.30]:
        for scope in ["procedure only", "all three stages"]:
            for extra in [0, 1, 2, 3, 4]:
                kw = {"extra_slots": extra} if scope == "procedure only" else {"extra_slots": extra, "extra_other": extra}
                res = [summarise(simulate(s, growth, **kw), *WINDOW) for s in range(REPLICATIONS)]
                rows.append({"referral_growth_pct": int(growth * 100), "capacity_added_to": scope,
                             "extra_slots_per_week": extra,
                             "mean_wait_days": np.mean([r[0] for r in res]),
                             "p90_wait_days": np.mean([r[1] for r in res]),
                             "pct_waiting_over_18_weeks": np.mean([r[2] for r in res])})
    grid = pd.DataFrame(rows).round(1)

    # 4. Other levers at baseline demand: faster assessment, added assessment capacity is not binding here
    levers = []
    for name, kw in [("Baseline", {}), ("+1 procedure slot a week", {"extra_slots": 1}),
                     ("Assessment 2 weeks faster", {"assess_lag_cut": 2 / ASSESS_LAG_WEEKS}),
                     ("Both", {"extra_slots": 1, "assess_lag_cut": 2 / ASSESS_LAG_WEEKS})]:
        res = [summarise(simulate(s, 0.0, **kw), WARMUP_WEEKS, 156) for s in range(REPLICATIONS)]
        levers.append({"scenario": name, "mean_wait_days": np.mean([r[0] for r in res]),
                       "p90_wait_days": np.mean([r[1] for r in res]),
                       "pct_waiting_over_18_weeks": np.mean([r[2] for r in res])})
    levers = pd.DataFrame(levers).round(1)

    grid.to_csv("results/scenario_stress_test.csv", index=False)
    levers.to_csv("results/scenario_levers.csv", index=False)
    print(levers.to_string(index=False))
    print(grid.pivot_table(index=["capacity_added_to", "extra_slots_per_week"], columns="referral_growth_pct", values="mean_wait_days"))

    # 5. Chart
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.8))
    ax[0].bar(levers.scenario, levers.mean_wait_days, color="#4C78A8")
    ax[0].axhline(TARGET_MEAN_DAYS, ls=":", color="grey")
    ax[0].set_title("Mean referral-to-procedure wait, current demand (days)")
    ax[0].set_ylabel("days")
    ax[0].tick_params(axis="x", rotation=15)
    for i, v in enumerate(levers.mean_wait_days):
        ax[0].text(i, v + 1, f"{v:.0f}", ha="center", fontsize=9)
    for g, color in zip([10, 20, 30], ["#F58518", "#E45756", "#72B7B2"]):
        for scope, ls in [("procedure only", "-"), ("all three stages", "--")]:
            d = grid[(grid.referral_growth_pct == g) & (grid.capacity_added_to == scope)]
            ax[1].plot(d.extra_slots_per_week, d.mean_wait_days, ls=ls, marker="o", color=color,
                       label=f"+{g}% referrals, {scope}")
    ax[1].set_title("Wait when referrals grow, by capacity added (2 years after growth begins)")
    ax[1].set_xlabel("Added slots per week")
    ax[1].set_ylabel("Mean wait (days)")
    ax[1].set_xticks([0, 1, 2, 3, 4])
    ax[1].legend(fontsize=8)
    fig.suptitle("Synthetic TAVI pathway simulation (assumption-based, not real patient data)", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig("charts/chart_pathway_scenarios.png", dpi=150)


if __name__ == "__main__":
    main()
