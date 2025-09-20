# nemo_library/adapter/_utils/file_handler.py
from datetime import date, datetime
from enum import Enum
import json
import logging
import gzip
from pathlib import Path
from contextlib import contextmanager
from typing import Iterable, Optional, Any

try:
    from prefect import get_run_logger  # type: ignore

    _PREFECT_AVAILABLE = True
except Exception:
    _PREFECT_AVAILABLE = False

from nemo_library.core import NemoLibrary


def _as_str(x: Any) -> str:
    """Return enum.value for Enums else str(x)."""
    return x.value if isinstance(x, Enum) else str(x)


def _slugify_filename(name: str | Enum) -> str:
    """Make a safe lowercase file stem from a human name."""
    import re

    if isinstance(name, Enum):
        name = name.value
    s = str(name)
    s = s.strip().lower()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^a-z0-9_]", "_", s)
    s = re.sub(r"_+", "_", s)
    return s.strip("_") or "table"


class ETLFileHandler:
    """
    JSON-only ETL file operations:
    - Pretty JSON write (single document)
    - Streaming write as a valid JSON array
    - Auto-detect gzip (.json.gz) on read & write
    """

    def __init__(self):
        nl = NemoLibrary()
        self.config = nl.config
        self.logger = self._init_logger()
        super().__init__()

    # ---------- logger ----------

    def _init_logger(self) -> logging.Logger:
        if _PREFECT_AVAILABLE:
            try:
                plogger = get_run_logger()
                plogger.info("Using Prefect run logger.")
                return plogger  # type: ignore[return-value]
            except Exception:
                pass

        logger_name = "nemo.etl"
        logger = logging.getLogger(logger_name)
        if not logger.handlers:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s %(levelname)s %(name)s: %(message)s",
            )
        logger.info(
            "Using standard Python logger (no active Prefect context detected)."
        )
        return logger

    # ---------- path helpers ----------

    def _output_path(
        self,
        adapter: str | Enum,
        step: str | Enum,
        substep: str | Enum | None,
        entity: Optional[str | Enum],
        filename: Optional[str],
        suffix: str,
    ) -> Path:
        """
        Build the path in the ETL directory structure and ensure parent exists.
        adapter: e.g. 'gedys' or ETLAdapter.GEDYS
        step: e.g. 'extract' or ETLStep.EXTRACT
        entity: table name (human string), used to derive file stem unless 'filename' is given
        """
        etl_dir = self.config.get_etl_directory()
        if not etl_dir:
            raise RuntimeError(
                "ETL directory is not configured (cfg.get_etl_directory())"
            )
        adapter_s = _as_str(adapter)
        step_s = _as_str(step)
        substep_s = _as_str(substep) if substep else None
        # prefer explicit filename; else derive from entity; else 'result'
        if filename:
            stem = _slugify_filename(filename)
        elif entity:
            stem = _slugify_filename(entity)
        else:
            stem = "result"
        # build directory path stepwise
        base = Path(etl_dir) / adapter_s / step_s
        if substep_s:
            base = base / substep_s

        p = base / f"{stem}{suffix}"
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    # ---------- (de)serialization helpers ----------

    def _json_default(self, o):
        """Default JSON serializer for datetimes, enums, and objects with to_dict()."""
        if hasattr(o, "to_dict") and callable(o.to_dict):
            return o.to_dict()
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if isinstance(o, Enum):
            return o.value
        return str(o)

    # ---------- utility methods ----------

    def _is_gz(self, path: Path) -> bool:
        return str(path).lower().endswith(".gz")

    def _open_text_auto(self, path: Path, mode: str):
        """
        Open text file; auto-detect gzip by file extension. Mode is 'r' or 'w' or 'a'.
        Always uses UTF-8 text encoding.
        """
        assert mode in ("r", "w", "a")
        if self._is_gz(path):
            return gzip.open(path, mode + "t", encoding="utf-8")
        else:
            return open(path, mode, encoding="utf-8")

    # ---------- read/write JSON (single document) ----------

    def readJSON(
        self,
        adapter: str | Enum,
        step: str | Enum,
        entity: str | None | Enum,
        filename: str | None = None,
        label: str | None = None,
        ignore_nonexistent: bool = False,
        substep: Optional[str | Enum] = None,
    ) -> dict | list:
        """
        Read a JSON document from the ETL output location, auto-detecting gzip.
        Tries <stem>.json then <stem>.json.gz; returns parsed JSON or {} / [] when empty.
        """
        base_path = self._output_path(adapter, step, substep, entity, filename, "")
        candidates = [base_path.with_suffix(".json"), base_path.with_suffix(".json.gz")]

        file_path = None
        for cand in candidates:
            if cand.exists():
                file_path = cand
                break

        obj_label = entity or label or "<unknown>"
        if file_path is None:
            if ignore_nonexistent:
                self.logger.warning(
                    f"No JSON file found for base {base_path}. Returning empty data for entity {obj_label}."
                )
                return {}
            raise FileNotFoundError(
                f"No JSON file found. Tried: {', '.join(str(c) for c in candidates)}"
            )

        with self._open_text_auto(file_path, "r") as f:
            data = json.load(f)

        if not data:
            self.logger.warning(
                f"No data found in file {file_path} for entity {obj_label}."
            )
            return {} if isinstance(data, dict) else []

        return data

    def writeJSON(
        self,
        adapter: str | Enum,
        step: str | Enum,
        data: dict | list[dict],
        entity: str | Enum | None,
        filename: str | None = None,
        label: str | None = None,
        gzip_enabled: bool = False,
        indent: int = 4,
        substep: Optional[str | Enum] = None,
    ) -> Path:
        """
        Write a dictionary or list of dictionaries as a single JSON document.
        If gzip_enabled=True, writes <stem>.json.gz, else <stem>.json.
        """
        suffix = ".json.gz" if gzip_enabled else ".json"
        file_path = self._output_path(adapter, step, substep, entity, filename, suffix)

        obj_label = (
            (entity.value if isinstance(entity, Enum) else entity) or label or "<unknown>"
        )
        if not data:
            self.logger.warning(
                f"No data to write for entity {obj_label}. Skipping file write."
            )
            return file_path

        with self._open_text_auto(file_path, "w") as f:
            json.dump(
                data, f, indent=indent, ensure_ascii=False, default=self._json_default
            )

        try:
            length_info = (
                f"{format(len(data), ',')} records"
                if hasattr(data, "__len__")
                else "Data"
            )
        except Exception:
            length_info = "Data"

        self.logger.info(
            f"{length_info} written to {file_path} for entity {obj_label}."
        )
        return file_path

    # ---------- streaming (valid JSON array) ----------

    @contextmanager
    def streamJSONList(
        self,
        adapter: str | Enum,
        step: str | Enum,
        entity: str | None,
        filename: str | None = None,
        label: str | None = None,
        gzip_enabled: bool = False,
        substep: Optional[str | Enum] = None,
    ):
        """
        Context manager that writes a *valid JSON array* incrementally:
        opens '[', streams items separated by ',', then closes ']'.
        """
        suffix = ".json.gz" if gzip_enabled else ".json"
        path = self._output_path(adapter, step, substep, entity, filename, suffix)

        if gzip_enabled:
            f = gzip.open(path, "wb")
            write_raw = lambda s: f.write(s.encode("utf-8"))
        else:
            f = open(path, "w", encoding="utf-8")
            write_raw = lambda s: f.write(s)

        first = True
        obj_label = entity or label or "<unknown>"

        class _Writer:
            def write_one(self_inner, rec: dict):
                nonlocal first
                if first:
                    write_raw("[")
                    first = False
                else:
                    write_raw(",\n")
                write_raw(
                    json.dumps(rec, ensure_ascii=False, default=self._json_default)
                )

            def write_many(self_inner, recs: Iterable[dict]):
                for rec in recs:
                    self_inner.write_one(rec)

            @property
            def path(self_inner) -> Path:
                return path

        try:
            yield _Writer()
        finally:
            if first:
                write_raw("[]")
            else:
                write_raw("]")
            f.close()
            self.logger.info(
                f"Streaming JSON list written to {path} for entity {obj_label}."
            )
