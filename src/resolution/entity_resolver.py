from rapidfuzz import process, fuzz
from typing import List, Dict, Any

class EntityResolver:
    def __init__(self, seed_canonical_entities: List[str]):
        self.seed_entities = seed_canonical_entities
        self.normalized_map = {self._clean(e): e for e in seed_canonical_entities}

    def _clean(self, text: str) -> str:
        text = text.lower()
        suffixes = ["inc", "inc.", "corp", "corporation", "llc", "ai", "labs", "io", "co"]
        words = [w for w in text.replace(",", "").replace(".", "").split() if w not in suffixes]
        return " ".join(words) if words else text

    def resolve(self, entity_name: str) -> Dict[str, Any]:
        cleaned = self._clean(entity_name)
        if cleaned in self.normalized_map:
            return {
                "rawName": entity_name,
                "canonicalName": self.normalized_map[cleaned],
                "confidence": 100.0,
                "matchType": "EXACT_NORMALIZED"
            }
        
        match = process.extractOne(cleaned, list(self.normalized_map.keys()), scorer=fuzz.token_set_ratio)
        if match and match[1] >= 85.0:
            return {
                "rawName": entity_name,
                "canonicalName": self.normalized_map[match[0]],
                "confidence": float(match[1]),
                "matchType": "FUZZY_TOKEN_SET"
            }
            
        return {
            "rawName": entity_name,
            "canonicalName": entity_name.strip(),
            "confidence": 0.0,
            "matchType": "UNRESOLVED_NEW"
        }
