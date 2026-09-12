import sys
import os
import json
import asyncio
import logging
from typing import List, Dict, Any

# Ensure root path is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.llm.llm_orchestrator import LLMOrchestrator
from src.llm.schemas import ScrapingExtractionResult

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("IngestionPipeline")

class DataIngestionEngine:
    def __init__(self):
        self.orchestrator = LLMOrchestrator()
        self.schema_desc = """
        {
          "source_url": "string",
          "entities": [
            {
              "name": "string",
              "category": "string",
              "description": "string",
              "key_features": ["string"]
            }
          ]
        }
        """

    async def process_raw_document(self, url: str, raw_markdown: str) -> Dict[str, Any]:
        logger.info(f"Processing content from: {url}")
        prompt = f"Target URL: {url}\n\nDocument Content:\n{raw_markdown}"
        
        extracted_json = await self.orchestrator.extract_entity(
            raw_content=prompt,
            schema_description=self.schema_desc
        )

        if not extracted_json:
            logger.error(f"Failed to extract structured data for {url}")
            return {"source_url": url, "entities": []}

        # Validate with Pydantic
        try:
            if "source_url" not in extracted_json:
                extracted_json["source_url"] = url
            validated = ScrapingExtractionResult(**extracted_json)
            return validated.model_dump()
        except Exception as e:
            logger.warning(f"Schema validation error on {url}: {e}. Returning raw dict.")
            return extracted_json

if __name__ == "__main__":
    async def run_pipeline_test():
        engine = DataIngestionEngine()
        sample_doc = '''
        # FrontierAtlas Overview
        FrontierAtlas is an AI-powered entity resolution engine for enterprise graphs.
        Key capabilities include fast fuzzy matching, graph linking, and LLM fallback extraction.
        
        # GraphOne Data Pipeline
        GraphOne provides high-throughput bulk web scraping and real-time streaming ingestion.
        '''
        res = await engine.process_raw_document("https://example.com/tech-stack", sample_doc)
        print("\nExtracted Pipeline Output:\n", json.dumps(res, indent=2))

    asyncio.run(run_pipeline_test())
