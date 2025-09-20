from prefect import get_run_logger
from nemo_library_etl.adapter._utils.enums import ETLAdapter, ETLStep
from nemo_library_etl.adapter._utils.file_handler import ETLFileHandler
from nemo_library_etl.adapter.zentis.config_models import PipelineZentis
from nemo_library_etl.adapter.zentis.enums import ZentisLoadStep
from nemo_library.core import NemoLibrary
import pandas as pd

class ZentisLoad:
    
    def __init__(self, cfg:PipelineZentis):

        self.nl = NemoLibrary()
        self.config = self.nl.config
        self.logger = get_run_logger()
        self.cfg = cfg

        super().__init__()

    def load(self) -> None:
        """
        Load the extracted and transformed data into Nemo.
        """
        filehandler = ETLFileHandler()

        for entity in ZentisLoadStep:
            
            data = filehandler.readJSON(
                adapter=ETLAdapter.ZENTIS,
                step=ETLStep.TRANSFORM,
                entity=entity,
            )
            self._load_data(entity, data)

    def _load_data(self, entity: ZentisLoadStep, data: list) -> None:
        """
        Loads the data into Nemo.
        """
        if not data:
            return

        self.logger.info(f"Loading {entity.value} data into Nemo")
        df = pd.DataFrame(data)
        
        ReUploadDataFrame(
            config=self.config,
            projectname=f"zentis_{entity.value}",
            df=df,
            update_project_settings=False,
        )

        