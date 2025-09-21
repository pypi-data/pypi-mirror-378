from prefect import get_run_logger
from nemo_library_etl.adapter._utils.enums import ETLAdapter, ETLStep
from nemo_library_etl.adapter._utils.file_handler import ETLFileHandler
from nemo_library_etl.adapter.gedys.config_models import PipelineGedys
from nemo_library_etl.adapter.gedys.enums import GedysTransformStep
from nemo_library.core import NemoLibrary
import pandas as pd

from features.fileingestion import ReUploadDataFrame


class GedysLoad:
    
    def __init__(self, cfg:PipelineGedys):

        nl = NemoLibrary()
        self.config = nl.config
        self.logger = get_run_logger()
        self.cfg = cfg

        super().__init__()

    def load(self) -> None:
        self.logger.info("Loading all Gedys objects")

        fh = ETLFileHandler()

        if self.cfg.load_tables:
            for table, model in self.cfg.extract.tables.items():

                data = fh.readJSON(
                    adapter=ETLAdapter.GEDYS,
                    step=ETLStep.TRANSFORM,
                    substep=GedysTransformStep.FLATTEN,
                    entity=table,
                    ignore_nonexistent=True,  # Ignore if file does not exist
                )
                if not data:
                    self.logger.warning(
                        f"No data found for entity {table}. Skipping load."
                    )
                    continue

                # Convert to DataFrame for loading
                df = pd.DataFrame(data)
                if df.empty:
                    self.logger.warning(
                        f"No data to load for entity {table}. Skipping load."
                    )
                    continue

                self.logger.info(f"Loading data for entity {table}")
                ReUploadDataFrame(
                    config=self.config,
                    projectname=f"{self.cfg.NemoProjectPrefix}{table}",
                    df=df,
                    update_project_settings=False,
                )

        if self.cfg.load_joined:
            data = fh.readJSON(
                adapter=ETLAdapter.GEDYS,
                step=ETLStep.TRANSFORM,
                substep=GedysTransformStep.JOIN,
                entity="Company Joined",
                ignore_nonexistent=True,  # Ignore if file does not exist
            )
            if not data:
                self.logger.warning(
                    f"No data found for entity Company Joined. Skipping load."
                )
                return
            
            # Convert to DataFrame for loading
            df = pd.DataFrame(data)
            if df.empty:
                self.logger.warning(
                    f"No data to load for entity Company Joined. Skipping load."
                )
                return

            self.logger.info(f"Loading data for entity Company Joined")
            ReUploadDataFrame(
                config=self.config,
                projectname=f"{self.cfg.NemoProjectPrefix}Company_Joined",
                df=df,
                update_project_settings=False,
            )            