from prefect import flow, task, get_run_logger
from nemo_library_etl.adapter.hubspot.config_models import PipelineHubSpot
from nemo_library_etl.adapter._utils.config import load_pipeline_config
from nemo_library_etl.adapter.hubspot.extract import HubSpotExtract
from nemo_library_etl.adapter.hubspot.transform import HubSpotTransform
from nemo_library_etl.adapter.hubspot.load import HubSpotLoad


@flow(name="HubSpot ETL Flow", log_prints=True)
def hubspot_flow(
    bextract: bool = True,
    btransform: bool = True,
    bload: bool = True,
):
    logger = get_run_logger()
    logger.info("Starting HubSpot ETL Flow")

    # load config
    cfg = load_pipeline_config("HubSpot")

    # run steps
    if bextract:
        logger.info("Extracting objects from HubSpot")
        extract(cfg=cfg)

    if btransform:
        logger.info("Transforming HubSpot objects")
        transform(cfg=cfg)

    if bload:
        logger.info("Loading HubSpot objects")
        load(cfg=cfg)

    logger.info("HubSpot ETL Flow finished")


@task(name="Extract All Objects from HubSpot")
def extract(cfg:PipelineHubSpot):
    logger = get_run_logger()
    logger.info("Extracting all HubSpot objects")
    extractor = HubSpotExtract(cfg=cfg)
    extractor.extract()


@task(name="Transform Objects")
def transform(cfg:PipelineHubSpot):
    logger = get_run_logger()
    logger.info("Transforming HubSpot objects")
    transformer = HubSpotTransform(cfg=cfg)
    transformer.transform()

@task(name="Load Objects into Nemo")
def load(cfg:PipelineHubSpot):
    logger = get_run_logger()
    logger.info("Loading HubSpot objects into Nemo")
    loader = HubSpotLoad(cfg=cfg)
    loader.load()

