import csv
import json
import logging
import os
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("CSVExporter")

class FullCSVExporter:
    def __init__(self, output_dir: str = "csv_output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def export_tab_1_raw_ingestion(self, scraped_docs: List[Dict[str, Any]]):
        """Tab 1: Raw Ingested Web Pages & URLs"""
        filepath = os.path.join(self.output_dir, "1_raw_sources.csv")
        fieldnames = ["source_url", "http_status", "content_length", "content_preview"]
        
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for doc in scraped_docs:
                content = doc.get("content", "")
                writer.writerow({
                    "source_url": doc.get("url", ""),
                    "http_status": doc.get("status", ""),
                    "content_length": len(content),
                    "content_preview": content[:150].replace("\n", " ").strip() if content else "FAILED_FETCH"
                })
        logger.info(f"[Tab 1] Exported raw sources to '{filepath}'")

    def export_tab_2_raw_extractions(self, extracted_entities: List[Dict[str, Any]]):
        """Tab 2: Unprocessed Raw LLM Extractions"""
        filepath = os.path.join(self.output_dir, "2_raw_extractions.csv")
        fieldnames = ["extracted_name", "category", "description", "raw_features"]
        
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for entity in extracted_entities:
                writer.writerow({
                    "extracted_name": entity.get("name", ""),
                    "category": entity.get("category", ""),
                    "description": entity.get("description", ""),
                    "raw_features": "; ".join(entity.get("key_features", [])) if isinstance(entity.get("key_features"), list) else str(entity.get("key_features", ""))
                })
        logger.info(f"[Tab 2] Exported raw extractions to '{filepath}'")

    def export_tab_3_canonical_entities(self, resolved_entities: List[Dict[str, Any]]):
        """Tab 3: Deduplicated Canonical Entities"""
        filepath = os.path.join(self.output_dir, "3_canonical_entities.csv")
        fieldnames = ["canonical_name", "category", "consolidated_description", "merged_features_count"]
        
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for entity in resolved_entities:
                features = entity.get("key_features", [])
                writer.writerow({
                    "canonical_name": entity.get("name", ""),
                    "category": entity.get("category", ""),
                    "consolidated_description": entity.get("description", ""),
                    "merged_features_count": len(features) if isinstance(features, list) else 0
                })
        logger.info(f"[Tab 3] Exported canonical entities to '{filepath}'")

    def export_tab_4_entity_resolution_audit(self, resolved_entities: List[Dict[str, Any]]):
        """Tab 4: Fuzzy Matching & Deduplication Audit Logs"""
        filepath = os.path.join(self.output_dir, "4_entity_resolution_audit.csv")
        fieldnames = ["canonical_entity", "merged_feature_list"]
        
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for entity in resolved_entities:
                features = entity.get("key_features", [])
                writer.writerow({
                    "canonical_entity": entity.get("name", ""),
                    "merged_feature_list": "; ".join(features) if isinstance(features, list) else str(features)
                })
        logger.info(f"[Tab 4] Exported resolution audit log to '{filepath}'")

    def export_tab_5_graph_nodes(self, graph_data_path: str = "data_graph.json"):
        """Tab 5: Knowledge Graph Nodes Index"""
        filepath = os.path.join(self.output_dir, "5_graph_nodes.csv")
        
        if not os.path.exists(graph_data_path):
            logger.warning(f"File {graph_data_path} not found. Skipping Tab 5 export.")
            return

        with open(graph_data_path, "r", encoding="utf-8") as f:
            graph_data = json.load(f)

        nodes = graph_data.get("nodes", [])
        
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["node_id", "node_type", "category"])
            writer.writeheader()
            for node in nodes:
                writer.writerow({
                    "node_id": node.get("id", ""),
                    "node_type": node.get("type", "Entity"),
                    "category": node.get("category", "N/A")
                })
        logger.info(f"[Tab 5] Exported graph nodes to '{filepath}'")

    def export_tab_6_graph_edges(self, graph_data_path: str = "data_graph.json"):
        """Tab 6: Knowledge Graph Directed Relationships"""
        filepath = os.path.join(self.output_dir, "6_graph_edges.csv")
        
        if not os.path.exists(graph_data_path):
            logger.warning(f"File {graph_data_path} not found. Skipping Tab 6 export.")
            return

        with open(graph_data_path, "r", encoding="utf-8") as f:
            graph_data = json.load(f)

        raw_edges = graph_data.get("links", []) or graph_data.get("edges", [])
        
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["source_node", "target_node", "relationship_type"])
            writer.writeheader()
            for edge in raw_edges:
                writer.writerow({
                    "source_node": edge.get("source", ""),
                    "target_node": edge.get("target", ""),
                    "relationship_type": edge.get("relation", "HAS_CAPABILITY")
                })
        logger.info(f"[Tab 6] Exported graph edges to '{filepath}'")
