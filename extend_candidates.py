import json

# Load the original sample
with open("data/sample_candidates.json", "r", encoding="utf-8") as f:
    original = json.load(f)

# Duplicate the candidates and modify candidate IDs to be unique
extended = []
for i in range(2):
    for candidate in original:
        new_candidate = candidate.copy()
        # Modify candidate ID to be unique
        new_candidate["candidate_id"] = f"CAND_{str(i*50 + int(candidate['candidate_id'].split('_')[1])).zfill(7)}"
        extended.append(new_candidate)

# Save the extended sample
with open("data/sample_candidates.json", "w", encoding="utf-8") as f:
    json.dump(extended, f, indent=2, ensure_ascii=False)

print(f"Extended sample to {len(extended)} candidates")