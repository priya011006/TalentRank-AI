from typing import List, Dict, Any, Iterable
from services.feature_generator import FeatureGenerator
from services.ranking_config import RankingConfig
from backend.candidate_parser import normalize_candidate

def rank_candidates(candidates: Iterable[Dict[str, Any]], jd_text: str, config: RankingConfig = RankingConfig()) -> List[Dict[str, Any]]:
    """
    Score, filter, and rank a stream of candidates.
    Applies the hybrid weights config and breaks ties deterministically by candidate_id.
    """
    fg = FeatureGenerator(jd_text)
    scored_candidates = []
    
    for c in candidates:
        # 1. Normalize
        normalized = normalize_candidate(c)
        
        # 2. Extract Features
        features = fg.extract_features(normalized)
        
        # 3. Apply Hard Filters (Honeypots, Consulting-only, Location incompatibilities)
        if config.FILTER_RISK_PROFILES and features["risk_flag"]:
            continue
        if config.FILTER_LOCATION_INCOMPATIBLE and features["location_suitability"] == 0.0:
            continue
            
        # 4. Compute Scores
        # Semantic Score (0.0 - 1.0)
        sem_score = (features["sim_profile"] * config.WEIGHT_SIM_PROFILE) + \
                    (features["sim_history"] * config.WEIGHT_SIM_HISTORY)
        
        # Skills Score (capping raw scores for normalization)
        req_skills_norm = min(1.0, features["skills_required_score"] / 5.0)
        pref_skills_norm = min(1.0, features["skills_preferred_score"] / 3.0)
        skills_score = (req_skills_norm * config.WEIGHT_SKILLS_REQUIRED) + \
                       (pref_skills_norm * config.WEIGHT_SKILLS_PREFERRED)
        
        # Experience Score (0.0 - 1.0)
        exp_score = (features["experience_fit"] * config.WEIGHT_EXP_FIT) + \
                    (features["title_relevance"] * config.WEIGHT_TITLE_RELEVANCE)
        
        # Base Weighted Score
        base_score = (sem_score * config.WEIGHT_SEMANTIC) + \
                     (skills_score * config.WEIGHT_SKILLS) + \
                     (exp_score * config.WEIGHT_EXPERIENCE)
        
        # 5. Apply Behavioral Modifiers and Penalties
        # Behavioral modifier (between 0.5 and 1.0)
        behavior_score = (features["behavior_activity"] * config.WEIGHT_BEHAVIOR_ACTIVITY) + \
                         (features["behavior_responsiveness"] * config.WEIGHT_BEHAVIOR_RESPONSIVENESS) + \
                         (features["behavior_reliability"] * config.WEIGHT_BEHAVIOR_RELIABILITY)
        behavior_modifier = 0.5 + (0.5 * behavior_score)
        
        # Final combined multiplier score
        final_score = base_score * \
                      behavior_modifier * \
                      features["notice_period_score"] * \
                      features["location_suitability"] * \
                      features["tenure_score"]
                      
        # Store candidate with scoring metadata
        scored_candidates.append({
            "candidate_id": features["candidate_id"],
            "score": round(final_score, 4),
            "features": features,
            "profile": normalized["profile"],
            "career_history": normalized["career_history"],
            "skills": normalized["skills"],
            "redrob_signals": normalized["redrob_signals"],
            "certifications": normalized["certifications"],
            "languages": normalized["languages"]
        })
        
    # 6. Sort deterministically (Score descending, Candidate ID ascending)
    scored_candidates.sort(key=lambda x: (-x["score"], x["candidate_id"]))
    
    return scored_candidates
