# CRM Analytics — Online IT School

End-to-end analytics of a CRM dataset for an online programming school: data cleaning, exploratory analysis, funnel and channel performance, sales-manager and product analysis, unit economics, and A/B-test design — delivered as an interactive Dash dashboard.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![pandas](https://img.shields.io/badge/pandas-2.2-150458)
![Dash](https://img.shields.io/badge/Dash-2.18-119DFF)
![Plotly](https://img.shields.io/badge/Plotly-5.24-3F4F75)

---

## 🔗 Live Dashboard

**[View the interactive dashboard →](https://crm-analytics-dashboard-wr1f.onrender.com)**

> Hosted on a free tier — the first load may take ~30–50 seconds to wake the service.

<!-- Add screenshot here once deployed: -->
<!-- ![Dashboard preview](assets/dashboard.png) -->

---

## Key Results

- **839 confirmed paying customers** out of 21,593 deals over 12 months (Jul 2023 – Jun 2024).
- **5.17% conversion rate** on closed deals.
- **~90% of lost deals are not about the product** — they trace back to lead generation and follow-up (unreachable leads, invalid numbers, unqualified or duplicate leads), not to product objections.
- **Digital Marketing is the flagship**: €2.24M revenue (~63% of total), LTV/CPA ≈ 15.
- All three main products are profitable: LTV/CPA of 14.9 (DM), 6.3 (UX/UI), 2.6 (Web Developer).

---

## Business Problem

The school runs paid and organic acquisition across 13 channels but lacks a clear view of where deals are actually lost, which channels and managers convert best, and whether each product line is economically sound. The goal of this project is to clean the raw CRM exports, quantify the funnel end to end, and turn the findings into concrete, testable growth hypotheses.

*Note: this is a final certification project. The "client" is a training scenario; all methodological decisions were made independently as the analyst.*

---

## Data

Four raw Excel exports, cleaned into Parquet:

| Source | Rows | Role in analysis |
|---|---|---|
| Deals | 21,593 | Main table — funnel, products, managers, revenue |
| Calls | 95,874 | Contact attempts, linked to deals via Contact ID |
| Spend | 19,862 | Ad spend by channel/campaign — total budget €149,523 |
| Contacts | 18,548 | Unique-contact reference for unit economics |

Cleaning preserves anomalies as **boolean flags** (`is_duplicate_lead`, `is_outlier_contact`, `is_closing_date_anomaly`) rather than deleting rows — keeping the dataset transparent and auditable.

---

## Pipeline

```
Raw Excel → Cleaning → EDA → Funnel & Channels → Managers → Products & Payments → Unit Economics → A/B Hypotheses → Dashboard
```

Each notebook documents its methodological decisions in markdown alongside the code.

---

## Key Findings

**Funnel.** Of all deals, 73% are Lost, 23% In Progress, 4% Won. Breaking down the loss reasons shows roughly half are lost at the contact stage (no answer, invalid number) and about a fifth are unqualified or duplicate leads — only ~10% are genuine product objections.

**Lead quality.** Quality-A leads are far more likely to convert (a small share of volume drives a large share of wins), while the lowest-quality tiers (the majority of inbound leads) convert at essentially zero — confirming that stricter qualification would sharpen the funnel.

**Channels.** Organic and webinar channels convert above paid channels: paid sources drive most of the *volume* but convert *below* organic. The worst paid channel by conversion is TikTok Ads.

**Managers.** Performance varies widely. Top performers combine high volume with strong conversion; a small premium-segment manager shows an exceptionally high conversion rate on a low lead count and high average order value — worth studying as a repeatable pattern.

**Products & payments.** Digital Marketing is the revenue flagship (~63% of revenue). The more expensive the course, the more customers choose installment (recurring) payments over one-time payment.

**Unit economics** (functional-programming approach, no consolidated table):

| Metric | Digital Marketing | UX/UI Design | Web Developer |
|---|---|---|---|
| Buyers (B) | 474 | 228 | 137 |
| C1 | 2.62% | 1.26% | 0.76% |
| AOV (per month) | €771.78 | €801.41 | €764.95 |
| LTV | €123.60 | €51.84 | €21.36 |
| Margin profit | €2.09M | €788k | €237k |
| LTV / CPA | 14.9 | 6.3 | 2.6 |

**A/B-test design — honest constraint.** Given the low base conversion (0.76–2.62%) and limited lead flow per product, classic A/B tests on C1 would require from ~5 months (Web Developer) to ~4 years (Digital Marketing) to reach significance. Rather than inflate the numbers, the project documents this conflict openly and recommends starting with the fastest test (Web Developer) and using quasi-experiments where a clean A/B test is infeasible.

---

## Tech Stack

- **Python 3.13**, pandas, NumPy
- **matplotlib** (notebook charts), **Plotly** (dashboard)
- **Dash** + dash-bootstrap-components (interactive dashboard)
- **PyArrow** (Parquet I/O)
- **Jupyter** (VS Code), **Git/GitHub**

---

## Repository Structure

```
crm-analytics-project_en/
├── data/
│   └── processed/          # cleaned datasets (.parquet)
├── notebooks/              # cleaning → EDA → analysis → unit economics
├── dashboard/
│   ├── app.py              # entry point: filters, KPIs, tabs
│   ├── data_loader.py      # cached parquet loader + filter helper
│   ├── theme.py            # colors, fonts, shared plotly layout
│   ├── tabs/               # Funnel & Channels, Sales Managers, Products & Payments
│   └── requirements.txt
└── README.md
```

---

## Run Locally

```bash
# from repo root
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r dashboard/requirements.txt

python dashboard/app.py
# open http://127.0.0.1:8050
```

The dashboard reads the processed Parquet files from `data/processed/`.

---

## Notes on Data Privacy

Raw client exports are **not** published — only cleaned, processed datasets are committed for reproducibility. The dataset is a training set with no confidential information, and manager names are fictitious (replaced with placeholder names).
