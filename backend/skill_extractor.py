from typing import List, Dict

class SkillExtractor:
    # Predefined taxonomy of AI/ML skills related to the JD
    SKILL_TAXONOMY = {
        "embeddings": ["embedding", "sentence-transformer", "bge", "e5", "openai embedding"],
        "vector_db": ["pinecone", "weaviate", "qdrant", "milvus", "faiss", "vector database", "vector search"],
        "hybrid_search": ["opensearch", "elasticsearch", "hybrid search", "bm25"],
        "evaluation": ["ndcg", "mrr", "map", "eval", "evaluation framework"],
        "programming": ["python"],
        "llm_tuning": ["fine-tuning", "lora", "qlora", "peft", "llm fine-tuning"],
        "learning_to_rank": ["learning-to-rank", "learning to rank", "xgboost", "ltr"],
        "distributed_systems": ["distributed systems", "large-scale inference", "inference optimization"]
    }

    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """
        Scan lowercased job description text and map matched keywords 
        back to technical skill categories.
        """
        text_lower = text.lower()
        extracted = {}
        for category, keywords in self.SKILL_TAXONOMY.items():
            matched = []
            for kw in keywords:
                if kw in text_lower:
                    matched.append(kw)
            if matched:
                extracted[category] = matched
        return extracted
