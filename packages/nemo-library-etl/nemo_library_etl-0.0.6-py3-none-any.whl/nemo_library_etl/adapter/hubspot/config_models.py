from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


# Per-table extras for HubSpot
class TableHubSpot(BaseModel):
    GUID: UUID
    active: bool = True

# Optional full pipeline model for stricter HubSpot-wide validation
class ExtractHubSpot(BaseModel):
    tables: Dict[str, TableHubSpot] = Field(default_factory=dict)


class PipelineHubSpot(BaseModel):
    config_version: str = "0.0.1"
    deal_pipelines: Optional[List[str]] = Field(
        default_factory=lambda: ["*"],
        description="List of deal pipelines to include. Use ['*'] to include all.",
    )
    extract: ExtractHubSpot = Field(default_factory=ExtractHubSpot)
    transform: Dict[str, Any] = Field(default_factory=dict)
    load: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")


# Expose the adapter models for the loader:
TABLE_MODEL = TableHubSpot
PIPELINE_MODEL = PipelineHubSpot
