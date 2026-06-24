import json
from typing import Generator
from config import CANDIDATES_PATH

def stream_candidates(file_path=CANDIDATES_PATH) -> Generator[dict, None, None]:
    """
    generator that streams candidate profile dictionaries from JSONL line-by-line.
    Memory footprint remains O(1) per record.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str:
                yield json.loads(line_str)
