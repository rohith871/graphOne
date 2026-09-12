import json
import logging
import os
from neo4j import GraphDatabase

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("Neo4jExporter")

class Neo4jExporter:
    def __init__(self, uri: str = "bolt://localhost:7687", auth: tuple = ("neo4j", "password")):
        self.uri = uri
        self.auth = auth

    def stream_graph_to_neo4j(self, graph_data_path: str = "data_graph.json"):
        if not os.path.exists(graph_data_path):
            logger.error(f"Graph file {graph_data_path} not found.")
            return

        with open(graph_data_path, "r", encoding="utf-8") as f:
            graph_data = json.load(f)

        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("links", []) or graph_data.get("edges", [])

        try:
            with GraphDatabase.driver(self.uri, auth=self.auth) as driver:
                with driver.session() as session:
                    # Merge Nodes
                    for node in nodes:
                        session.run(
                            "MERGE (n:Entity {id: \}) SET n.type = \, n.category = \",
                            id=node.get("id"),
                            type=node.get("type", "Entity"),
                            category=node.get("category", "N/A")
                        )
                    # Merge Edges
                    for edge in edges:
                        session.run(
                            """
                            MATCH (a:Entity {id: \})
                            MATCH (b:Entity {id: \})
                            MERGE (a)-[r:HAS_CAPABILITY]->(b)
                            """,
                            source=edge.get("source"),
                            target=edge.get("target")
                        )
            logger.info(f"Successfully streamed {len(nodes)} nodes and {len(edges)} edges to Neo4j.")
        except Exception as e:
            logger.warning(f"Could not connect to Neo4j instance: {e}")

if __name__ == "__main__":
    exporter = Neo4jExporter()
    exporter.stream_graph_to_neo4j()
