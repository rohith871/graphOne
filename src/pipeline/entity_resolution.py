import re
import logging
import json
from typing import List, Dict, Any
from rapidfuzz import process, fuzz

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("EntityResolver")

class EntityResolutionEngine:
    def __init__(self, similarity_threshold: float = 75.0):
        self.similarity_threshold = similarity_threshold
        self.entity_store: Dict[str, Dict[str, Any]] = {}
        self.noise_pattern = re.compile(r'\b(inc|corp|corporation|llc|ltd|ai|engine|platform|software)\b', re.IGNORECASE)

    def normalize_name(self, name: str) -> str:
        # Split camelCase / PascalCase words (e.g. "FrontierAtlas" -> "Frontier Atlas")
        split_camel = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        # Remove common noise words
        cleaned = self.noise_pattern.sub("", split_camel)
        # Remove non-alphanumeric chars
        cleaned = re.sub(r'[^\w\s]', '', cleaned)
        return " ".join(cleaned.split()).lower()

    def resolve_and_merge(self, incoming_entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        resolved_results = []

        for entity in incoming_entities:
            name = entity.get("name", "").strip()
            if not name:
                continue

            canonical_name = self._find_canonical_match(name)

            if canonical_name:
                logger.info(f"Resolved match: '{name}' -> Merging into Existing Entity '{canonical_name}'")
                merged = self._merge_entity_data(canonical_name, entity)
                resolved_results.append(merged)
            else:
                logger.info(f"New Entity Registered: '{name}'")
                self.entity_store[name] = entity
                resolved_results.append(entity)

        return resolved_results

    def _find_canonical_match(self, incoming_name: str) -> str:
        if not self.entity_store:
            return None

        norm_incoming = self.normalize_name(incoming_name)
        existing_names = list(self.entity_store.keys())

        # Direct check after camelCase split & normalization
        for existing in existing_names:
            if self.normalize_name(existing) == norm_incoming:
                return existing

        match = process.extractOne(
            norm_incoming,
            [self.normalize_name(n) for n in existing_names],
            scorer=fuzz.token_set_ratio
        )

        if match:
            _, score, index = match
            if score >= self.similarity_threshold:
                return existing_names[index]

        return None

    def _merge_entity_data(self, canonical_name: str, new_data: Dict[str, Any]) -> Dict[str, Any]:
        existing = self.entity_store[canonical_name]

        existing_features = set(existing.get("key_features", []))
        new_features = set(new_data.get("key_features", []))
        existing["key_features"] = list(existing_features.union(new_features))

        if len(new_data.get("description", "")) > len(existing.get("description", "")):
            existing["description"] = new_data["description"]

        self.entity_store[canonical_name] = existing
        return existing


if __name__ == "__main__":
    resolver = EntityResolutionEngine(similarity_threshold=75.0)

    batch_1 = [
        {"name": "GraphOne", "category": "Data Pipeline", "description": "High-throughput pipeline.", "key_features": ["bulk scraping"]},
        {"name": "FrontierAtlas", "category": "Resolution Engine", "description": "AI matching engine.", "key_features": ["graph linking"]}
    ]
    
    batch_2 = [
        {"name": "GraphOne Inc.", "category": "Data Pipeline", "description": "High-throughput bulk web scraping pipeline for enterprise.", "key_features": ["real-time streaming"]},
        {"name": "Frontier Atlas AI", "category": "Resolution Engine", "description": "AI matching engine.", "key_features": ["LLM fallback"]}
    ]

    print("--- Ingesting Batch 1 ---")
    resolver.resolve_and_merge(batch_1)

    print("\n--- Ingesting Batch 2 (Resolving Duplicates) ---")
    resolver.resolve_and_merge(batch_2)

    print("\nResolved Repository Entities:\n", json.dumps(list(resolver.entity_store.values()), indent=2))
