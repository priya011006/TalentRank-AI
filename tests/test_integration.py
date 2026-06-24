import pytest
import csv
import json
from pathlib import Path
from backend.candidate_loader import stream_candidates
from backend.jd_parser import parse_docx
from services.ranking_engine import rank_candidates
from backend.submission_generator import generate_submission
import config

def test_honeypots_not_ranked():
    """
    Ranking validation test:
    Verify that none of the 92 anomalous honeypot candidates are ranked
    in the final top 100 candidates.
    """
    # 1. Identify the honeypots programmatically using same criteria
    # This forms our target blacklist
    honeypots = set()
    from backend.candidate_parser import is_honeypot
    
    candidates = list(stream_candidates(config.CANDIDATES_PATH))
    for c in candidates:
        if is_honeypot(c, config.CURRENT_DATE):
            honeypots.add(c["candidate_id"])
            
    # Verify we successfully detected the honeypot dataset size
    assert len(honeypots) == 92
    
    # 2. Run ranking on a sample to verify none of these IDs are included
    jd_text = parse_docx(config.JD_PATH)
    ranked = rank_candidates(candidates, jd_text)
    
    top_100_ids = {c["candidate_id"] for c in ranked[:100]}
    
    # Assert intersection is empty
    overlap = top_100_ids.intersection(honeypots)
    assert len(overlap) == 0, f"Disqualification warning! The following honeypot candidates were ranked: {overlap}"

def test_end_to_end_pipeline():
    """
    Integration test:
    Generate a full submission CSV, run the official validator,
    verify CSV formatting rules, and clean up.
    """
    participant_id = "integration_test_team"
    csv_path = config.OUTPUTS_DIR / f"{participant_id}.csv"
    
    if csv_path.exists():
        csv_path.unlink()
        
    try:
        # Run full pipeline
        output_path = generate_submission(participant_id)
        assert output_path.exists() is True
        
        # Read and check row compliance
        with open(output_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
            
        assert len(rows) == 101 # header + 100 rows
        assert rows[0] == ["candidate_id", "rank", "score", "reasoning"]
        
    finally:
        if csv_path.exists():
            csv_path.unlink()
