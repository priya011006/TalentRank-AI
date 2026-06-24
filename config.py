import os
from pathlib import Path

# Root and project directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
BACKEND_DIR = BASE_DIR / "backend"
SERVICES_DIR = BASE_DIR / "services"
OUTPUTS_DIR = BASE_DIR / "outputs"
DOCS_DIR = BASE_DIR / "docs"
UTILS_DIR = BASE_DIR / "utils"
TESTS_DIR = BASE_DIR / "tests"

# Source file paths
CANDIDATES_PATH = DATA_DIR / "candidates.jsonl"
SCHEMA_PATH = DATA_DIR / "candidate_schema.json"
JD_PATH = DATA_DIR / "job_description.docx"
SIGNALS_PATH = DATA_DIR / "redrob_signals_doc.docx"

# Output submission template
METADATA_TEMPLATE_PATH = DATA_DIR / "submission_metadata_template.yaml"

# Constants
CURRENT_DATE = "2026-06-17"  # Challenge execution timeline

# Set of consulting/services companies for background filtering
CONSULTING_FIRMS = {
    "TCS",
    "Infosys",
    "Wipro",
    "Accenture",
    "Cognizant",
    "Capgemini",
    "HCL",
    "Tech Mahindra",
    "Mindtree",
    "Mphasis"
}

# Heuristic weights for combination scoring
WEIGHT_SEMANTIC = 0.35      # Profile text similarity with JD
WEIGHT_SKILLS = 0.35        # Precise match on technical capabilities
WEIGHT_EXPERIENCE = 0.30    # Job experience relevance (5-9 years target)
