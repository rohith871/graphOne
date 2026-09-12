import json
import logging
from typing import List, Dict, Any
import networkx as nx

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("GraphExporter")

class KnowledgeGraphExporter:
    def __init__(self):
        self.graph = nx.DiGraph()

    def build_graph_from_entities(self, resolved_entities: List[Dict[str, Any]]):
        for entity in resolved_entities:
            node_id = entity["name"]
            
            # Add entity node with metadata properties
            self.graph.add_node(
                node_id,
                type="Entity",
                category=entity.get("category", "Unknown"),
                description=entity.get("description", "")
            )
            logger.info(f"Added Node: [{node_id}] ({entity.get('category')})")

            # Link features as secondary attribute nodes
            for feature in entity.get("key_features", []):
                feature_node_id = f"Feature: {feature}"
                self.graph.add_node(feature_node_id, type="Feature")
                self.graph.add_edge(node_id, feature_node_id, relation="HAS_CAPABILITY")
                logger.info(f"Added Edge: [{node_id}] --(HAS_CAPABILITY)--> [{feature_node_id}]")

    def export_to_json(self, output_filepath: str = "output_graph.json"):
        data = nx.node_link_data(self.graph)
        with open(output_filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Successfully exported Graph structure to '{output_filepath}'")
        return data

if __name__ == "__main__":
    sample_resolved_entities = [
        {
            "name": "GraphOne",
            "category": "Data Pipeline",
            "description": "High-throughput bulk web scraping pipeline.",
            "key_features": ["real-time streaming", "bulk scraping"]
        },
        {
            "name": "FrontierAtlas",
            "category": "Resolution Engine",
            "description": "AI matching engine.",
            "key_features": ["LLM fallback", "graph linking"]
        }
    ]

    exporter = KnowledgeGraphExporter()
    exporter.build_graph_from_entities(sample_resolved_entities)
    exporter.export_to_json("data_graph.json")
