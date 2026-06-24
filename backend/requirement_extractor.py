import re
from typing import Dict, Any, Tuple

class RequirementExtractor:
    def extract_experience(self, text: str) -> Tuple[int, int]:
        """
        Extract the target years of experience range (e.g. 5–9) from text.
        Returns a tuple of (min_exp, max_exp). Default is (5, 9).
        """
        # Matches patterns like '5-9 years' or '5 to 9 years' or '5–9 years'
        match = re.search(r"(\d+)\s*[-–to\s]+\s*(\d+)\s*years", text, re.IGNORECASE)
        if match:
            return int(match.group(1)), int(match.group(2))
        return (5, 9)

    def extract_locations(self, text: str) -> Dict[str, Any]:
        """
        Extract location parameters and preferred work mode configuration.
        """
        text_lower = text.lower()
        cities = []
        for city in ["Pune", "Noida", "Hyderabad", "Mumbai", "Delhi", "Bangalore", "Chennai"]:
            if city.lower() in text_lower:
                cities.append(city)
                
        hybrid = "hybrid" in text_lower
        remote = "remote" in text_lower
        
        return {
            "cities": cities,
            "hybrid_preferred": hybrid,
            "remote_allowed": remote
        }

    def extract_notice_period(self, text: str) -> int:
        """
        Extract the target notice period threshold in days.
        Default is 30 days.
        """
        text_lower = text.lower()
        if "sub-30" in text_lower or "30-day" in text_lower:
            return 30
        return 60
