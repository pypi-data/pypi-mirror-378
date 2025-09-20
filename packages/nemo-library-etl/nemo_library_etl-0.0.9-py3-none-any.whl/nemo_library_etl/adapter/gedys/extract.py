import json
from prefect import get_run_logger
import requests
from nemo_library_etl.adapter.gedys.config_models import PipelineGedys
from nemo_library_etl.adapter._utils.file_handler import ETLFileHandler
from nemo_library_etl.adapter._utils.enums import ETLAdapter, ETLStep
from nemo_library.core import NemoLibrary


class GedysExtract:

    def __init__(self, cfg: PipelineGedys):

        nl = NemoLibrary()
        self.config = nl.config
        self.logger = get_run_logger()
        self.cfg = cfg
        self.gedys_token = self._get_token()

        super().__init__()

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

    def extract(self) -> None:
        self.logger.info("Extracting all Gedys objects")

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
