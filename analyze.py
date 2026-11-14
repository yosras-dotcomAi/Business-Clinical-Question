"""Run the full analysis and write tables + charts to outputs/."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import analysis as an

OUT = Path("outputs"); OUT.mkdir(exist_ok=True)
COL = {"Naive": "#d1495b", "Adjusted": "#00798c", "Matched": "#edae49"}


def main(path="data/health_improvement_programs_data.csv"):
    res = an.run_all(an.load_data(path))
    eff = res["effects"]
    eff.round(4).to_csv(OUT / "summary_results.csv", index=False)
    res["table1"].to_csv(OUT / "table1_baseline.csv")
    res["smd"].round(3).to_csv(OUT / "balance_smd.csv", index=False)

    # Chart 1: how much of the TRUE effect each method recovers
    fig, ax = plt.subplots(figsize=(9, 4.8))
    outcomes = list(dict.fromkeys(eff.outcome))
    w = 0.26
    for i, m in enumerate(["Naive", "Adjusted", "Matched"]):
        v = eff[eff.method == m].set_index("outcome").loc[outcomes, "pct_of_true"]
        ax.bar(np.arange(len(outcomes)) + (i - 1) * w, v, w, label=m, color=COL[m])
    ax.axhline(100, color="black", lw=1, ls="--")
    ax.set_xticks(range(len(outcomes)))
    ax.set_xticklabels([o.replace(" (odds ratio)", "\n(odds ratio)").replace(" cholesterol", "\ncholesterol")
                        for o in outcomes], fontsize=8)
    ax.set_ylabel("Estimated effect as % of true effect")
    ax.set_title("Naive comparison overstates the benefit; adjustment and matching recover it")
    ax.legend(); fig.tight_layout(); fig.savefig(OUT / "chart_naive_vs_adjusted.png", dpi=150); plt.close(fig)

    # Chart 2: covariate balance (love plot)
    s = res["smd"].iloc[::-1]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter(s.before, s.covariate, label="Before matching", color=COL["Naive"])
    ax.scatter(s.after, s.covariate, label="After matching", color=COL["Adjusted"])
    ax.axvline(0, color="black", lw=0.8); ax.axvspan(-0.1, 0.1, color="grey", alpha=0.15)
    ax.set_xlabel("Standardised mean difference"); ax.set_title("Covariate balance")
    ax.legend(); fig.tight_layout(); fig.savefig(OUT / "chart_balance.png", dpi=150); plt.close(fig)

    # Chart 3: readmission rates
    r = res["readmit"]
    fig, ax = plt.subplots(figsize=(4.5, 4))
    ax.bar(["Non-participants", "Participants"], [r["rate_non"] * 100, r["rate_part"] * 100],
           color=[COL["Naive"], COL["Adjusted"]])
    ax.set_ylabel("90-day readmission (%)"); ax.set_title("Crude readmission rate")
    fig.tight_layout(); fig.savefig(OUT / "chart_readmission_rate.png", dpi=150); plt.close(fig)

    print(eff[["outcome", "method", "estimate", "lo", "hi", "pct_of_true"]].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
