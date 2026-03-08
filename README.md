# DEGO Project - Team 6

---

## Team Members
- Mariana Cabral Sacadura Campos Lopes | Data Scientist
- Konstantin Titze | Product Lead
- Leonor de Albuquerque Mateus Manso | Governance Officer
- Riccardo Giuliano Bertolini | Data Engineer

---

## Project Description
Credit scoring bias analysis for DEGO course.

---

## Executive Summary

This project audits a dataset of 502 historical credit applications from NovaCred, a fictional fintech startup under regulatory scrutiny for potential discrimination in its lending practices. Acting as a Data Governance Task Force, we analyzed the data across three dimensions: **data quality**, **algorithmic bias**, and **privacy & GDPR compliance**.

Our analysis uncovered significant data quality issues—including duplicate records, inconsistent encodings, and schema drift—as well as statistically significant gender and age-based disparities in loan approval rates. The gender Disparate Impact ratio (0.767) falls below the 0.80 four-fifths threshold, providing evidence of potential discrimination. Multiple PII fields are stored in plain text without any protection, in direct violation of GDPR principles.

We propose a set of concrete governance interventions to bring NovaCred into compliance with the GDPR and the EU AI Act.

---

## Repository Structure

```
project-team6/
├── README.md                        # This file
├── data/
│   ├── raw_credit_applications.json # Original dataset (do not modify)
│   └── credit_applications_clean.csv# Cleaned dataset (output of notebook 01)
├── notebooks/
│   ├── 01-data-quality.ipynb        # Data cleaning and quality assessment
│   ├── 02-bias-analysis.ipynb       # Bias detection and fairness metrics
│   └── 03-privacy-demo.ipynb        # PII identification, pseudonymization, GDPR mapping
└── src/
    └── fairness_utils.py            # Reusable fairness metric functions
```

---

## 1. Data Quality Findings

**Notebook:** *01-data-quality.ipynb* | **Role:** Riccardo Giuliano Bertolini (Data Engineer)

The raw dataset (502 records, 21 columns after JSON flattening) was audited across five data quality dimensions.

### 1.1 Completeness

| Issue | Affected Records | Action Taken |
|-------|-----------------|--------------|
| *notes* field: 99.6% missing | 500/502 | Dropped — no analytical value |
| *financials.annual_salary* vs *financials.annual_income*: mutually exclusive fields (same concept, different names) | 5 records with salary only | Merged into *annual_income*, dropped *annual_salary* |
| *loan_purpose*: 90% missing | ~452 | Retained but excluded from analysis |
| *processing_timestamp*: 88% missing | ~441 | Retained but excluded from analysis |
| *decision.rejection_reason*: 58% missing | ~291 | Expected (only rejected loans have reasons) |
| *decision.approved_amount* / *decision.interest_rate*: 42% missing | ~211 | Expected (only approved loans have these) |

After merging, *financials.annual_income* had 0 missing values.

### 1.2 Consistency

- **Numeric type mismatches:** *financials.annual_income*, *debt_to_income*, *savings_balance*, *credit_history_months*, *approved_amount*, and *interest_rate* were stored as *object* (string) type in parts of the dataset. All were coerced to numeric using *pd.to_numeric* with safe coercion; no new nulls were introduced.
- **Gender encoding:** Four variants found — *Male*, *Female*, *M*, *F* — plus 2 blank strings and 1 *NaN*. Standardized to *Male*/*Female*; 3 records set to *NaN*.
- **Date format inconsistency:** *applicant_info.date_of_birth* contained mixed formats (e.g., *YYYY-MM-DD* and *DD/MM/YYYY*). Parsed with *pd.to_datetime(..., errors='coerce')*.

### 1.3 Validity

- **Negative credit history months:** Some records contained negative values for *financials.credit_history_months*, which is logically impossible. Flagged and investigated.
- **Invalid income values:** String-formatted numbers and outliers identified during numeric coercion.

### 1.4 Uniqueness

- Duplicate records were identified and investigated. The dataset contains intentional duplicates that were detected and removed during the cleaning process.

### 1.5 Accuracy — Spending Behavior Note

All 502 records contain a *spending_behavior* array covering categories including Rent, Shopping, Fitness, Entertainment, Alcohol, Gambling, and Adult Entertainment. This field was **excluded from all predictive analysis** due to its potential to act as a socioeconomic proxy for protected characteristics (e.g., race, gender), which would create downstream fairness and governance risks under both GDPR and the EU AI Act.

---

## 2. Bias Analysis

**Notebook:** *02-bias-analysis.ipynb* | **Role:** Mariana Cabral Sacadura Campos Lopes (Data Scientist)

### 2.1 Gender Disparate Impact

| Group | Approval Rate |
|-------|--------------|
| Male | 65.99% |
| Female | 50.60% |
| **Disparate Impact ratio** | **0.767** |

A DI ratio below **0.80** indicates potential disparate impact under the four-fifths rule. The observed ratio of **0.767** falls below this threshold. A chi-square test of independence confirmed the association is statistically significant (χ²(1) = 11.50, **p = 0.00069**), indicating the gender gap is highly unlikely to be due to random chance.

### 2.2 Age-Based Disparities

| Age Group | Approval Rate |
|-----------|--------------|
| 18–25 | ~40% |
| 26–30 | ~46% |
| 31–40 | ~56% |
| 41–50 | ~71% |
| 51–60 | ~59% |
| 61–70 | ~71% |

The DI ratio comparing the least-favored group (18–25) to the most-favored group (41–50) is approximately **0.565**, well below 0.80. A chi-square test confirmed statistical significance (χ²(5) = 13.62, **p = 0.013**). Younger applicants are systematically less likely to be approved regardless of financial profile.

### 2.3 Intersectional Effects (Age × Gender)

Intersectional analysis explored whether the combined effect of age and gender produced additional disparities beyond either dimension alone. Young female applicants (18–25) showed the lowest approval rates in the dataset, suggesting compounding disadvantage.

### 2.4 Proxy Discrimination Analysis

*applicant_info.zip_code* was investigated as a potential proxy for protected characteristics (e.g., race or ethnicity via residential segregation patterns). Geographic attributes can reproduce discrimination even when protected features are excluded from the model. Correlations between zip code, approval outcomes, and applicant demographics were examined and documented.

---

## 3. Privacy & Governance Assessment

**Notebook:** *03-privacy-demo.ipynb* | **Role:** Leonor de Albuquerque Mateus Manso (Governance Officer)

### 3.1 PII Identified

| Field | Risk Level | GDPR Basis |
|-------|-----------|------------|
| *applicant_info.full_name* | High | Direct identifier |
| *applicant_info.email* | High | Direct identifier |
| *applicant_info.ssn* | **Critical** | Unique national identifier |
| *applicant_info.ip_address* | Medium | Indirect identifier (GDPR Art. 4) |
| *applicant_info.date_of_birth* | Medium | Enables re-identification |

All five fields are stored in **plain text** in the raw dataset without any technical protection measures, violating GDPR Article 32(1)(a).

### 3.2 Pseudonymization Demonstration

Two techniques were demonstrated:

1. **SHA-256 hashing with salt** applied to email addresses — irreversible but consistent, preventing rainbow table attacks.
2. **UUID tokenization** applied to SSNs — reversible with a secure mapping table stored separately from the pseudonymized dataset.

A sanitized dataset was produced by dropping *full_name*, *email*, and *ssn* and retaining only pseudonymized versions. Note: pseudonymized data remains personal data under GDPR (Recital 26).

### 3.3 GDPR Compliance Gaps

| GDPR Article | Principle | Gap Identified |
|---|---|---|
| Art. 5(1)(c) | Data minimisation | IP addresses, SSNs, and detailed spending behavior collected without clear necessity for credit scoring |
| Art. 5(1)(e) | Storage limitation | No data retention policy defined; records appear to be stored indefinitely |
| Art. 6(1)(a) | Lawful basis | No consent tracking mechanism present in the dataset |
| Art. 17 | Right to erasure | No audit trail or deletion mechanism documented |
| Art. 32(1)(a) | Security of processing | PII stored in plain text; no encryption or pseudonymization applied |

### 3.4 EU AI Act Classification

Credit scoring systems fall under **Annex III – High-Risk AI Systems** of the EU AI Act. This classification imposes obligations including: mandatory human oversight, conformity assessments, transparency to affected individuals, and registration in the EU database of high-risk AI systems. NovaCred's current setup shows no evidence of human oversight documentation or audit trails for individual decisions.

---

## 4. Governance Recommendations

Based on the analysis above, we recommend the following interventions for NovaCred:

1. **Implement a fairness-aware model pipeline.** Retrain the credit scoring model with fairness constraints (e.g., demographic parity or equalized odds). Use *fairlearn* to monitor DI and Demographic Parity Difference at each model update.

2. **Introduce human oversight for borderline decisions.** Flag applications near the decision boundary (e.g., model confidence < 70%) for mandatory human review, as required under the EU AI Act for high-risk systems.

3. **Establish a data retention policy.** Define maximum retention periods per field category (e.g., 5 years for approved applications, 1 year for rejected applications) in line with GDPR Art. 5(1)(e).

4. **Pseudonymize PII at ingestion.** Apply SHA-256 hashing to email addresses and UUID tokenization to SSNs before data enters any analytical pipeline. Store mapping tables in isolated, access-controlled infrastructure.

5. **Remove or justify high-risk fields.** Assess whether *ssn*, *ip_address*, and sensitive spending categories (Alcohol, Gambling, Adult Entertainment) are strictly necessary under GDPR Art. 5(1)(c). If not, remove from collection.

6. **Create an audit trail.** Log every automated decision with a timestamp, model version, key input features (anonymized), and outcome. This supports both GDPR accountability (Art. 5(2)) and EU AI Act auditability requirements.

7. **Implement a consent management mechanism.** Capture and store explicit, documented consent at application time, including purpose specification, as required by GDPR Art. 6 and Art. 7.

8. **Conduct periodic bias audits.** Schedule quarterly DI and statistical parity checks for all protected attributes (gender, age, geography). Trigger mandatory review if any ratio falls below 0.80.

---

## How to Run

### Prerequisites

*pip install pandas numpy matplotlib seaborn scipy scikit-learn fairlearn*

### Execution Order

The notebooks must be run in sequence, as each depends on the output of the previous:

*01-data-quality.ipynb* → produces *data/credit_applications_clean.csv*
*02-bias-analysis.ipynb* → reads *data/credit_applications_clean.csv*
*03-privacy-demo.ipynb* → reads *data/credit_applications_clean.csv*

All notebooks are self-contained and run without errors when executed in order from the *notebooks/* directory.

---

*DEGO 2606 | Nova SBE | Group 6 | March 2026*