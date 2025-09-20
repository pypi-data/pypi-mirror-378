from prefect import get_run_logger
from nemo_library_etl.adapter._utils.enums import ETLAdapter, ETLStep
from nemo_library_etl.adapter._utils.generic_odbc import GenericODBCExtract
from nemo_library_etl.adapter.inforcom.config_models import PipelineInforCOM
from nemo_library_etl.adapter._utils.file_handler import ETLFileHandler
from nemo_library.core import NemoLibrary


class InforCOMExtract:

    def __init__(self, cfg: PipelineInforCOM):

        nl = NemoLibrary()
        self.config = nl.config
        self.logger = get_run_logger()
        self.cfg = cfg

        super().__init__()

    def extract(self) -> None:
        self.logger.info("Extracting all InforCOM objects")

        # extract objects
        odbc = GenericODBCExtract(
            odbc_connstr=self.cfg.odbc_connstr,
            timeout=self.cfg.timeout,
        )
        for table, model in self.cfg.extract.tables.items():
            if model.active is False:
                self.logger.info(f"Skipping inactive table: {table}")
                continue

            self.logger.info(f"Extracting table: {table}")
            odbc.generic_odbc_extract(
                query=f"SELECT * FROM {self.cfg.table_prefix}{table}",
                adapter=ETLAdapter.INFORCOM,
                step=ETLStep.EXTRACT,
                entity=table,
                chunksize=self.cfg.chunk_size if model.big_data else None,
                gzip_enabled=True,
            )
