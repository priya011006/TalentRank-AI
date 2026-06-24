import os
import csv
import pytest
from pathlib import Path
from backend.submission_generator import generate_submission
import config

def test_generate_submission():
    participant_id = "test_team_verification"
    csv_path = config.OUTPUTS_DIR / f"{participant_id}.csv"
    
    # Clean up any previous test file
    if csv_path.exists():
        csv_path.unlink()
        
    try:
        # Run generation
        output_path = generate_submission(participant_id)
        
        # Verify file creation
        assert output_path.exists() is True
        assert output_path == csv_path
        
        # Verify row and column formatting
        with open(output_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
            
        # 1 header row + 100 data rows = 101 rows total
        assert len(rows) == 101
        
        # Check header names
        assert rows[0] == ["candidate_id", "rank", "score", "reasoning"]
        
        # Check ranks are sequential 1 to 100
        for i in range(1, 101):
            assert int(rows[i][1]) == i
            
        # Check scores are non-increasing
        scores = [float(rows[i][2]) for i in range(1, 101)]
        for i in range(len(scores) - 1):
            assert scores[i] >= scores[i+1]
            
    finally:
        # Clean up test output file
        if csv_path.exists():
            csv_path.unlink()
            pass
