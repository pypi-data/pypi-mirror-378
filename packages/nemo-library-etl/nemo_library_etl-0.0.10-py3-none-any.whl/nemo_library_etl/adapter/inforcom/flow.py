from prefect import flow, task, get_run_logger
from nemo_library_etl.adapter.inforcom.config_models import PipelineInforCOM
from nemo_library_etl.adapter._utils.config import load_pipeline_config
from nemo_library_etl.adapter.inforcom.extract import InforCOMExtract
from nemo_library_etl.adapter.inforcom.transform import InforCOMTransform
from nemo_library_etl.adapter.inforcom.load import InforCOMLoad


@flow(name="InforCOM ETL Flow", log_prints=True)
def inforcom_flow(
    bextract: bool = True,
    btransform: bool = True,
    bload: bool = True,
):
    logger = get_run_logger()
    logger.info("Starting InforCOM ETL Flow")

    # load config
    cfg = load_pipeline_config("InforCOM")

    # run steps
    if bextract:
        logger.info("Extracting objects from InforCOM")
        extract(cfg=cfg)

    if btransform:
        logger.info("Transforming InforCOM objects")
        transform(cfg=cfg)

    if bload:
        logger.info("Loading InforCOM objects")
        load(cfg=cfg)

    logger.info("InforCOM ETL Flow finished")


@task(name="Extract All Objects from InforCOM")
def extract(cfg:PipelineInforCOM):
    logger = get_run_logger()
    logger.info("Extracting all InforCOM objects")
    extractor = InforCOMExtract(cfg=cfg)
    extractor.extract()


@task(name="Transform Objects")
def transform(cfg:PipelineInforCOM):
    logger = get_run_logger()
    logger.info("Transforming InforCOM objects")
    transformer = InforCOMTransform(cfg=cfg)
    transformer.transform()

@task(name="Load Objects into Nemo")
def load(cfg:PipelineInforCOM):
    logger = get_run_logger()
    logger.info("Loading InforCOM objects into Nemo")
    loader = InforCOMLoad(cfg=cfg)
    loader.load()

