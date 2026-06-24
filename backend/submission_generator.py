import csv
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config
from backend.candidate_loader import stream_candidates
from backend.jd_parser import parse_docx
from services.ranking_engine import rank_candidates
from services.explainability import ExplainabilityEngine

# Import official validator from the data directory
sys.path.append(str(config.DATA_DIR))
try:
    from validate_submission import validate_submission
except ImportError:
    # Fallback to direct path append if sys.path fails to resolve
    import sys
    sys.path.insert(0, str(config.DATA_DIR))
    from validate_submission import validate_submission

def generate_submission(participant_id: str) -> Path:
    """
    Generate the ranked Top 100 candidates CSV file for the challenge.
    Runs the official validator script on the file and raises ValueError if invalid.
    """
    output_path = config.OUTPUTS_DIR / f"{participant_id}.csv"
    
    # 1. Parse target JD
    jd_text = parse_docx(config.JD_PATH)
    
    # 2. Stream candidates pool (100k)
    candidates_iter = stream_candidates(config.CANDIDATES_PATH)
    
    # 3. Score and rank candidates
    print("Scoring and ranking candidate pool (running CPU-only pipeline)...")
    ranked = rank_candidates(candidates_iter, jd_text)
    
    # 4. Select top 100 fits
    top_100 = ranked[:100]
    
    # 5. Extract explainability justifications
    engine = ExplainabilityEngine()
    
    # 6. Write to CSV output (following format rules exactly)
    config.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        
        for i, c in enumerate(top_100):
            rank = i + 1
            reasoning = engine.generate_explanation_text(c, rank)
            writer.writerow([c["candidate_id"], rank, c["score"], reasoning])
            
    print(f"Rankings successfully written to: {output_path}")
    
    # 7. Validate before concluding
    errors = validate_submission(str(output_path))
    if errors:
        print(f"Validation FAILED with {len(errors)} issue(s):")
        for err in errors:
            print(f"  - {err}")
        raise ValueError("Generated CSV violated validator checks.")
    else:
        print("Validation PASSED. Submission CSV is 100% compliant!")
        
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python backend/submission_generator.py <participant_id>")
        sys.exit(1)
    generate_submission(sys.argv[1])
