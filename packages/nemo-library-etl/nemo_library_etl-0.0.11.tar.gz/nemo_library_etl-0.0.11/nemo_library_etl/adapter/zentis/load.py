"""
Zentis ETL Load Module.

This module handles the loading phase of the Zentis ETL pipeline.
It takes the transformed data and loads it into the target system, typically the
Nemo database or data warehouse.

The loading process typically includes:
1. Data validation before insertion
2. Connection management to target systems
3. Batch processing for efficient data loading
4. Error handling and rollback capabilities
5. Data integrity checks post-loading
6. Performance optimization for large datasets
7. Comprehensive logging throughout the process

Classes:
    ZentisLoad: Main class handling Zentis data loading.
"""

from prefect import get_run_logger
from nemo_library_etl.adapter.zentis.config_models import PipelineZentis
from nemo_library_etl.adapter._utils.enums import ETLAdapter, ETLStep
from nemo_library_etl.adapter._utils.file_handler import ETLFileHandler
from nemo_library import NemoLibrary
import pandas as pd

from nemo_library_etl.adapter.zentis.enums import ZentisLoadStep


class ZentisLoad:
    """
    Handles loading of transformed Zentis data into target system.
    
    This class manages the loading phase of the Zentis ETL pipeline,
    providing methods to insert transformed data into the target system with
    proper error handling, validation, and performance optimization.
    
    The loader:
    - Uses NemoLibrary for core functionality and configuration
    - Integrates with Prefect logging for pipeline visibility
    - Manages database connections and transactions
    - Provides batch processing capabilities
    - Handles data validation before insertion
    - Ensures data integrity and consistency
    - Optimizes performance for large datasets
    
    Attributes:
        nl (NemoLibrary): Core Nemo library instance for system integration.
        config: Configuration object from the Nemo library.
        logger: Prefect logger for pipeline execution tracking.
        cfg (PipelineZentis): Pipeline configuration with loading settings.
    """
    
    def __init__(self, cfg:PipelineZentis):
        """
        Initialize the ZentisLoad instance.
        
        Sets up the loader with the necessary library instances, configuration,
        and logging capabilities for the loading process.
        
        Args:
            cfg (PipelineZentis): Pipeline configuration object containing
                                                          loading settings and target system configuration.
        """
        self.nl = NemoLibrary()
        self.config = self.nl.config
        self.logger = get_run_logger()
        self.cfg = cfg

        super().__init__()

    def load(self) -> None:
        """
        Execute the main loading process for Zentis data.
        
        This method orchestrates the complete loading process by:
        1. Connecting to the target system (database, data warehouse, etc.)
        2. Loading transformed data from the previous ETL phase
        3. Validating data before insertion
        4. Performing batch inserts for optimal performance
        5. Handling errors and implementing rollback mechanisms
        6. Verifying data integrity post-insertion
        7. Updating metadata and audit tables
        8. Cleaning up temporary resources
        
        The method provides detailed logging for monitoring and debugging purposes
        and ensures transaction safety through proper error handling.
        
        Note:
            The actual loading logic needs to be implemented based on
            the target system requirements and data models.
        """
        self.logger.info("Loading all Zentis objects")

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

        self.nl.ReUploadDataFrame(
            projectname=f"zentis_{entity.value}",
            df=df,
            update_project_settings=False,
        )
                
        