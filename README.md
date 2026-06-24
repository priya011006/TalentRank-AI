# TalentRank AI — Candidate Discovery & Ranking Engine

TalentRank AI is a production-grade candidate discovery, matching, and ranking engine built to evaluate massive candidate pools against specific hiring requirements in real-time. The system implements a high-performance cascade pipeline that cleans, filters, scores, and explains candidate recommendations under strict CPU-only and local compute constraints.

---

## 🚀 Core Features

*   **Premium Glassmorphic Interface**: A dark-mode recruiter dashboard styled with soft gradients, floating accents, and interactive controls to adjust heuristic scoring weights in real-time.
*   **Logical Contradiction Detection (Anti-Traps)**: An advanced pre-filtering step that automatically identifies and disqualifies candidate profiles containing fraudulent career histories or date contradictions (honeypots).
*   **Cascade Search & Pruning**: Rapid location-suitability and corporate exclusion filters that prune a 100,000-candidate pool down to a highly relevant shortlist in milliseconds, enabling CPU-only real-time performance.
*   **Local NLP Semantic Alignment**: Lightweight local vector space modeling (TF-IDF + Cosine Similarity) that compares job descriptions with candidate headlines, summaries, and career history logs.
*   **Technical Skill Weighting**: Multi-tier scoring of required and preferred skills based on stated experience duration and proficiency levels (Expert, Intermediate, Beginner).
*   **Behavioral Signal Modifiers**: Score optimization based on recruiter response rates, login recency, notice period thresholds, and interview attendance reliability.
*   **Explainable AI (XAI)**: Context-aware recommendations detailing matched skills, key strengths, potential areas of concern, and a concise 180-character summary explaining each candidate's ranking.

---

## 🛠️ System Architecture

The pipeline processes candidate profiles in a three-stage cascade:

1.  **Stage 1: Hard Pruning Filters**: Drops profile contradictions (mismatched calendar dates, zero-duration expert skills, future dates), consulting-firm employees, and location-incompatible profiles.
2.  **Stage 2: Hybrid Scoring Engine**: Computes semantic text overlap, skill duration scores, experience range alignment, and company tenure stability.
3.  **Stage 3: Behavioral Signal Modifier**: Adjusts base scores dynamically using real-time engagement patterns and availability constraints.

---

## 📁 Repository Structure

```text
TalentRank-AI/
├── .streamlit/
│   └── config.toml               # Streamlit theme (dark mode, violet accent)
├── backend/
│   ├── candidate_loader.py       # Line-by-line JSONL streaming loader
│   ├── candidate_parser.py       # Candidate profiles cleaner & normalizer
│   ├── jd_parser.py              # Word document parser (.docx)
│   ├── schema_validator.py       # jsonschema profile validator
│   └── submission_generator.py   # Final CSV output formatter & validator
├── services/
│   ├── explainability.py         # AI explainability text generator
│   ├── feature_generator.py      # Feature computation (tenure, skills, experience)
│   ├── ranking_config.py         # Heuristic weights configuration defaults
│   └── ranking_engine.py         # Core scoring, filtering, and tie-breaking engine
├── frontend/
│   └── app.py                    # Recruiter dashboard UI (Streamlit)
├── tests/
│   ├── test_loader.py            # Loader and schema validation unit tests
│   ├── test_jd_intelligence.py   # JD requirements extraction unit tests
│   ├── test_features.py          # Feature extraction unit tests
│   ├── test_ranking.py           # Core ranking rules unit tests
│   ├── test_explainability.py    # Explainability generator unit tests
│   ├── test_submission.py        # Output CSV formatting unit tests
│   └── test_integration.py       # End-to-end integration and honeypot tests
├── requirements.txt              # Project library dependencies
├── config.py                     # Global file paths and hyperparameter constants
└── settings.py                   # UI styling and page configurations
```

---

## ⚙️ Setup & Installation

### Prerequisites
*   Python 3.10 or higher
*   Windows / macOS / Linux

### 1. Create and Activate a Virtual Environment
```powershell
# Create environment
python -m venv .venv

# Activate on Windows (PowerShell)
.venv\Scripts\activate

# Activate on macOS/Linux
source .venv/bin/activate
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Place Input Datasets
*   Place the candidate database (`candidates.jsonl`) under the `data/` folder.
*   Place the target job description (`job_description.docx`) under the `data/` folder.

---

## 🖥️ Running the Application

Launch the recruiter dashboard locally using the following command:
```powershell
streamlit run frontend/app.py
```
Open your browser and navigate to `http://localhost:8501`.

---

## 🧪 Running Verification Tests

Validate all pipeline modules and anti-trap filters using `pytest`:
```powershell
python -m pytest
```
All unit and integration tests should pass successfully.
