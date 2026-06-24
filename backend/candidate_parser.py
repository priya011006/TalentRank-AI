import datetime
from typing import Dict, Any, List

def parse_date(date_str: str) -> datetime.date:
    """Parse YYYY-MM-DD date strings safely."""
    if not date_str:
        return None
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None

def normalize_candidate(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize fields in candidate record:
    - Inject default empty lists for optional fields (certifications, languages).
    - Strip leading/trailing whitespaces in titles, locations, and companies.
    """
    normalized = candidate.copy()
    
    # Optional schema structures default fallback
    if "certifications" not in normalized or normalized["certifications"] is None:
        normalized["certifications"] = []
    if "languages" not in normalized or normalized["languages"] is None:
        normalized["languages"] = []
        
    # Profile sanitization
    profile = normalized.get("profile", {})
    profile["location"] = profile.get("location", "").strip()
    profile["country"] = profile.get("country", "").strip()
    profile["current_title"] = profile.get("current_title", "").strip()
    profile["current_company"] = profile.get("current_company", "").strip()
    
    # Career history sanitization
    for ch in normalized.get("career_history", []):
        ch["company"] = ch.get("company", "").strip()
        ch["title"] = ch.get("title", "").strip()
        ch["description"] = ch.get("description", "").strip()
        
    # Education sanitization
    for edu in normalized.get("education", []):
        edu["institution"] = edu.get("institution", "").strip()
        edu["degree"] = edu.get("degree", "").strip()
        edu["field_of_study"] = edu.get("field_of_study", "").strip()
        
    return normalized

def detect_expert_zero_dur_skills(candidate: Dict[str, Any]) -> bool:
    """Check if candidate lists any skill at 'expert' level but with 0 months duration."""
    skills = candidate.get("skills", [])
    for sk in skills:
        if sk.get("proficiency") == "expert" and sk.get("duration_months", 0) == 0:
            return True
    return False

def detect_career_duration_mismatch(candidate: Dict[str, Any], evaluation_date_str: str = "2026-06-17") -> bool:
    """
    Check if any job's claimed duration in months significantly differs (by >3 months)
    from the date delta between start and end dates.
    """
    eval_date = datetime.datetime.strptime(evaluation_date_str, "%Y-%m-%d").date()
    for ch in candidate.get("career_history", []):
        try:
            start_date = parse_date(ch.get("start_date"))
            if not start_date:
                continue
                
            is_current = ch.get("is_current", False)
            end_date_str = ch.get("end_date")
            
            if is_current or not end_date_str:
                end_date = eval_date
            else:
                end_date = parse_date(end_date_str)
                
            if not end_date:
                continue
                
            diff_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            claimed_duration = ch.get("duration_months", 0)
            
            if abs(diff_months - claimed_duration) > 3:
                return True
        except Exception:
            pass
    return False

def detect_profile_experience_mismatch(candidate: Dict[str, Any]) -> bool:
    """
    Check if overall profile years of experience exceeds the sum of career history
    job durations by more than 2.0 years.
    """
    profile_exp = candidate.get("profile", {}).get("years_of_experience", 0)
    
    total_months = sum(ch.get("duration_months", 0) for ch in candidate.get("career_history", []))
    history_years = total_months / 12.0
    
    if abs(profile_exp - history_years) > 2.0 and profile_exp > 0:
        return True
    return False

def detect_future_certifications(candidate: Dict[str, Any], current_year: int = 2026) -> bool:
    """Check if candidate lists certifications with years in the future (>2026)."""
    for cert in candidate.get("certifications", []):
        year = cert.get("year")
        if year and year > current_year:
            return True
    return False

def is_honeypot(candidate: Dict[str, Any], evaluation_date_str: str = "2026-06-17") -> bool:
    """
    Check candidate profile for logical contradictions representing honeypot traps.
    Returns True if any anomalies are found.
    """
    if detect_expert_zero_dur_skills(candidate):
        return True
    if detect_career_duration_mismatch(candidate, evaluation_date_str):
        return True
    if detect_profile_experience_mismatch(candidate):
        return True
    current_year = int(evaluation_date_str.split("-")[0])
    if detect_future_certifications(candidate, current_year):
        return True
    return False
