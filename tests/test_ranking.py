import pytest
from services.ranking_engine import rank_candidates
from services.ranking_config import RankingConfig

def test_rank_candidates():
    # Setup dummy candidates
    # C1 is a strong candidate, C2 is a honeypot (expert 0 dur skill), C3 is a normal candidate, C4 is a duplicate score tie-break test
    dummy_jd = "Python Developer. Must have vector search and ML experience."
    
    candidates = [
        {
            "candidate_id": "CAND_0000001",
            "profile": {
                "years_of_experience": 6.5,
                "current_title": "AI Engineer",
                "location": "Pune, India",
                "country": "India"
            },
            "career_history": [{"company": "Acme Corp", "duration_months": 78}],
            "skills": [
                {"name": "Python", "proficiency": "advanced", "duration_months": 48},
                {"name": "Vector Search", "proficiency": "advanced", "duration_months": 24}
            ],
            "redrob_signals": {
                "notice_period_days": 30,
                "willing_to_relocate": False,
                "last_active_date": "2026-06-01",
                "recruiter_response_rate": 0.9,
                "avg_response_time_hours": 2,
                "interview_completion_rate": 0.95,
                "offer_acceptance_rate": 0.8
            }
        },
        {
            # Honeypot: expert skill with 0 duration
            "candidate_id": "CAND_0000002",
            "profile": {
                "years_of_experience": 5.0,
                "current_title": "ML Engineer",
                "location": "Noida, India",
                "country": "India"
            },
            "career_history": [{"company": "Hooli", "duration_months": 60}],
            "skills": [
                {"name": "Python", "proficiency": "expert", "duration_months": 0}
            ],
            "redrob_signals": {"notice_period_days": 30}
        },
        {
            # Tie-break candidate 1 (same profile as C1, but different ID)
            "candidate_id": "CAND_0000004",
            "profile": {
                "years_of_experience": 6.5,
                "current_title": "AI Engineer",
                "location": "Pune, India",
                "country": "India"
            },
            "career_history": [{"company": "Acme Corp", "duration_months": 78}],
            "skills": [
                {"name": "Python", "proficiency": "advanced", "duration_months": 48},
                {"name": "Vector Search", "proficiency": "advanced", "duration_months": 24}
            ],
            "redrob_signals": {
                "notice_period_days": 30,
                "willing_to_relocate": False,
                "last_active_date": "2026-06-01",
                "recruiter_response_rate": 0.9,
                "avg_response_time_hours": 2,
                "interview_completion_rate": 0.95,
                "offer_acceptance_rate": 0.8
            }
        }
    ]
    
    config = RankingConfig()
    ranked = rank_candidates(candidates, dummy_jd, config)
    
    # Verify C2 (Honeypot) was filtered out
    active_ids = [c["candidate_id"] for c in ranked]
    assert "CAND_0000002" not in active_ids
    
    # Verify we have exactly 2 candidates remaining
    assert len(ranked) == 2
    
    # Verify tie-breaker (C1 has lexicographically smaller ID than C4, so CAND_0000001 must appear first)
    assert ranked[0]["candidate_id"] == "CAND_0000001"
    assert ranked[1]["candidate_id"] == "CAND_0000004"
    assert ranked[0]["score"] == ranked[1]["score"]
