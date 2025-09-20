from prefect import get_run_logger
from nemo_library_etl.adapter._utils.enums import ETLAdapter, ETLStep
from nemo_library_etl.adapter._utils.file_handler import ETLFileHandler
from nemo_library_etl.adapter.zentis.config_models import PipelineZentis
from nemo_library_etl.adapter.zentis.enums import ZentisLoadStep
from nemo_library.core import NemoLibrary
import pandas as pd


class ZentisTransform:
    
    def __init__(self, cfg:PipelineZentis):

        nl = NemoLibrary()
        self.config = nl.config
        self.logger = get_run_logger()
        self.cfg = cfg

        super().__init__()

    def transform(self) -> None:
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
        