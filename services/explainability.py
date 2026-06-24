from typing import Dict, Any, List
import datetime
import config

class ExplainabilityEngine:
    def __init__(self):
        # Taxonomy to map raw skill names to professional display labels
        self.skill_display_map = {
            "embeddings": "Embeddings-based Retrieval",
            "vector_db": "Vector Databases",
            "hybrid_search": "Hybrid Search",
            "evaluation": "Ranking Evaluation Metrics",
            "programming": "Python Programming",
            "llm_tuning": "LLM Fine-tuning",
            "learning_to_rank": "Learning to Rank",
            "distributed_systems": "Distributed Systems"
        }

    def generate_explanation(self, scored_candidate: Dict[str, Any], evaluation_date_str: str = config.CURRENT_DATE) -> Dict[str, Any]:
        """
        Generate evidence-based explanation lists for a candidate's rank.
        Returns:
            Dict containing:
            - 'matched_skills': List of display-ready skill names.
            - 'strengths': List of statements detailing candidate fit.
            - 'concerns': List of statements detailing risks or gaps.
        """
        features = scored_candidate.get("features", {})
        profile = scored_candidate.get("profile", {})
        signals = scored_candidate.get("redrob_signals", {})
        skills = scored_candidate.get("skills", [])
        
        strengths = []
        concerns = []
        matched_skills_set = set()
        
        # 1. Skill Overlap Identification
        from services.feature_generator import FeatureGenerator
        # Define taxonomic categories to check
        categories = {
            "embeddings": ["embedding", "sentence-transformer", "bge", "e5", "openai embedding"],
            "vector_db": ["pinecone", "weaviate", "qdrant", "milvus", "faiss", "vector database", "vector search"],
            "hybrid_search": ["opensearch", "elasticsearch", "hybrid search", "bm25"],
            "evaluation": ["ndcg", "mrr", "map", "eval", "evaluation framework"],
            "programming": ["python"],
            "llm_tuning": ["fine-tuning", "lora", "qlora", "peft", "llm fine-tuning"],
            "learning_to_rank": ["learning-to-rank", "learning to rank", "xgboost", "ltr"],
            "distributed_systems": ["distributed systems", "large-scale inference", "inference optimization"]
        }
        
        for sk in skills:
            name_lower = sk.get("name", "").lower()
            for cat, keywords in categories.items():
                if any(kw in name_lower for kw in keywords):
                    matched_skills_set.add(self.skill_display_map[cat])
                    
        # 2. Experience relevance checks
        exp = profile.get("years_of_experience", 0)
        if 5.0 <= exp <= 9.0:
            strengths.append(f"Stated experience ({exp} years) aligns perfectly with the target 5-9 years range.")
        elif exp < 5.0:
            concerns.append(f"Stated experience ({exp} years) is below the preferred 5-9 years target range.")
        else:
            concerns.append(f"Stated experience ({exp} years) exceeds the 5-9 years target, indicating potential overqualification.")
            
        # Title relevance checks
        if features.get("title_relevance", 0.0) >= 0.8:
            strengths.append(f"Current or recent title ({profile.get('current_title')}) is highly relevant to AI/ML engineering.")
            
        # 3. Location alignment checks
        loc = profile.get("location", "")
        willing = signals.get("willing_to_relocate", False)
        if features.get("location_suitability", 0.0) == 1.0:
            strengths.append(f"Candidate is already local to {loc}, avoiding relocation requirements.")
        elif features.get("location_suitability", 0.0) == 0.8:
            strengths.append(f"Candidate resides in {loc} but is willing to relocate to Noida/Pune.")
        elif features.get("location_suitability", 0.0) == 0.3:
            concerns.append(f"Candidate is based in {loc} and has indicated they are unwilling to relocate.")
            
        # 4. Notice Period checks
        notice = signals.get("notice_period_days", 30)
        if notice <= 30:
            strengths.append(f"Short notice period ({notice} days) allows for immediate onboarding.")
        elif notice >= 90:
            concerns.append(f"Extended notice period ({notice} days) will delay hiring and onboarding.")
            
        # 5. Tenure Stability checks
        tenure = features.get("tenure_score", 1.0)
        if tenure == 1.0:
            strengths.append("Demonstrates a stable job history with solid average tenure per position.")
        elif tenure <= 0.5:
            concerns.append("Frequently changes companies (average job tenure is under 18 months).")
            
        # 6. Behavioral Signal checks
        # Active Date
        last_active = signals.get("last_active_date", "")
        try:
            la_date = datetime.datetime.strptime(last_active, "%Y-%m-%d").date()
            eval_date = datetime.datetime.strptime(evaluation_date_str, "%Y-%m-%d").date()
            days = (eval_date - la_date).days
            if days <= 15:
                strengths.append(f"High platform engagement (last active {days} days ago).")
            elif days >= 60:
                concerns.append(f"Low platform engagement (inactive for {days} days).")
        except Exception:
            pass
            
        # Recruiter response rate
        resp_rate = signals.get("recruiter_response_rate", 0.0)
        if resp_rate >= 0.8:
            strengths.append(f"Highly responsive to recruiters (response rate: {int(resp_rate * 100)}%).")
        elif resp_rate <= 0.4:
            concerns.append(f"Low responsiveness to recruiter messages (response rate: {int(resp_rate * 100)}%).")
            
        # Interview completion
        int_comp = signals.get("interview_completion_rate", 0.0)
        if int_comp >= 0.9:
            strengths.append(f"Excellent interview reliability (completion rate: {int(int_comp * 100)}%).")
        elif int_comp <= 0.6:
            concerns.append(f"Unreliable interview attendance (attendance rate: {int(int_comp * 100)}%).")

        return {
            "matched_skills": sorted(list(matched_skills_set)),
            "strengths": strengths,
            "concerns": concerns
        }

    def generate_explanation_text(self, scored_candidate: Dict[str, Any], rank: int) -> str:
        """
        Generate a formatted plain-text justification suitable for the
        reasoning column in the submission CSV file (limit to 1-2 concise sentences).
        """
        explanation = self.generate_explanation(scored_candidate)
        profile = scored_candidate.get("profile", {})
        exp = profile.get("years_of_experience", 0)
        title = profile.get("current_title", "")
        
        # Combine top points
        skills_matched = explanation["matched_skills"]
        skills_str = ", ".join(skills_matched[:3]) if skills_matched else "related technical skills"
        
        reasoning = f"{title} with {exp} years of experience. Matched skills: {skills_str}."
        
        if explanation["strengths"]:
            # Append the first strength
            reasoning += f" Strength: {explanation['strengths'][0]}"
        elif explanation["concerns"]:
            reasoning += f" Concern: {explanation['concerns'][0]}"
            
        # Cap length to ensure it is clean and fits nicely in standard output
        if len(reasoning) > 180:
            reasoning = reasoning[:177] + "..."
            
        return reasoning
