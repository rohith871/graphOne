from pydantic import BaseModel, Field
from typing import List, Optional

class ExtractedEntity(BaseModel):
    name: str = Field(description="Name of the company, product, or tool")
    category: str = Field(description="Category (e.g., AI Framework, Database, SaaS)")
    description: Optional[str] = Field(None, description="Short summary of the entity")
    key_features: List[str] = Field(default_factory=list, description="List of primary features")

class ScrapingExtractionResult(BaseModel):
    source_url: str
    entities: List[ExtractedEntity]
