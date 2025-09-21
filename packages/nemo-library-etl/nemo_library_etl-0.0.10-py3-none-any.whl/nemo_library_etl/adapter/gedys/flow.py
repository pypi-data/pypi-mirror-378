from prefect import flow, task, get_run_logger
from nemo_library_etl.adapter.gedys.config_models import PipelineGedys
from nemo_library_etl.adapter._utils.config import load_pipeline_config
from nemo_library_etl.adapter.gedys.extract import GedysExtract
from nemo_library_etl.adapter.gedys.transform import GedysTransform
from nemo_library_etl.adapter.gedys.load import GedysLoad


@flow(name="Gedys ETL Flow", log_prints=True)
def gedys_flow(
    bextract: bool = True,
    btransform: bool = True,
    bload: bool = True,
):
    logger = get_run_logger()
    logger.info("Starting Gedys ETL Flow")

    # load config
    cfg = load_pipeline_config("Gedys")

    # run steps
    if bextract:
        logger.info("Extracting objects from Gedys")
        extract(cfg=cfg)

    if btransform:
        logger.info("Transforming Gedys objects")
        transform(cfg=cfg)

    if bload:
        logger.info("Loading Gedys objects")
        load(cfg=cfg)

    logger.info("Gedys ETL Flow finished")


@task(name="Extract All Objects from Gedys")
def extract(cfg:PipelineGedys):
    logger = get_run_logger()
    logger.info("Extracting all Gedys objects")
    extractor = GedysExtract(cfg=cfg)
    extractor.extract()


@task(name="Transform Objects")
def transform(cfg:PipelineGedys):
    logger = get_run_logger()
    logger.info("Transforming Gedys objects")
    transformer = GedysTransform(cfg=cfg)
    transformer.transform()

@task(name="Load Objects into Nemo")
def load(cfg:PipelineGedys):
    logger = get_run_logger()
    logger.info("Loading Gedys objects into Nemo")
    loader = GedysLoad(cfg=cfg)
    loader.load()

