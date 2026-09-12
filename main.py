import sys
import os
import asyncio
import json
import logging

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.pipeline.scraper import AsyncScraper
from src.llm.llm_orchestrator import LLMOrchestrator
from src.pipeline.entity_resolution import EntityResolutionEngine
from src.pipeline.graph_exporter import KnowledgeGraphExporter
from src.pipeline.csv_exporter import FullCSVExporter

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("MasterPipeline")

TARGET_URLS = [
    "https://httpbin.org/html"
]

async def run_pipeline():
    logger.info("=== Starting GraphOne Intelligence Pipeline ===")

    # 1. Scraping Phase (Playwright Headless Browser Enabled)
    logger.info("Phase 1: Rendering target URLs via Playwright...")
    scraper = AsyncScraper(concurrency=2)
    scraped_docs = await scraper.scrape_urls(TARGET_URLS, render_js=True)
    logger.info(f"Phase 1 Complete: Scraped {len(scraped_docs)} documents.")

    # 2. LLM Extraction Phase
    logger.info("Phase 2: Extracting entities via LLM Orchestrator...")
    orchestrator = LLMOrchestrator()
    schema_desc = "{'entities': [{'name': 'string', 'category': 'string', 'description': 'string', 'key_features': ['string']}]}"
    
    extracted_entities = []
    for doc in scraped_docs:
        raw_text = doc.get("content", "")
        if raw_text and len(raw_text) > 50:
            result = await orchestrator.extract_entity(raw_text, schema_desc)
            if result and isinstance(result, dict):
                extracted_entities.extend(result.get("entities", []))

    # 3. Entity Resolution Phase
    logger.info("Phase 3: Resolving and merging canonical entities...")
    resolver = EntityResolutionEngine(similarity_threshold=75.0)
    resolved_entities = resolver.resolve_and_merge(extracted_entities)
    logger.info(f"Phase 3 Complete: {len(resolved_entities)} unique canonical entities resolved.")

    # 4. Graph Construction Phase
    logger.info("Phase 4: Building Graph Representation...")
    exporter = KnowledgeGraphExporter()
    exporter.build_graph_from_entities(resolved_entities)
    exporter.export_to_json("data_graph.json")

    # 5. Multi-Tab CSV Artifact Generation
    logger.info("Phase 5: Exporting all 6 Google Sheets CSV Artifacts...")
    csv_writer = FullCSVExporter(output_dir="csv_output")
    csv_writer.export_tab_1_raw_ingestion(scraped_docs)
    csv_writer.export_tab_2_raw_extractions(extracted_entities)
    csv_writer.export_tab_3_canonical_entities(resolved_entities)
    csv_writer.export_tab_4_entity_resolution_audit(resolved_entities)
    csv_writer.export_tab_5_graph_nodes("data_graph.json")
    csv_writer.export_tab_6_graph_edges("data_graph.json")

    logger.info("=== Pipeline Execution Finished Successfully ===")

if __name__ == "__main__":
    asyncio.run(run_pipeline())
