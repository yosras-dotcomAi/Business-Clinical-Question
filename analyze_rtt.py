"""NHS RTT Sep 2026: Cardiology and Cardiothoracic Surgery waiting-time baseline.
Reads the cleaned files in data/ and writes one chart to charts/.
Run from the repository root:  python analyze_rtt.py
"""
import pandas as pd
import matplotlib.pyplot as plt

SUMMARY = "data/rtt_national_summary_sep2026.csv"
PROVIDERS = "data/rtt_cardiology_cardiothoracic_sep2026_by_provider.csv"
OUT = "charts/chart_rtt_baseline.png"

nat = pd.read_csv(SUMMARY)
prov = pd.read_csv(PROVIDERS)

# Panel 1: share of pathways waiting over 52 weeks, still waiting vs treated with admission
label = {"Incomplete Pathways": "Still waiting",
         "Completed Pathways For Admitted Patients": "Treated with admission"}
nat["group"] = nat["RTT Part Description"].map(label)
nat["specialty"] = nat["Treatment Function Name"].str.replace(" Service", "", regex=False)
p1 = nat.pivot(index="specialty", columns="group", values="pct_over_52_weeks")[["Still waiting", "Treated with admission"]]

# Panel 2: spread between hospitals, % within 18 weeks (still-waiting pathways, hospitals with 100+ pathways)
inc = prov[(prov.part == "Part_2") & (prov.pathways_total >= 100)].copy()
inc["specialty"] = inc["specialty"].str.replace(" Service", "", regex=False)

fig, ax = plt.subplots(1, 2, figsize=(12, 4.8))
p1.plot(kind="bar", ax=ax[0], rot=0, color=["#4C78A8", "#E45756"])
ax[0].set_title("Pathways waiting over 52 weeks (%)")
ax[0].set_xlabel("")
ax[0].set_ylabel("% of pathways")
ax[0].legend(title="")
for c in ax[0].containers:
    ax[0].bar_label(c, fmt="%.2f", padding=2, fontsize=9)

for name, color in [("Cardiology", "#4C78A8"), ("Cardiothoracic Surgery", "#F58518")]:
    d = inc[inc.specialty == name]
    ax[1].hist(d.pct_within_18_weeks, bins=range(20, 105, 5), alpha=0.7, color=color,
               label=f"{name} (n={len(d)} hospitals)")
ax[1].set_title("Hospitals by % of waiting pathways within 18 weeks")
ax[1].set_xlabel("% within 18 weeks")
ax[1].set_ylabel("Number of hospitals")
ax[1].set_ylim(0, 25)
ax[1].legend(loc="upper left")

fig.suptitle("NHS England RTT, September 2026: Cardiology and Cardiothoracic Surgery", fontsize=12)
fig.text(0.5, 0.005, "Source: NHS England RTT full extract, September 2026. Specialty-level data, not TAVI-specific.",
         ha="center", fontsize=8)
fig.tight_layout(rect=[0, 0.03, 1, 0.95])
fig.savefig(OUT, dpi=150)
print("saved", OUT)
print(p1.round(2))
print(inc.groupby("specialty").pct_within_18_weeks.describe().round(1))
