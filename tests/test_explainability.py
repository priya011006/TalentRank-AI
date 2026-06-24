import pytest
from services.explainability import ExplainabilityEngine

def test_explainability_engine():
    engine = ExplainabilityEngine()
    
    # Setup a mock candidate
    scored_candidate = {
        "candidate_id": "CAND_0000001",
        "score": 0.85,
        "profile": {
            "years_of_experience": 7.0,
            "current_title": "AI Engineer",
            "location": "Pune, India",
            "country": "India"
        },
        "skills": [
            {"name": "Python", "proficiency": "advanced", "duration_months": 48},
            {"name": "Pinecone", "proficiency": "advanced", "duration_months": 24}
        ],
        "redrob_signals": {
            "notice_period_days": 30,
            "willing_to_relocate": False,
            "last_active_date": "2026-06-10", # Active 7 days ago
            "recruiter_response_rate": 0.95,
            "interview_completion_rate": 0.95,
            "offer_acceptance_rate": 0.8
        },
        "features": {
            "title_relevance": 1.0,
            "location_suitability": 1.0,
            "tenure_score": 1.0,
            "notice_period_score": 1.0,
            "behavior_activity": 1.0,
            "behavior_responsiveness": 1.0,
            "behavior_reliability": 1.0
        }
    }
    
    # 1. Generate explanation lists
    explanation = engine.generate_explanation(scored_candidate)
    
    assert "matched_skills" in explanation
    assert "strengths" in explanation
    assert "concerns" in explanation
    
    assert "Python Programming" in explanation["matched_skills"]
    assert "Vector Databases" in explanation["matched_skills"]
    
    # 2. Verify strengths
    assert len(explanation["strengths"]) > 0
    assert any("7.0 years" in s for s in explanation["strengths"])
    assert any("local" in s for s in explanation["strengths"])
    assert any("notice period" in s for s in explanation["strengths"])
    
    # 3. Generate text reasoning for CSV
    reasoning_text = engine.generate_explanation_text(scored_candidate, rank=1)
    assert len(reasoning_text) > 0
    assert len(reasoning_text) <= 180
    assert "AI Engineer" in reasoning_text
    assert "7.0" in reasoning_text
