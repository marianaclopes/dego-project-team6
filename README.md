# Credit Applications – Data Engineering

This project implements a complete data engineering pipeline for cleaning and processing credit application data.

---

## Project Structure

project-teamX/

data/
- raw/        → Raw JSON dataset
- clean/      → Cleaned parquet dataset (output)
- processed/  → Optional future transformations

notebooks/
- 01-data-quality.ipynb

src/
- pipeline.py

README.md

---

## Pipeline Overview

The pipeline performs the following steps:

1. Load raw JSON dataset
2. Flatten nested JSON structure
3. Remove duplicate application IDs
4. Convert annual income to numeric
5. Replace invalid credit history values (< 0) with NA
6. Replace debt-to-income values outside [0,1] with NA
7. Remove unnecessary columns
8. Export cleaned dataset to Parquet format

---

## How to Run the Pipeline

1. Place the raw dataset inside:
data/raw/raw_credit_applications.json

2. Run the pipeline from the project root:
python src/pipeline.py

---

## Output

The cleaned dataset will be generated in:
data/clean/credit_applications_clean_v2.parquet

---

## Role: Data Engineer

Implemented responsibilities:

- Data loading
- Data cleaning logic
- Automated pipeline execution
- Repository structure organization
- Export to efficient Parquet format