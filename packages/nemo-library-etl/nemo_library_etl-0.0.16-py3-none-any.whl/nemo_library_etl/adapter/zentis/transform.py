"""
Zentis ETL Transform Module.

This module handles the transformation phase of the Zentis ETL pipeline.
It processes the extracted data, applies business rules, data cleaning, and formatting
to prepare the data for loading into the target system.

The transformation process typically includes:
1. Data validation and quality checks
2. Data type conversions and formatting
3. Business rule application
4. Data enrichment and calculated fields
5. Data structure normalization
6. Comprehensive logging throughout the process

Classes:
    ZentisTransform: Main class handling Zentis data transformation.
"""

from prefect import get_run_logger
from nemo_library_etl.adapter.zentis.config_models import PipelineZentis
from nemo_library_etl.adapter._utils.enums import ETLAdapter, ETLStep
from nemo_library_etl.adapter._utils.file_handler import ETLFileHandler
from nemo_library import NemoLibrary
import pandas as pd

from nemo_library_etl.adapter.zentis.enums import ZentisLoadStep


class ZentisTransform:
    """
    Handles transformation of extracted Zentis data.
    
    This class manages the transformation phase of the Zentis ETL pipeline,
    providing methods to process, clean, and format the extracted data for loading
    into the target system.
    
    The transformer:
    - Uses NemoLibrary for core functionality and configuration
    - Integrates with Prefect logging for pipeline visibility
    - Applies business rules and data validation
    - Handles data type conversions and formatting
    - Provides data enrichment and calculated fields
    - Ensures data quality and consistency
    
    Attributes:
        nl (NemoLibrary): Core Nemo library instance for system integration.
        config: Configuration object from the Nemo library.
        logger: Prefect logger for pipeline execution tracking.
        cfg (PipelineZentis): Pipeline configuration with transformation settings.
    """
    
    def __init__(self, cfg:PipelineZentis):
        """
        Initialize the ZentisTransform instance.
        
        Sets up the transformer with the necessary library instances, configuration,
        and logging capabilities for the transformation process.
        
        Args:
            cfg (PipelineZentis): Pipeline configuration object containing
                                                          transformation settings and rules.
        """
        self.nl = NemoLibrary()
        self.config = self.nl.config
        self.logger = get_run_logger()
        self.cfg = cfg

        super().__init__()

    def transform(self) -> None:
        """
        Execute the main transformation process for Zentis data.
        
        This method orchestrates the complete transformation process by:
        1. Loading extracted data from the previous ETL phase
        2. Applying data validation and quality checks
        3. Performing data type conversions and formatting
        4. Applying business rules and logic
        5. Creating calculated fields and data enrichment
        6. Ensuring data consistency and integrity
        7. Preparing data for the loading phase
        
        The method provides detailed logging for monitoring and debugging purposes
        and handles errors gracefully to ensure pipeline stability.
        
        Note:
            The actual transformation logic needs to be implemented based on
            the specific Zentis system requirements and business rules.
        """
        self.logger.info("Transforming all Zentis objects")

        # transform objects
        self.beautify()
        self.join()
                
    def beautify(self) -> None:
        filehandler = ETLFileHandler()

        # FERTIGARTIKEL
        fertigartikel = filehandler.readJSON(
            adapter=ETLAdapter.ZENTIS,
            step=ETLStep.EXTRACT,
            entity=ZentisLoadStep.FERTIGARTIKEL,
        )
        # no transformation
        filehandler.writeJSON(
            adapter=ETLAdapter.ZENTIS,
            step=ETLStep.TRANSFORM,
            data=fertigartikel,
            entity=ZentisLoadStep.FERTIGARTIKEL,
        )
        
        # REZEPTURDATEN
        rezepturdaten = filehandler.readJSON(
            adapter=ETLAdapter.ZENTIS,
            step=ETLStep.EXTRACT,
            entity=ZentisLoadStep.REZEPTURDATEN,
        )
        # Iterate through all dicts and rename key "4c" to "RENAMED_4c"
        for record in rezepturdaten:
            if "4c" in record:
                record["RENAMED_4c"] = record.pop("4c")        
                
        filehandler.writeJSON(
            adapter=ETLAdapter.ZENTIS,
            step=ETLStep.TRANSFORM,
            data=rezepturdaten,
            entity=ZentisLoadStep.REZEPTURDATEN,
        )

    def join(self) -> None:
        filehandler = ETLFileHandler()
        fertigartikel = filehandler.readJSON(
            adapter=ETLAdapter.ZENTIS,
            step=ETLStep.TRANSFORM,
            entity=ZentisLoadStep.FERTIGARTIKEL,
        )
        rezepturdaten = filehandler.readJSON(
            adapter=ETLAdapter.ZENTIS,
            step=ETLStep.TRANSFORM,
            entity=ZentisLoadStep.REZEPTURDATEN,
        )
        dffertigartikel = pd.DataFrame(fertigartikel)
        dfrezepturdaten = pd.DataFrame(rezepturdaten)
        dffertigartikel.columns = [f"Fertigartikel_{col}" for col in dffertigartikel.columns]
        dfrezepturdaten.columns = [f"Rezeptur_{col}" for col in dfrezepturdaten.columns]

        joined = pd.merge(
            dffertigartikel,
            dfrezepturdaten,
            left_on="Fertigartikel_MATNR",
            right_on="Rezeptur_Fertigartikel",
            how="outer",
            indicator=True,
        )

        # Map merge indicator to readable status
        status_map = {
            "both": "matched_both",
            "left_only": "only_fertigartikel",
            "right_only": "only_rezeptur",
        }
        joined["match_status"] = joined["_merge"].map(status_map)

        # (Optional) keep the original merge indicator or drop it
        joined.drop(columns=["_merge"], inplace=True)

        filehandler.writeJSON(
            adapter=ETLAdapter.ZENTIS,
            step=ETLStep.TRANSFORM,
            data=joined.to_dict(orient="records"),
            entity=ZentisLoadStep.JOINED_DATA,
        )
                        
                        
        