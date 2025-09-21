from pathlib import Path
from prefect import get_run_logger
from nemo_library_etl.adapter._utils.datatype_handler import df_to_records_jsonsafe, normalize_na, read_csv_all_str, to_bool_nullable, to_datetime_safe, to_float64_mixed, to_int64_nullable
from nemo_library_etl.adapter._utils.enums import ETLAdapter, ETLStep
from nemo_library_etl.adapter.zentis.config_models import PipelineZentis
from nemo_library_etl.adapter._utils.file_handler import ETLFileHandler
from nemo_library.core import NemoLibrary
import pandas as pd

from nemo_library_etl.adapter.zentis.enums import ZentisLoadStep


class ZentisExtract:
    
    def __init__(self, cfg:PipelineZentis):

        self.nl = NemoLibrary()
        self.config = self.nl.config
        self.logger = get_run_logger()
        self.cfg = cfg

        super().__init__()
    
    def extract(self) -> None:
        self.logger.info("Extracting all Zentis objects")

        self._extract_fertigartikel()
        self._extract_rezepturdaten()

    def _extract_fertigartikel(self) -> None:
        """
        Extracts data for the Fertigartikel entity from the Zentis API.
        """

        df = read_csv_all_str(
            Path(__file__).parent.parent.parent.parent / "src_data" / ETLAdapter.ZENTIS.value / "V_NemoAI_Fertigartikel_IST_PLAN.csv"
        )
        df = normalize_na(df)

        # Float columns (nullable)
        float_cols: list[str] = [
            "VERPR",
            "STPRS",
            "MengeKG",
            "MengeVE",
            "NetErloes4",
        ]
        for c in float_cols:
            if c in df.columns:
                df[c] = to_float64_mixed(df[c])

        # Integers (nullable)
        int_cols = [
            "MATNR",
            "Anzahl",
            "Customer",
            "Reklamationsjahr",
        ]
        for c in int_cols:
            if c in df.columns:
                df[c] = to_int64_nullable(df[c])

        if "CALMONTH" in df.columns:
            # Expecting YYYYMM without separators
            df["CALMONTH"] = pd.to_datetime(
                df["CALMONTH"], format="%Y%m", errors="coerce"
            ).dt.to_period("M")

        for c in ["PLANIST", "MEINS", "MTART", "MMSTA"]:
            if c in df.columns:
                df[c] = df[c].astype("category")

        data = df_to_records_jsonsafe(df)

        # dump the data to a file
        filehandler = ETLFileHandler()
        filehandler.writeJSON(
            adapter=ETLAdapter.ZENTIS,
            step=ETLStep.EXTRACT,
            data=data,
            entity=ZentisLoadStep.FERTIGARTIKEL,
        )

    def _extract_rezepturdaten(self) -> None:
        """
        Extracts data for the Rezepturdaten entity from the Zentis API.
        """

        df = read_csv_all_str(
            Path(__file__).parent.parent.parent.parent / "src_data" / ETLAdapter.ZENTIS.value / "V_NemoAI_Rezepturdaten.csv"
        )
        df = normalize_na(df)

        # Floats (nullable) — accept both ',' and '.'
        float_cols = [
            "Stuecklistenpreis",
            "StuecklistenpreisEbene1",
            "StuecklistenpreisEbene2",
            "MengeBME",
            "MengeBMEEbene1",
            "Bruttokosten",
            "BruttokostenEbene1",
            "BruttokostenEbene2",
            "Bruttomenge_BMEEbene2",
            "MengeBMEEbene2",
            "VERPR",
            "STPRS",
        ]
        for c in float_cols:
            if c in df.columns:
                df[c] = to_float64_mixed(df[c])

        # Integers (nullable)
        int_cols = [
            "Fertigartikel",
            "Artikel",
            "SAP_Status",
            "SAP_Status_DE",
            "VersionsNr",
            "KundenSpezialRohware",
            "SpezialRohwareEbene1",
            "VersionsNr",
        ]
        for c in int_cols:
            if c in df.columns:
                df[c] = to_int64_nullable(df[c])

        # Datetime
        if "Gueltig_gesetzt_am" in df.columns:
            df["Gueltig_gesetzt_am"] = to_datetime_safe(df["Gueltig_gesetzt_am"])

        # categorical values
        yes_no_cols = [
            "Vegetarisch",
            "Vegan",
            "Laktosefrei",
            "Nussfrei",
            "Glutenfrei",
            "Ei-frei",
            "Lupinfrei",
            "Sojafrei",
            "ohne Propylenglycol",
            "keine Bestandteile vom Schwein",
            "Bio",
            "Baby",
            "ohne Gentechnik -DE-",
            "Kosher-fähig",
            "Halal-fähig",
            "RA Kakao MB",
            "RA Kaffee SG",
            "RA Haselnuss MB",
            "Fair Trade",
            "mit Palm(kern)/-derivate",
            "RSPO MB",
            "RSPO SG",
            "konform mit US-Gesetzgebung",
            "konform mit kan. Gesetzgebung",
            "ohne Palm(kern)/-derivate",
            "4c",
            "BIO Naturland",
            "BIO Bioland",
            "ProVeg",
        ]
        for c in yes_no_cols:
            if c in df.columns:
                df[c] = to_bool_nullable(df[c])

        data = df_to_records_jsonsafe(df)

        # dump the data to a file
        filehandler = ETLFileHandler()
        filehandler.writeJSON(
            adapter=ETLAdapter.ZENTIS,
            step=ETLStep.EXTRACT,
            data=data,
            entity=ZentisLoadStep.REZEPTURDATEN,
        )
