from prefect import get_run_logger
from nemo_library_etl.adapter._utils.enums import ETLAdapter, ETLStep
from nemo_library_etl.adapter._utils.file_handler import ETLFileHandler
from nemo_library_etl.adapter.hubspot.config_models import PipelineHubSpot
from nemo_library_etl.adapter.hubspot.enums import HubSpotLoadStep
from nemo_library.core import NemoLibrary


class HubSpotLoad:

    def __init__(self, cfg: PipelineHubSpot):

        nl = NemoLibrary()
        self.config = nl.config
        self.logger = get_run_logger()
        self.cfg = cfg

        super().__init__()

    def load(self) -> None:
        self.logger.info("Loading all HubSpot objects")

        # load objects
        self.load_forecast_call()

    def load_forecast_call(self) -> None:
        """
        Load forecast call data into the target system.
        """
        # Load transformed deals data
        filehandler = ETLFileHandler()
        deals = filehandler.readJSON(
            adapter=ETLAdapter.HUBSPOT,
            step=ETLStep.TRANSFORM,
            entity=HubSpotLoadStep.DEALS,
        )

        # dump the header
        header = [
            deal for deal in deals if deal.get("dealname").startswith("(FORECAST)")
        ]
        filehandler.writeJSON(
            adapter=ETLAdapter.HUBSPOT,
            step=ETLStep.LOAD,
            entity=HubSpotLoadStep.DEALS_FORECAST_HEADER,
            data=header,
        )

        # dump the deals itself
        forecast_deals = [
            deal
            for deal in deals
            if not deal.get("dealname", "").startswith("(FORECAST)")
            and deal.get("closedate")
            and deal.get("amount")
            and float(deal.get("amount")) > 0
            and not deal.get("dealstage") in ["Unqualified lead", "closed and lost"]
        ]
        filehandler.writeJSON(
            adapter=ETLAdapter.HUBSPOT,
            step=ETLStep.LOAD,
            entity=HubSpotLoadStep.DEALS_FORECAST_DEALS,
            data=forecast_deals,
        )
