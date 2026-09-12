```markdown
# GraphOne Intelligence Engine

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Automated_Scraping-green?style=for-the-badge&logo=playwright&logoColor=white)
![Gemini](https://img.shields.io/badge/Google_Gemini-3.6_Flash-purple?style=for-the-badge&logo=googlegemini&logoColor=white)
![NetworkX](https://img.shields.io/badge/NetworkX-Graph_Topology-orange?style=for-the-badge)
![Neo4j](https://img.shields.io/badge/Neo4j-Cypher_Export-008CC1?style=for-the-badge&logo=neo4j&logoColor=white)

An asynchronous data ingestion, entity resolution, and graph construction pipeline built for processing web documents, extracting structured knowledge using Gemini 3.6 Flash, deduplicating entities with fuzzy matching, and exporting graph structures alongside multi-tab CSV analytics.

---

## Pipeline Architecture

```text
[ Web Sources / Target URLs ]
               │
               ▼
[ Stage 1: Async Ingestion Layer ] (httpx + Playwright Headless Browser)
               │
               ▼
[ Stage 2: LLM Extraction Orchestrator ] (Gemini 3.6 Flash + Pydantic Validation)
               │
               ▼
[ Stage 3: Entity Resolution Engine ] (RapidFuzz Token-Set Matching & Canonical Mapping)
               │
               ▼
[ Stage 4: Graph Topology Engine ] (NetworkX Directed Graph + Neo4j Exporter)
               │
               ▼
[ Stage 5: Relational Exporter ] (6-Tab CSV Audit Suite for Google Sheets)

```

---

## Key Features

* **Dual-Mode Web Scraping:** High-throughput static page fetching (`httpx`) with automatic fallback to dynamic DOM rendering via headless Chromium (`Playwright`).
* **Structured LLM Extraction:** Parses unstructured HTML prose into validated JSON entity schemas using Gemini 3.6 Flash with built-in retry mechanisms.
* **Fuzzy Entity Resolution:** Deduplicates raw extracted surface names into unified canonical entities using `RapidFuzz` token-set ratio matching.
* **Graph Topology & Serialization:** Constructs directed multigraphs using `NetworkX`, exports serialized `data_graph.json` files, and generates parameterized Cypher streams for Neo4j databases.
* **Multi-Tab CSV Analytics:** Generates a 6-tab audit suite formatted for direct Google Sheets ingestion.

---

## Directory Structure

```text
graphone-intelligence-engine/
├── csv_output/                  # Auto-generated 6-tab CSV analytics suite
│   ├── 1_raw_sources.csv
│   ├── 2_raw_extractions.csv
│   ├── 3_canonical_entities.csv
│   ├── 4_entity_resolution_audit.csv
│   ├── 5_graph_nodes.csv
│   └── 6_graph_edges.csv
├── src/
│   ├── llm/
│   │   └── llm_orchestrator.py  # Gemini extraction & structural retry logic
│   └── pipeline/
│       ├── csv_exporter.py      # Exports 6-tab CSV audit suite
│       ├── entity_resolution.py # Fuzzy matching & canonical deduplication
│       ├── graph_exporter.py    # NetworkX graph builder & JSON serializer
│       ├── neo4j_exporter.py    # Cypher query stream generator
│       └── scraper.py           # Async HTTPX & Playwright scrapers
├── data_graph.json              # Serialized graph output
├── main.py                      # Master pipeline entry point
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation

```

---

## Prerequisites & Installation

### 1. Environment Setup

Ensure Python 3.10+ is installed on your system. Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1

```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
playwright install chromium

```

### 3. Environment Variables

Set your Gemini API key:

```powershell
$env:GEMINI_API_KEY="your-gemini-api-key"

```

---

## Execution

Run the master orchestrator script to execute the complete end-to-end pipeline:

```powershell
python main.py

```

---

## Output Artifacts

The engine outputs two main categories of data artifacts:

1. **`data_graph.json`**: Complete NetworkX directed graph containing nodes, attributes, and edge relationships.
2. **`csv_output/` Suite**:
* `1_raw_sources.csv`: Source URL audit logs and raw payload metrics.
* `2_raw_extractions.csv`: Unfiltered structured outputs directly from the LLM.
* `3_canonical_entities.csv`: Merged, deduplicated canonical entity records.
* `4_entity_resolution_audit.csv`: Lineage map connecting raw extractions to canonical IDs.
* `5_graph_nodes.csv`: Graph node list (Entities, Categories, Features).
* `6_graph_edges.csv`: Graph relationship list (`HAS_CAPABILITY`).



---

## Tech Stack

* **Language:** Python 3.10+
* **Ingestion:** `httpx`, `playwright`, `beautifulsoup4`
* **LLM Orchestration:** `google-genai` (Gemini 3.6 Flash), `pydantic`
* **Entity Resolution:** `rapidfuzz`
* **Graph Engine:** `networkx`, `neo4j`

```

```
