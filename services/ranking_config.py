class RankingConfig:
    # Core weights (must sum to 1.0)
    WEIGHT_SEMANTIC = 0.35      # Profile text similarity with JD
    WEIGHT_SKILLS = 0.35        # Match on required and preferred skills
    WEIGHT_EXPERIENCE = 0.30    # Target experience range (5-9 years) and title relevance

    # Semantic sub-feature weights (must sum to 1.0)
    WEIGHT_SIM_PROFILE = 0.60   # Headline and summary TF-IDF
    WEIGHT_SIM_HISTORY = 0.40   # Career history description TF-IDF

    # Skill sub-feature weights (must sum to 1.0)
    WEIGHT_SKILLS_REQUIRED = 0.70  # Core skills: vector search, embeddings, python, ndcg
    WEIGHT_SKILLS_PREFERRED = 0.30 # Plus skills: fine-tuning, learning-to-rank, distributed systems

    # Experience sub-feature weights (must sum to 1.0)
    WEIGHT_EXP_FIT = 0.60          # 5-9 years target matching
    WEIGHT_TITLE_RELEVANCE = 0.40   # Target title keywords matching

    # Behavioral sub-feature weights (must sum to 1.0)
    WEIGHT_BEHAVIOR_ACTIVITY = 0.30       # Login recency
    WEIGHT_BEHAVIOR_RESPONSIVENESS = 0.40 # Recruiter response rate & response speed
    WEIGHT_BEHAVIOR_RELIABILITY = 0.30    # Interview completion & offer acceptance rates

    # Soft / Hard Filters
    FILTER_RISK_PROFILES = False          # Exclude honeypots, consulting-only, and stuffed profiles
    FILTER_LOCATION_INCOMPATIBLE = False  # Exclude candidates outside India or unwilling to relocate
