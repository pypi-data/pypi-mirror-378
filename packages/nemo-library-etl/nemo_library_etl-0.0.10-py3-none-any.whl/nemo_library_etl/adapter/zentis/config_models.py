from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


# Per-table extras for Zentis
class TableZentis(BaseModel):
    GUID: UUID
    active: bool = True

# Optional full pipeline model for stricter Zentis-wide validation
class ExtractZentis(BaseModel):
    tables: Dict[str, TableZentis] = Field(default_factory=dict)


class PipelineZentis(BaseModel):
    config_version: str = "0.0.1"
    extract: ExtractZentis = Field(default_factory=ExtractZentis)
    transform: Dict[str, Any] = Field(default_factory=dict)
    load: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")


# Expose the adapter models for the loader:
TABLE_MODEL = TableZentis
PIPELINE_MODEL = PipelineZentis
