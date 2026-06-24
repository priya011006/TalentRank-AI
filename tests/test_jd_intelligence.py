import pytest
from pathlib import Path
from backend.jd_parser import parse_docx
from backend.skill_extractor import SkillExtractor
from backend.requirement_extractor import RequirementExtractor
from config import JD_PATH

def test_parse_docx():
    # Test reading the actual job_description.docx file
    assert JD_PATH.exists() is True
    text = parse_docx(JD_PATH)
    assert len(text) > 0
    assert "Senior AI Engineer" in text
    assert "Redrob" in text

def test_skill_extractor():
    extractor = SkillExtractor()
    # Test on standard text
    text = "We need Pinecone, Milvus vector search, Python programming, and fine-tuning with LoRA."
    skills = extractor.extract_skills(text)
    
    assert "vector_db" in skills
    assert "pinecone" in skills["vector_db"]
    assert "milvus" in skills["vector_db"]
    assert "programming" in skills
    assert "python" in skills["programming"]
    assert "llm_tuning" in skills
    assert "lora" in skills["llm_tuning"]

def test_requirement_extractor():
    extractor = RequirementExtractor()
    
    # 1. Experience extraction
    text_exp = "Requirements: 5-9 years of production machine learning experience."
    min_exp, max_exp = extractor.extract_experience(text_exp)
    assert min_exp == 5
    assert max_exp == 9
    
    # Test dash variations
    min_exp_dash, max_exp_dash = extractor.extract_experience("Experience: 5–9 years")
    assert min_exp_dash == 5
    assert max_exp_dash == 9
    
    # 2. Location extraction
    text_loc = "Location is Pune/Noida, India (Hybrid preferred)."
    loc = extractor.extract_locations(text_loc)
    assert "Pune" in loc["cities"]
    assert "Noida" in loc["cities"]
    assert loc["hybrid_preferred"] is True
    
    # 3. Notice period
    text_notice = "Notice period: sub-30-day notice is preferred."
    notice = extractor.extract_notice_period(text_notice)
    assert notice == 30
