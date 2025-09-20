from prefect import flow, task, get_run_logger
from nemo_library_etl.adapter.zentis.config_models import PipelineZentis
from nemo_library_etl.adapter._utils.config import load_pipeline_config
from nemo_library_etl.adapter.zentis.extract import ZentisExtract
from nemo_library_etl.adapter.zentis.transform import ZentisTransform
from nemo_library_etl.adapter.zentis.load import ZentisLoad


@flow(name="Zentis ETL Flow", log_prints=True)
def zentis_flow(
    bextract: bool = True,
    btransform: bool = True,
    bload: bool = True,
):
    logger = get_run_logger()
    logger.info("Starting Zentis ETL Flow")

    # load config
    cfg = load_pipeline_config("Zentis")

    # run steps
    if bextract:
        logger.info("Extracting objects from Zentis")
        extract(cfg=cfg)

    if btransform:
        logger.info("Transforming Zentis objects")
        transform(cfg=cfg)

    if bload:
        logger.info("Loading Zentis objects")
        load(cfg=cfg)

    logger.info("Zentis ETL Flow finished")


@task(name="Extract All Objects from Zentis")
def extract(cfg:PipelineZentis):
    logger = get_run_logger()
    logger.info("Extracting all Zentis objects")
    extractor = ZentisExtract(cfg=cfg)
    extractor.extract()


@task(name="Transform Objects")
def transform(cfg:PipelineZentis):
    logger = get_run_logger()
    logger.info("Transforming Zentis objects")
    transformer = ZentisTransform(cfg=cfg)
    transformer.transform()

@task(name="Load Objects into Nemo")
def load(cfg:PipelineZentis):
    logger = get_run_logger()
    logger.info("Loading Zentis objects into Nemo")
    loader = ZentisLoad(cfg=cfg)
    loader.load()

