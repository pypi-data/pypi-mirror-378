from prefect import get_run_logger
from nemo_library_etl.adapter.zentis.config_models import PipelineZentis
from nemo_library.core import NemoLibrary


class ZentisLoad:
    
    def __init__(self, cfg:PipelineZentis):

        self.nl = NemoLibrary()
        self.config = self.nl.config
        self.logger = get_run_logger()
        self.cfg = cfg

        super().__init__()

    def load(self) -> None:
        self.logger.info("Loading all Zentis objects")

        # load objects
                
        