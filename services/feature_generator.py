import datetime
import re
from typing import Dict, Any, Set
from sklearn.feature_extraction.text import TfidfVectorizer
from backend.candidate_parser import is_honeypot, parse_date
import config

class FeatureGenerator:
    def __init__(self, jd_text: str):
        """
        Initialize the feature generator.
        Pre-fits a TF-IDF vectorizer on the Job Description text.
        """
        self.jd_text = jd_text
        self.vectorizer = TfidfVectorizer(stop_words='english')
        # Learn vocabulary from the job description
        self.vectorizer.fit([jd_text])
        self.jd_vector = self.vectorizer.transform([jd_text])

    def get_semantic_similarity(self, text: str) -> float:
        """
        Compute cosine similarity between the input text and the JD 
        using the fitted TF-IDF term space.
        """
        if not text or not text.strip():
            return 0.0
        try:
            text_vector = self.vectorizer.transform([text])
            sim = (self.jd_vector * text_vector.T).toarray()[0][0]
            return float(sim)
        except Exception:
            return 0.0

    def compute_title_relevance(self, candidate: Dict[str, Any]) -> float:
        """
        Score title relevance based on presence of target keywords.
        Target: AI, ML, NLP, Search, Retrieval, Data Scientist, Software Engineer.
        """
        target_keywords = ["ai", "ml", "machine learning", "nlp", "search", "retrieval", "data scientist", "software engineer", "backend"]
        current_title = candidate.get("profile", {}).get("current_title", "").lower()
        
        score = 0.0
        for kw in target_keywords:
            if kw in current_title:
                score = max(score, 0.5 if kw in ["software engineer", "backend"] else 1.0)
                
        # Look at past job titles
        for ch in candidate.get("career_history", []):
            ch_title = ch.get("title", "").lower()
            for kw in target_keywords:
                if kw in ch_title:
                    score = max(score, 0.4 if kw in ["software engineer", "backend"] else 0.8)
                    
        return score

    def compute_skills_score(self, candidate: Dict[str, Any]) -> Dict[str, float]:
        """
        Compute required and preferred skill scores.
        Required: embeddings, vector_db, hybrid_search, evaluation, programming.
        Preferred: llm_tuning, learning_to_rank, distributed_systems.
        Scores are weighted by proficiency (expert=1.0, advanced=0.8, intermediate=0.5, beginner=0.2)
        and duration used.
        """
        required_skills = {
            "embeddings": ["embedding", "sentence-transformer", "bge", "e5", "openai embedding"],
            "vector_db": ["pinecone", "weaviate", "qdrant", "milvus", "faiss", "vector database", "vector search"],
            "hybrid_search": ["opensearch", "elasticsearch", "hybrid search", "bm25"],
            "evaluation": ["ndcg", "mrr", "map", "eval", "evaluation framework"],
            "programming": ["python"]
        }
        
        preferred_skills = {
            "llm_tuning": ["fine-tuning", "lora", "qlora", "peft", "llm fine-tuning"],
            "learning_to_rank": ["learning-to-rank", "learning to rank", "xgboost", "ltr"],
            "distributed_systems": ["distributed systems", "large-scale inference", "inference optimization"]
        }
        
        proficiency_weights = {
            "expert": 1.0,
            "advanced": 0.8,
            "intermediate": 0.5,
            "beginner": 0.2
        }
        
        req_score = 0.0
        pref_score = 0.0
        
        for sk in candidate.get("skills", []):
            name_lower = sk.get("name", "").lower()
            prof = sk.get("proficiency", "beginner")
            weight = proficiency_weights.get(prof, 0.2)
            duration = sk.get("duration_months", 0)
            
            # Duration scaling modifier (diminishing returns)
            duration_mod = 1.0 + (duration / 12.0) if duration > 0 else 1.0
            skill_value = weight * duration_mod
            
            # Check required
            is_req = False
            for cat, keywords in required_skills.items():
                if any(kw in name_lower for kw in keywords):
                    is_req = True
                    break
            if is_req:
                req_score += skill_value
                continue
                
            # Check preferred
            is_pref = False
            for cat, keywords in preferred_skills.items():
                if any(kw in name_lower for kw in keywords):
                    is_pref = True
                    break
            if is_pref:
                pref_score += skill_value

        return {
            "required_score": req_score,
            "preferred_score": pref_score
        }

    def compute_experience_fit(self, candidate: Dict[str, Any]) -> float:
        """
        Score how well years of experience matches target (5-9 years).
        Returns 1.0 if in target, else penalizes linearly based on distance.
        """
        exp = candidate.get("profile", {}).get("years_of_experience", 0)
        if 5.0 <= exp <= 9.0:
            return 1.0
        elif exp < 5.0:
            return max(0.1, exp / 5.0) # linear penalty for lower experience
        else:
            # exp > 9.0
            diff = exp - 9.0
            return max(0.2, 1.0 - (diff * 0.1)) # soft penalty for higher experience

    def compute_tenure_score(self, candidate: Dict[str, Any]) -> float:
        """
        Penalize title-chasers (average tenure < 18 months per job).
        Returns a score between 0.2 and 1.0.
        """
        history = candidate.get("career_history", [])
        if not history:
            return 1.0
            
        total_months = sum(ch.get("duration_months", 0) for ch in history)
        avg_tenure = total_months / len(history)
        
        if avg_tenure >= 24:
            return 1.0
        elif avg_tenure >= 18:
            return 0.8
        elif avg_tenure >= 12:
            return 0.5
        else:
            return 0.2

    def compute_location_suitability(self, candidate: Dict[str, Any]) -> float:
        """
        Evaluate geographic alignment:
        - 1.0 if in Pune or Noida.
        - 0.8 if in India and willing to relocate.
        - 0.3 if in India but unwilling to relocate.
        - 0.0 if international (no work visa sponsorship).
        """
        loc = candidate.get("profile", {}).get("location", "").lower()
        country = candidate.get("profile", {}).get("country", "").lower()
        willing = candidate.get("redrob_signals", {}).get("willing_to_relocate", False)
        
        is_pune_noida = "pune" in loc or "noida" in loc
        is_india = country == "india" or "india" in loc
        
        if is_pune_noida:
            return 1.0
        elif is_india and willing:
            return 0.8
        elif is_india:
            return 0.3
        else:
            return 0.0

    def compute_notice_period_score(self, candidate: Dict[str, Any]) -> float:
        """
        Score notice period alignment. Lower is preferred:
        - <= 30 days: 1.0
        - 60 days: 0.85
        - 90 days: 0.70
        - > 90 days: 0.50
        """
        np_days = candidate.get("redrob_signals", {}).get("notice_period_days", 30)
        if np_days <= 30:
            return 1.0
        elif np_days <= 60:
            return 0.85
        elif np_days <= 90:
            return 0.70
        else:
            return 0.50

    def compute_behavior_score(self, candidate: Dict[str, Any], evaluation_date_str: str = config.CURRENT_DATE) -> Dict[str, float]:
        """
        Compute activity and response indicators from redrob_signals.
        """
        sig = candidate.get("redrob_signals", {})
        
        # 1. Activity (login recency)
        last_active_s = sig.get("last_active_date", "")
        try:
            la_date = datetime.datetime.strptime(last_active_s, "%Y-%m-%d").date()
            eval_date = datetime.datetime.strptime(evaluation_date_str, "%Y-%m-%d").date()
            days_inactive = (eval_date - la_date).days
        except Exception:
            days_inactive = 180
            
        activity = max(0.0, 1.0 - (days_inactive / 180.0))
        
        # 2. Responsiveness (recruiter response rate + speed)
        resp_rate = sig.get("recruiter_response_rate", 0.0)
        resp_time = sig.get("avg_response_time_hours", 168.0)
        time_score = max(0.0, 1.0 - (resp_time / 168.0)) # 1 week max penalty
        responsiveness = (resp_rate * 0.7) + (time_score * 0.3)
        
        # 3. Reliability (interview attendance + offer acceptance)
        int_comp = sig.get("interview_completion_rate", 0.0)
        offer_acc = sig.get("offer_acceptance_rate", -1.0)
        if offer_acc == -1.0:
            offer_acc = 0.5 # Neutral fallback for no history
        reliability = (int_comp * 0.6) + (offer_acc * 0.4)
        
        return {
            "activity": activity,
            "responsiveness": responsiveness,
            "reliability": reliability
        }

    def is_suspicious_profile(self, candidate: Dict[str, Any], consulting_firms: Set[str] = config.CONSULTING_FIRMS, evaluation_date_str: str = config.CURRENT_DATE) -> bool:
        """
        Identify if candidate is a honeypot, has consulting-only history,
        or shows signs of keyword stuffing.
        """
        # Honeypots check
        if is_honeypot(candidate, evaluation_date_str):
            return True
            
        # Consulting-only history check
        companies = {ch.get("company") for ch in candidate.get("career_history", []) if ch.get("company")}
        if companies and companies.issubset(consulting_firms):
            return True
            
        # Keyword stuffing check
        skills = candidate.get("skills", [])
        if len(skills) > 20:
            return True
            
        expert_short_dur = sum(1 for sk in skills if sk.get("proficiency") == "expert" and sk.get("duration_months", 0) < 6)
        if expert_short_dur >= 5:
            return True
            
        return False

    def extract_features(self, candidate: Dict[str, Any], evaluation_date_str: str = config.CURRENT_DATE) -> Dict[str, Any]:
        """
        Extract the complete feature vector for a candidate record.
        """
        # Text concatenation for semantic matches
        profile = candidate.get("profile", {})
        summary_text = f"{profile.get('headline', '')} {profile.get('summary', '')}"
        
        history_texts = []
        for ch in candidate.get("career_history", []):
            history_texts.append(f"{ch.get('title', '')} {ch.get('description', '')}")
        history_text = " ".join(history_texts)
        
        # Extract features
        sim_profile = self.get_semantic_similarity(summary_text)
        sim_history = self.get_semantic_similarity(history_text)
        
        title_rel = self.compute_title_relevance(candidate)
        skills_scores = self.compute_skills_score(candidate)
        exp_fit = self.compute_experience_fit(candidate)
        tenure = self.compute_tenure_score(candidate)
        location = self.compute_location_suitability(candidate)
        notice = self.compute_notice_period_score(candidate)
        behavior = self.compute_behavior_score(candidate, evaluation_date_str)
        
        risk = self.is_suspicious_profile(candidate, config.CONSULTING_FIRMS, evaluation_date_str)
        
        return {
            "candidate_id": candidate.get("candidate_id"),
            "sim_profile": sim_profile,
            "sim_history": sim_history,
            "title_relevance": title_rel,
            "skills_required_score": skills_scores["required_score"],
            "skills_preferred_score": skills_scores["preferred_score"],
            "experience_fit": exp_fit,
            "tenure_score": tenure,
            "location_suitability": location,
            "notice_period_score": notice,
            "behavior_activity": behavior["activity"],
            "behavior_responsiveness": behavior["responsiveness"],
            "behavior_reliability": behavior["reliability"],
            "risk_flag": risk
        }
