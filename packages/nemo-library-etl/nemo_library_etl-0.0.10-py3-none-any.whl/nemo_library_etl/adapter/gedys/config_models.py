from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


# Per-table extras for Gedys
class TableGedys(BaseModel):
    GUID: UUID
    active: bool = True
    history: bool = False  # Whether to include record history in extraction
    sentiment_analysis_fields: Optional[List[str]] = None  # Fields for sentiment analysis


# Optional full pipeline model for stricter Gedys-wide validation
class ExtractGedys(BaseModel):
    tables: Dict[str, TableGedys] = Field(default_factory=dict)

class TransformGedys(BaseModel):
    sentiment_analysis: bool = True
    flatten: bool = True
    join: bool = True

class PipelineGedys(BaseModel):
    config_version: str = "0.0.1"
    URL: str = "https://x-test.crm2host.com/gedys"
    chunksize: int = 100
    maxrecords: int | None = None # Optional limit on total records to extract
    load_tables: bool = True
    load_joined: bool = True
    NemoProjectPrefix: str = "gedys_"
    extract: ExtractGedys = Field(default_factory=ExtractGedys)
    transform: TransformGedys = Field(default_factory=TransformGedys)
    load: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")


# Expose the adapter models for the loader:
TABLE_MODEL = TableGedys
PIPELINE_MODEL = PipelineGedys
