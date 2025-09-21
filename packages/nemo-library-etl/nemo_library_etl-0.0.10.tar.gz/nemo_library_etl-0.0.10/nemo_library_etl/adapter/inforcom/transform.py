from prefect import get_run_logger
from nemo_library_etl.adapter.inforcom.config_models import PipelineInforCOM
from nemo_library.core import NemoLibrary


class InforCOMTransform:
    
    def __init__(self, cfg:PipelineInforCOM):

        nl = NemoLibrary()
        self.config = nl.config
        self.logger = get_run_logger()
        self.cfg = cfg

        super().__init__()

    def transform(self) -> None:
        self.logger.info("Transforming all InforCOM objects")

        # transform objects
                
        