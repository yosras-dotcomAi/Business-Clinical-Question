# 🫀 Business-Clinical Question: TAVI Market Opportunity & Public Data Benchmarking

## 📌 Overview
This repository serves as the **Clinical & Business Framing Layer** for the **TAVI Market Opportunity Engine**. It bridges clinical cardiovascular realities with healthcare business intelligence by defining core strategic questions, clinical coding standards, and public benchmarking methodologies.

🔗 **Connected Dashboard:** [TAVI-GCC Market Opportunity Model](https://github.com/yosras-dotcomAi/TAVI-GCC-market-opportunity-mode) *(Update with your live Streamlit URL if applicable)*

---

## 🎯 Core Business-Clinical Questions
To evaluate Transcatheter Aortic Valve Implantation (TAVI) adoption, procedural capacity, and unmet patient demand, this project investigates:
1. **Procedural Volume & Growth:** How have TAVI procedure volumes scaled over time compared to Surgical Aortic Valve Replacement (SAVR)?
2. **Capacity & Waitlist Bottlenecks:** What is the gap between diagnosed severe aortic stenosis prevalence and actual catheterization lab throughput?
3. **Age & Demographic Shifts:** How is the expansion of TAVI into intermediate- and low-risk patient cohorts shifting hospital resource allocation and length of stay (LOS)?
4. **Benchmarking & Market Penetration:** How can mature, publicly reported healthcare systems (such as the UK NHS) serve as a baseline model for forecasting market penetration and procedural readiness in emerging/GCC healthcare markets?

---

## 📊 Public Data Source: NHS England & NICOR
To ensure reproducibility, transparency, and zero licensing barriers, this analysis utilizes free, publicly available datasets from the **UK National Health Service (NHS)**:

* **NHS England – Hospital Episode Statistics (HES) / Admitted Patient Care:**
  * Provides annual procedural counts, patient age distributions, and average Length of Stay (LOS).
  * **OPCS-4 Clinical Codes Tracked:**
    * `K26.2` / `K26.3` – Transcatheter implantation of aortic valve (TAVI)
    * `K26.1` – Open surgical replacement of aortic valve (SAVR) for comparative baseline
* **NICOR (National Institute for Cardiovascular Outcomes Research) – UK TAVI Registry:**
  * Public annual audit reports detailing procedural trends, mortality outcomes, hospital center volumes, and transcatheter valve utilization rates.
* **NHS Reference Costs / National Cost Collection:**
  * Used to benchmark procedural reimbursement tariffs and hospital resource utilization.

---

## 🔄 Methodology & Architecture
1. **Clinical Definition & Coding:** Mapping clinical indications (Severe Aortic Stenosis — ICD-10 `I35.0`) to procedural intervention codes (OPCS-4 / CPT).
2. **ETL & Data Normalization:** Cleaning and standardizing public NHS CSV/Excel releases using **Python (Pandas)** and **Power Query**.
3. **Opportunity Modeling:** Calculating penetration rates per million population and applying growth multipliers to simulate regional demand in the connected Streamlit dashboard.

---

## 🛠️ Tech Stack
* **Data Processing & Analysis:** Python (Pandas, NumPy), SQL, Power Query
* **Clinical Standards:** ICD-10, OPCS-4, CPT
* **Visualization & App Deployment:** Streamlit, Power BI

---

## 👩‍⚕️ Author
**Yosra El-Naggar (م. يسرا النجار)**  
*Nursing Supervisor (Critical Care & Cardiac Catheterization) | Healthcare Data Analyst*  
*Host of **Beyond Nursing** Podcast*  

* **GitHub:** [@yosras-dotcomAi](https://github.com/yosras-dotcomAi)
* **Podcast & Website:** [beyondnursingyn.com](https://beyondnursingyn.com)
