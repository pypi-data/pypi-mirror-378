from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


# Per-table extras for InforCOM
class TableInforCOM(BaseModel):
    GUID: UUID
    active: bool = True
    big_data: bool = False
    description: Optional[str] = None

# Optional full pipeline model for stricter InforCOM-wide validation
class ExtractInforCOM(BaseModel):
    tables: Dict[str, TableInforCOM] = Field(default_factory=dict)


class PipelineInforCOM(BaseModel):
    config_version: str = "0.0.1"
    odbc_connstr: Optional[str] = None
    chunk_size: int = 1000
    timeout: int = 300
    table_prefix: str = "INFOR."
    extract: ExtractInforCOM = Field(default_factory=ExtractInforCOM)
    transform: Dict[str, Any] = Field(default_factory=dict)
    load: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")


# Expose the adapter models for the loader:
TABLE_MODEL = TableInforCOM
PIPELINE_MODEL = PipelineInforCOM
