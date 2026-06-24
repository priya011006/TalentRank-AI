import pytest
import json
from services.feature_generator import FeatureGenerator
from backend.candidate_parser import normalize_candidate

@pytest.fixture
def dummy_generator():
    jd_text = "Senior AI Engineer. Deploys embeddings-based retrieval systems, sentence-transformers, Pinecone vector database. Python programming, fine-tuning LoRA, and NDCG ranking metrics."
    return FeatureGenerator(jd_text)

def test_semantic_similarity(dummy_generator):
    # Match text vs non-match text
    match_text = "I build embeddings-based search engines using sentence-transformers and Pinecone vector databases in Python."
    nomatch_text = "Experienced mechanical design technician specializing in CAD drawings and assembly pipelines."
    
    sim_high = dummy_generator.get_semantic_similarity(match_text)
    sim_low = dummy_generator.get_semantic_similarity(nomatch_text)
    
    assert sim_high > sim_low
    assert sim_high > 0.1
    assert sim_low < 0.05

def test_title_relevance(dummy_generator):
    c1 = {"profile": {"current_title": "Senior AI Engineer"}, "career_history": []}
    c2 = {"profile": {"current_title": "Marketing Manager"}, "career_history": []}
    c3 = {"profile": {"current_title": "Software Engineer"}, "career_history": []}
    
    assert dummy_generator.compute_title_relevance(c1) == 1.0
    assert dummy_generator.compute_title_relevance(c2) == 0.0
    assert dummy_generator.compute_title_relevance(c3) == 0.5

def test_skills_score(dummy_generator):
    c = {
        "skills": [
            {"name": "Pinecone", "proficiency": "expert", "duration_months": 24}, # required
            {"name": "LoRA", "proficiency": "intermediate", "duration_months": 12} # preferred
        ]
    }
    scores = dummy_generator.compute_skills_score(c)
    assert scores["required_score"] > 0
    assert scores["preferred_score"] > 0

def test_experience_fit(dummy_generator):
    c_target = {"profile": {"years_of_experience": 7.0}} # within 5-9 target
    c_low = {"profile": {"years_of_experience": 3.0}} # below target
    c_high = {"profile": {"years_of_experience": 15.0}} # above target
    
    assert dummy_generator.compute_experience_fit(c_target) == 1.0
    assert dummy_generator.compute_experience_fit(c_low) < 1.0
    assert dummy_generator.compute_experience_fit(c_high) < 1.0

def test_tenure_score(dummy_generator):
    c_stable = {"career_history": [{"duration_months": 36}, {"duration_months": 48}]} # avg 42 months
    c_hopper = {"career_history": [{"duration_months": 10}, {"duration_months": 12}, {"duration_months": 8}]} # avg 10 months
    
    assert dummy_generator.compute_tenure_score(c_stable) == 1.0
    assert dummy_generator.compute_tenure_score(c_hopper) == 0.2

def test_location_suitability(dummy_generator):
    c_local = {"profile": {"location": "Pune, India", "country": "India"}, "redrob_signals": {"willing_to_relocate": False}}
    c_reloc = {"profile": {"location": "Bangalore, India", "country": "India"}, "redrob_signals": {"willing_to_relocate": True}}
    c_intl = {"profile": {"location": "Toronto, Canada", "country": "Canada"}, "redrob_signals": {"willing_to_relocate": True}}
    
    assert dummy_generator.compute_location_suitability(c_local) == 1.0
    assert dummy_generator.compute_location_suitability(c_reloc) == 0.8
    assert dummy_generator.compute_location_suitability(c_intl) == 0.0

def test_is_suspicious_profile(dummy_generator):
    # 1. Honeypot profile (expert skill with 0 duration)
    honeypot = {
        "candidate_id": "CAND_0000001",
        "skills": [{"name": "NLP", "proficiency": "expert", "duration_months": 0}],
        "career_history": []
    }
    
    # 2. Consulting only profile
    consulting = {
        "candidate_id": "CAND_0000002",
        "skills": [],
        "career_history": [
            {"company": "TCS", "duration_months": 12},
            {"company": "Infosys", "duration_months": 24}
        ]
    }
    
    # 3. Normal candidate
    with open("data/sample_candidates.json", "r", encoding="utf-8") as f:
        samples = json.load(f)
    normal = normalize_candidate(samples[0])
    
    assert dummy_generator.is_suspicious_profile(honeypot) is True
    assert dummy_generator.is_suspicious_profile(consulting) is True
    assert dummy_generator.is_suspicious_profile(normal) is False

def test_extract_features(dummy_generator):
    with open("data/sample_candidates.json", "r", encoding="utf-8") as f:
        samples = json.load(f)
    normal = normalize_candidate(samples[0])
    
    features = dummy_generator.extract_features(normal)
    
    expected_keys = [
        "candidate_id", "sim_profile", "sim_history", "title_relevance", 
        "skills_required_score", "skills_preferred_score", "experience_fit", 
        "tenure_score", "location_suitability", "notice_period_score", 
        "behavior_activity", "behavior_responsiveness", "behavior_reliability", 
        "risk_flag"
    ]
    for key in expected_keys:
        assert key in features
