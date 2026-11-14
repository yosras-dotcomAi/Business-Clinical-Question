# Business-Clinical Question: TAVI Access, Capacity and Benchmarking

> **Note on data:** This repository uses **public data only**. No real patient or hospital data is used. Any patient-level data in the TAVI projects is **synthetic** and labelled as such.

| | |
|---|---|
| Live dashboard | [GCC TAVI Market Opportunity Model](https://tavi-gcc-market-opportunity-mode-iy7nxbmcjkkcg6eudp7aud.streamlit.app/) |
| Companion repo | [TAVI-GCC-market-opportunity-mode](https://github.com/yosras-dotcomAi/TAVI-GCC-market-opportunity-mode) |

## The question

**Can a health system treat the patients who need TAVI fast enough, and what limits it: patient demand, the referral pathway, or catheterisation lab capacity?**

This repository is the clinical and business framing layer for the GCC TAVI Opportunity Model. The model estimates how many patients may need TAVI. This repository asks whether a hospital can actually deliver it, and uses mature public NHS data as a benchmark.

## Why it matters (public evidence)

- England performed 7,697 TAVI procedures in 2022/23, about 136 per million people. This is still below Western Europe and the US (141 and 176 per million in 2019). Source: [Geographical Inequality in Access to Aortic Valve Intervention in England](https://pmc.ncbi.nlm.nih.gov/articles/PMC11413983/).
- The same paper cites UK analysis attributing more than 500 avoidable deaths a year to long TAVI waiting lists.
- A UK survey of TAVI centres found cath lab capacity and bed numbers were the most common limits on expansion (74% and 56% of centres). Source: [PMC7996656](https://pmc.ncbi.nlm.nih.gov/articles/PMC7996656).
- An average of about 142 days from referral to procedure in the UK is reported in [Cardiovascular News](https://cardiovascularnews.com/tackling-unacceptable-mortality-in-aortic-stenosis-a-call-to-expand-tavi-access/). This is an advocacy article, so treat it as an estimate, not an official statistic.

## Sub-questions

1. **Volume and growth:** how have TAVI volumes changed compared with surgical aortic valve replacement (SAVR)?
2. **Capacity and waiting:** where is the gap between patients with severe aortic stenosis and lab and bed throughput?
3. **Age and length of stay:** as TAVI moves into lower-risk and younger groups, how does length of stay and resource use change?
4. **Benchmarking:** can UK performance serve as a baseline for readiness in GCC markets, and what does not transfer?

## Data sources

| Source | Used for | Limit |
|---|---|---|
| NHS England Referral to Treatment (RTT) waiting times | Monthly waiting times by specialty and provider (Cardiology, Cardiothoracic Surgery) | Specialty level only, **not TAVI-specific** |
| NICOR UK TAVI Registry (published reports) | TAVI volumes, outcomes, centre activity | Published aggregates, not record-level |
| NHS England Hospital Episode Statistics (HES) | Procedure counts and length of stay | See the coding note below |

**Coding note.** TAVI is not identified by a single OPCS-4 code. NICE coding guidance records TAVI as an aortic valve code in category `K26.-` together with an approach code: `Y79.-` (transluminal) or `Y49.4` (transapical). Surgical aortic valve replacement also sits in `K26.-`, so counting `K26` codes alone mixes the two procedures. See [Bortolussi et al., BMJ Open 2019](https://discovery-pp.ucl.ac.uk/id/eprint/10072218/1/e023316.full.pdf). The related diagnosis code is ICD-10 `I35.0` (aortic valve stenosis). Because public HES tables are aggregated, TAVI volumes in this project are taken from NICOR reports instead.

## Method

1. Define the clinical condition and the procedure (ICD-10 and OPCS-4).
2. Clean and standardise the public NHS files in Python (pandas).
3. Build a national waiting-time baseline from RTT data.
4. Link the baseline to the Opportunity Model and test how demand and capacity assumptions change waiting time.

## Status

- [x] Framing questions and data sources defined
- [x] Companion dashboard live
- [ ] RTT Cardiology and Cardiothoracic baseline added to `data/`
- [ ] Analysis script and charts with results added
- [ ] Results summary added to this README

## Limitations

- RTT data does not isolate TAVI patients.
- The NHS is a single-payer system with a different age structure and funding model from GCC markets, so benchmarks show direction, not forecasts.
- Patient-level pathway data, where used, is synthetic.

## Author

**Yosra El-Naggar**, Nursing Supervisor (Critical Care and Cardiac Catheterization) and Healthcare Data Analyst.
GitHub: [@yosras-dotcomAi](https://github.com/yosras-dotcomAi)
