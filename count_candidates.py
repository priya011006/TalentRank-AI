import json
with open("data/sample_candidates.json", "r", encoding="utf-8") as f:
    candidates = json.load(f)
print(f"Total candidates: {len(candidates)}")