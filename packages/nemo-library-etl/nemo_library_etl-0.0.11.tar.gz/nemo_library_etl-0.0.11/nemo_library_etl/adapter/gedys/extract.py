"""
Gedys ETL Extract Module.

This module handles the extraction phase of the Gedys ETL pipeline.
It provides functionality to extract data from Gedys systems and 
prepare it for the transformation phase.

The extraction process:
1. Connects to the Gedys system using configured credentials
2. Iterates through configured tables and extracts data
3. Handles inactive tables by skipping them
4. Uses ETLFileHandler for data persistence
5. Provides comprehensive logging throughout the process

Classes:
    GedysExtract: Main class handling Gedys data extraction.
"""

import json
from prefect import get_run_logger
import requests
from nemo_library_etl.adapter._utils.enums import ETLAdapter, ETLStep
from nemo_library_etl.adapter.gedys.config_models import PipelineGedys
from nemo_library_etl.adapter._utils.file_handler import ETLFileHandler
from nemo_library.core import NemoLibrary


class GedysExtract:
    """
    Handles extraction of data from Gedys system.
    
    This class manages the extraction phase of the Gedys ETL pipeline,
    providing methods to connect to Gedys systems, retrieve data,
    and prepare it for subsequent transformation and loading phases.
    
    The extractor:
    - Uses NemoLibrary for core functionality and configuration
    - Integrates with Prefect logging for pipeline visibility
    - Processes tables based on configuration settings
    - Handles both active and inactive table configurations
    - Leverages ETLFileHandler for data persistence
    
    Attributes:
        nl (NemoLibrary): Core Nemo library instance for system integration.
        config: Configuration object from the Nemo library.
        logger: Prefect logger for pipeline execution tracking.
        cfg (PipelineGedys): Pipeline configuration with extraction settings.
    """
    
    def __init__(self, cfg:PipelineGedys):
        """
        Initialize the GedysExtract instance.
        
        Sets up the extractor with the necessary library instances, configuration,
        and logging capabilities for the extraction process.
        
        Args:
            cfg (PipelineGedys): Pipeline configuration object containing
                                                         extraction settings including table
                                                         configurations and activation flags.
        """
        self.nl = NemoLibrary()
        self.config = self.nl.config
        self.logger = get_run_logger()
        self.cfg = cfg
        self.gedys_token = self._get_token()

        super().__init__()
    
    def extract(self) -> None:
        """
        Execute the main extraction process for Gedys data.
        
        This method orchestrates the complete extraction process by:
        1. Logging the start of extraction
        2. Iterating through configured tables
        3. Skipping inactive tables
        4. Processing active tables and extracting their data
        5. Using ETLFileHandler for data persistence
        
        The method respects table activation settings and provides detailed
        logging for monitoring and debugging purposes.
        
        Note:
            The actual data extraction logic needs to be implemented based on
            the specific Gedys system requirements.
        """
        self.logger.info("Extracting all Gedys objects")

        # extract objects
        fh = ETLFileHandler()

        # Use a Session for connection pooling
        with requests.Session() as session:
            headers = {"Authorization": f"Bearer {self.gedys_token}"}

            for table, model in self.cfg.extract.tables.items():
                if model.active is False:
                    self.logger.info(f"Skipping inactive table: {table}")
                    continue

                self.logger.info(f"Extracting table: {table}")

                take = self.cfg.chunksize
                skip = 0
                total_count_reported = None
                total_written = 0

                # Open a streaming JSON array writer once per table
                with fh.streamJSONList(
                    adapter=ETLAdapter.GEDYS,  # Enum or "gedys" – both OK
                    step=ETLStep.EXTRACT,  # Enum or "extract" – both OK
                    entity=table,  # plain table name (used for file stem)
                ) as writer:

                    while True:
                        body = {
                            "Skip": skip,
                            "Take": take,
                        }
                        params = {
                            "includeRecordHistory": getattr(model, "history", False)
                        }

                        resp = session.post(
                            f"{self.cfg.URL}/rest/v1/records/list/{model.GUID}",
                            headers=headers,
                            json=body,
                            params=params,
                            timeout=60,
                        )

                        if resp.status_code != 200:
                            raise Exception(
                                f"request failed. Status: {resp.status_code}, error: {resp.text}, entity: {table}"
                            )

                        result = resp.json()
                        data = result.get("Data", []) or []
                        total_count = result.get("TotalCount", 0)
                        return_count = result.get("ReturnCount", len(data))

                        # Write this page immediately to disk (streamed JSON array)
                        if data:
                            writer.write_many(data)
                            total_written += len(data)

                        # First page: remember advertised total for logging
                        if total_count_reported is None:
                            total_count_reported = total_count

                        self.logger.info(
                            f"Received {return_count:,} records out of {total_count:,} "
                            f"(Skip: {skip:,}). Written so far: {total_written:,}."
                        )

                        skip += return_count
                        if (
                            return_count == 0
                            or skip >= total_count
                            or (
                                self.cfg.maxrecords
                                and total_written >= self.cfg.maxrecords
                            )
                        ):
                            break

                self.logger.info(
                    f"Finished {table}: wrote {total_written:,} records "
                    f"to {ETLStep.EXTRACT.value}/{table}."
                )

    def _get_token(self) -> str:
        data = {
            "username": self.config.get_gedys_user_id(),
            "password": self.config.get_gedys_password(),
        }
        response_auth = requests.post(
            f"{self.cfg.URL}/api/auth/login",
            data=data,
        )
        if response_auth.status_code != 200:
            raise Exception(
                f"request failed. Status: {response_auth.status_code}, error: {response_auth.text}"
            )
        token = json.loads(response_auth.text)
        return token["token"]