"""Streamlit dashboard: Health Improvement Program analysis (synthetic data)."""
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

import analysis as an
import generate_data as gd

st.set_page_config(page_title="HIP Analysis", page_icon="🩺", layout="wide")
DATA = Path(__file__).parent / "data" / "health_improvement_programs_data.csv"
COLORS = {"Naive": "#d1495b", "Adjusted": "#00798c", "Matched": "#edae49"}


@st.cache_data
def load():
    df = pd.read_csv(DATA) if DATA.exists() else gd.generate(n=2000)
    return an.add_changes(df)


@st.cache_data
def analyse(df):
    return an.run_all(df)


df = load()

# ---------- sidebar filters ----------
st.sidebar.header("Filters")
depts = st.sidebar.multiselect("Department", gd.DEPARTMENTS, default=gd.DEPARTMENTS)
genders = st.sidebar.multiselect("Gender", ["Female", "Male"], default=["Female", "Male"])
amin, amax = int(df.age.min()), int(df.age.max())
age_rng = st.sidebar.slider("Age range", amin, amax, (amin, amax))
f = df[df.department.isin(depts) & df.gender.isin(genders) & df.age.between(*age_rng)]
st.sidebar.caption(f"{len(f):,} of {len(df):,} patients selected")
st.sidebar.info("All data are **synthetic**, generated for methodology demonstration. "
                "No real patient data is used.")

st.title("🩺 Health Improvement Program: Impact Analysis")
st.caption("Does program participation reduce risk markers and readmissions, "
           "and how much do naive comparisons mislead us?")

if len(f) < 100 or f.participant.nunique() < 2 or f.participant.value_counts().min() < 30:
    st.warning("Selection too small for a reliable analysis. Widen the filters.")
    st.stop()

res = analyse(f.reset_index(drop=True))
eff = res["effects"]

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Overview", "Outcomes", "Bias Lab", "Adherence", "Data"])

# ---------- Overview ----------
with tab1:
    r = res["readmit"]
    c = st.columns(5)
    c[0].metric("Patients", f"{len(f):,}")
    c[1].metric("Participants", f"{int(f.participant.sum()):,}")
    c[2].metric("Readmission (participants)", f"{r['rate_part']*100:.1f}%")
    c[3].metric("Readmission (non-participants)", f"{r['rate_non']*100:.1f}%",
                delta=f"{(r['rate_part']-r['rate_non'])*100:.1f} pts (crude)", delta_color="inverse")
    c[4].metric("Avg adherence", f"{f.adherence_pct.mean():.0f}%")

    left, right = st.columns(2)
    grp = f.assign(Group=f.participant.map({1: "Participants", 0: "Non-participants"}))
    left.plotly_chart(px.histogram(grp, x="comorbidity_score", color="Group", barmode="overlay",
                                   opacity=0.6, nbins=40,
                                   title="Participants were healthier at the start (selection bias)",
                                   labels={"comorbidity_score": "Comorbidity score"}),
                      width="stretch")
    right.plotly_chart(px.histogram(grp, x="department", color="Group", barmode="group",
                                    title="Enrolment by department"), width="stretch")
    st.markdown("**Baseline characteristics**")
    st.dataframe(res["table1"], width="stretch")
    st.caption("A gap in baseline comorbidity means a raw comparison is not like-for-like. "
               "See the Bias Lab tab.")

# ---------- Outcomes ----------
with tab2:
    key = st.selectbox("Outcome", list(an.METRICS), format_func=lambda k: an.METRICS[k])
    lab = an.METRICS[key]
    a, b = st.columns([3, 2])
    a.plotly_chart(px.box(grp, x="Group", y=f"{key}_change", color="Group", points="outliers",
                          labels={f"{key}_change": f"Change in {lab}"},
                          title=f"Change from baseline: {lab}"), width="stretch")
    sub = eff[eff.key == key].copy()
    sub["95% CI"] = sub.apply(lambda r: f"{r.lo:.2f} to {r.hi:.2f}", axis=1)
    b.markdown("**Estimated program effect** (participants minus non-participants)")
    b.dataframe(sub[["method", "estimate", "95% CI", "p"]].round(3).set_index("method"),
                width="stretch")
    b.caption(f"Planted true effect: {sub.true.iloc[0]:.2f}")
    st.markdown("**Readmission, 90 days (odds ratio, below 1 = fewer readmissions)**")
    ro = eff[eff.key == "readmit"].copy()
    ro["95% CI"] = ro.apply(lambda r: f"{r.lo:.2f} to {r.hi:.2f}", axis=1)
    st.dataframe(ro[["method", "estimate", "95% CI", "p", "p_holm"]].round(4).set_index("method"),
                 width="stretch")
    st.caption("Naive = raw comparison. Adjusted = regression on age, gender, department, "
               "comorbidity and baseline value. Matched = 1:1 propensity-score matching. "
               "p_holm is the Holm-corrected p-value across the five adjusted tests.")

# ---------- Bias Lab ----------
with tab3:
    st.subheader("Bias Lab: how selection bias distorts results")
    st.write("Regenerate the synthetic cohort with different amounts of confounding. "
             "The true program effect is fixed, so you can see how far each method lands from it.")
    k1, k2, k3 = st.columns(3)
    n = k1.slider("Cohort size", 500, 5000, 2000, step=500)
    sel = k2.slider("Selection strength (0 = random enrolment)", 0.0, 1.5, 0.7, step=0.1)
    drift = k3.slider("Natural worsening in sicker patients", 0.0, 0.5, 0.25, step=0.05)
    sim = gd.generate(n=n, seed=42, selection_strength=sel, drift=drift)
    sres = an.run_all(an.add_changes(sim))
    se = sres["effects"]
    fig = px.bar(se, x="outcome", y="pct_of_true", color="method", barmode="group",
                 color_discrete_map=COLORS,
                 labels={"pct_of_true": "% of true effect recovered", "outcome": ""},
                 title="100% = unbiased")
    fig.add_hline(y=100, line_dash="dash")
    st.plotly_chart(fig, width="stretch")
    naive_bias = se[(se.method == "Naive") & (se.key != "readmit")].pct_of_true.mean() - 100
    adj_bias = se[(se.method == "Adjusted") & (se.key != "readmit")].pct_of_true.mean() - 100
    st.info(f"Average bias on the continuous outcomes: naive {naive_bias:+.0f}%, "
            f"adjusted {adj_bias:+.0f}%.")
    st.markdown("**Covariate balance before and after matching**")
    st.dataframe(sres["smd"].round(2).set_index("covariate"), width="stretch")
    st.caption("A standardised mean difference within ±0.1 is generally considered balanced.")

# ---------- Adherence ----------
with tab4:
    p = f[f.participant == 1]
    m = st.selectbox("Outcome", list(an.METRICS), format_func=lambda k: an.METRICS[k], key="ad")
    st.plotly_chart(px.scatter(p, x="adherence_pct", y=f"{m}_change", trendline="ols", opacity=0.4,
                               labels={"adherence_pct": "Program adherence (%)",
                                       f"{m}_change": f"Change in {an.METRICS[m]}"},
                               title="Dose-response: higher adherence, larger improvement?"),
                    width="stretch")
    st.caption("A dose-response pattern strengthens the case that the program drives the change, "
               "though it does not prove causation on its own.")

# ---------- Data ----------
with tab5:
    st.dataframe(f.drop(columns=[c for c in f.columns if c.endswith("_change")]),
                 width="stretch", height=400)
    st.download_button("Download filtered data (CSV)", f.to_csv(index=False).encode(),
                       "hip_filtered.csv", "text/csv")
