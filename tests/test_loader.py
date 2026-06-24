import os
import json
import pytest
from backend.schema_validator import SchemaValidator
from backend.candidate_loader import stream_candidates
from backend.candidate_parser import (
    normalize_candidate,
    is_honeypot,
    detect_expert_zero_dur_skills,
    detect_career_duration_mismatch,
    detect_profile_experience_mismatch,
    detect_future_certifications
)

def test_stream_candidates(tmp_path):
    # Create a temporary JSONL file
    temp_jsonl = tmp_path / "temp_candidates.jsonl"
    dummy_records = [
        {"candidate_id": "CAND_0000001", "profile": {}},
        {"candidate_id": "CAND_0000002", "profile": {}}
    ]
    with open(temp_jsonl, "w", encoding="utf-8") as f:
        for r in dummy_records:
            f.write(json.dumps(r) + "\n")
            
    loaded = list(stream_candidates(file_path=str(temp_jsonl)))
    assert len(loaded) == 2
    assert loaded[0]["candidate_id"] == "CAND_0000001"
    assert loaded[1]["candidate_id"] == "CAND_0000002"

def test_schema_validator():
    validator = SchemaValidator()
    # Test validation against pretty-printed sample json
    with open("data/sample_candidates.json", "r", encoding="utf-8") as f:
        samples = json.load(f)
    assert len(samples) > 0
    # Samples should pass base schema validations
    assert validator.validate(samples[0]) is True

def test_normalize_candidate():
    dummy = {
        "candidate_id": "CAND_1234567",
        "profile": {
            "location": " Noida ",
            "country": "India",
            "current_title": "Engineer  ",
            "current_company": "  TCS  "
        }
    }
    normalized = normalize_candidate(dummy)
    assert normalized["certifications"] == []
    assert normalized["languages"] == []
    assert normalized["profile"]["location"] == "Noida"
    assert normalized["profile"]["current_title"] == "Engineer"
    assert normalized["profile"]["current_company"] == "TCS"

def test_detect_anomalies():
    # 1. Expert zero dur skills
    candidate_sk = {
        "skills": [{"name": "Python", "proficiency": "expert", "duration_months": 0}]
    }
    assert detect_expert_zero_dur_skills(candidate_sk) is True
    
    # 2. Career duration mismatch
    candidate_dur = {
        "career_history": [{
            "start_date": "2023-01-01",
            "end_date": "2023-06-01",
            "duration_months": 24, # 5 calendar months vs 24 claimed months
            "is_current": False
        }]
    }
    assert detect_career_duration_mismatch(candidate_dur) is True
    
    # 3. Profile experience mismatch
    candidate_profile_mismatch = {
        "profile": {"years_of_experience": 10.0},
        "career_history": [
            {"duration_months": 24} # 2 years total, profile claims 10
        ]
    }
    assert detect_profile_experience_mismatch(candidate_profile_mismatch) is True
    
    # 4. Future certifications
    candidate_cert = {
        "certifications": [{"name": "AWS Specialty", "year": 2030}]
    }
    assert detect_future_certifications(candidate_cert, current_year=2026) is True

def test_is_honeypot():
    with open("data/sample_candidates.json", "r", encoding="utf-8") as f:
        samples = json.load(f)
    # Verify that first record (normal candidate) is not flagged as a honeypot
    assert is_honeypot(samples[0]) is False

    # Verify that a custom created anomalous record is flagged as a honeypot
    anomaly = {
        "skills": [{"name": "Python", "proficiency": "expert", "duration_months": 0}],
        "certifications": []
    }
    assert is_honeypot(anomaly) is True
