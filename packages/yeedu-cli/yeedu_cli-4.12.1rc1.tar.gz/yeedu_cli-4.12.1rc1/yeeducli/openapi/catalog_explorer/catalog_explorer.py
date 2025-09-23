from yeeducli.utility.json_utils import response_validator
from yeeducli.utility.request_utils import Requests
from yeeducli.utility.logger_utils import Logger
from yeeducli import config
import requests
import sys

logger = Logger.get_logger(__name__, True)


class CatalogExplorer:

    def list_catalogs(metastore_catalog_id, workspace_id):
        try:
            url = f"{config.YEEDU_RESTAPI_URL}/metastore/{metastore_catalog_id}/catalogs"

            response = Requests(
                url=url,
                method="GET",
                headers=config.headers,
                params={
                    "workspace_id": workspace_id
                }
            ).send_http_request()

            return response_validator(response)
        except requests.exceptions.RequestException as e:
            logger.exception(f"Failed to connect due to {e}")
            sys.exit(-1)

    def list_schemas(metastore_catalog_id, workspace_id, catalog_name=None):
        try:
            url = f"{config.YEEDU_RESTAPI_URL}/metastore/{metastore_catalog_id}/schemas"

            response = Requests(
                url=url,
                method="GET",
                headers=config.headers,
                params={
                    "workspace_id": workspace_id,
                    "catalog_name": catalog_name
                }
            ).send_http_request()

            return response_validator(response)
        except requests.exceptions.RequestException as e:
            logger.exception(f"Failed to connect due to {e}")
            sys.exit(-1)

    def list_tables(metastore_catalog_id, workspace_id, schema_name, catalog_name=None):
        try:
            url = f"{config.YEEDU_RESTAPI_URL}/metastore/{metastore_catalog_id}/tables"

            response = Requests(
                url=url,
                method="GET",
                headers=config.headers,
                params={
                    "workspace_id": workspace_id,
                    "catalog_name": catalog_name,
                    "schema_name": schema_name
                }
            ).send_http_request()

            return response_validator(response)
        except requests.exceptions.RequestException as e:
            logger.exception(f"Failed to connect due to {e}")
            sys.exit(-1)

    def list_columns(metastore_catalog_id, workspace_id, schema_name, table_name, catalog_name=None):
        try:
            url = f"{config.YEEDU_RESTAPI_URL}/metastore/{metastore_catalog_id}/columns"

            response = Requests(
                url=url,
                method="GET",
                headers=config.headers,
                params={
                    "workspace_id": workspace_id,
                    "catalog_name": catalog_name,
                    "schema_name": schema_name,
                    "table_name": table_name
                }
            ).send_http_request()

            return response_validator(response)
        except requests.exceptions.RequestException as e:
            logger.exception(f"Failed to connect due to {e}")
            sys.exit(-1)

    def list_table_summaries(metastore_catalog_id, workspace_id, catalog_name=None, cached_tables=None):
        try:
            url = f"{config.YEEDU_RESTAPI_URL}/metastore/{metastore_catalog_id}/table_summaries"

            response = Requests(
                url=url,
                method="GET",
                headers=config.headers,
                params={
                    "workspace_id": workspace_id,
                    "catalog_name": catalog_name,
                    "cached_tables": cached_tables
                }
            ).send_http_request()

            return response_validator(response)
        except requests.exceptions.RequestException as e:
            logger.exception(f"Failed to connect due to {e}")
            sys.exit(-1)

    def get_table_ddl(metastore_catalog_id, workspace_id, cached_tables=None):
        try:
            url = f"{config.YEEDU_RESTAPI_URL}/metastore/{metastore_catalog_id}/table_ddl"
            response = Requests(
                url=url,
                method="GET",
                headers=config.headers,
                params={
                    "workspace_id": workspace_id,
                    "cached_tables": cached_tables
                }
            ).send_http_request()

            return response_validator(response)
        except requests.exceptions.RequestException as e:
            logger.exception(f"Failed to connect due to {e}")
            sys.exit(-1)

    def list_functions(metastore_catalog_id, workspace_id, catalog_name=None, schema_name=None):
        try:
            url = f"{config.YEEDU_RESTAPI_URL}/metastore/{metastore_catalog_id}/functions"
            response = Requests(
                url=url,
                method="GET",
                headers=config.headers,
                params={
                    "workspace_id": workspace_id,
                    "catalog_name": catalog_name,
                    "schema_name": schema_name
                }
            ).send_http_request()

            return response_validator(response)
        except requests.exceptions.RequestException as e:
            logger.exception(f"Failed to connect due to {e}")
            sys.exit(-1)

    def list_volumes(metastore_catalog_id, workspace_id, catalog_name=None, schema_name=None):
        try:
            url = f"{config.YEEDU_RESTAPI_URL}/metastore/{metastore_catalog_id}/volumes"
            response = Requests(
                url=url,
                method="GET",
                headers=config.headers,
                params={
                    "workspace_id": workspace_id,
                    "catalog_name": catalog_name,
                    "schema_name": schema_name
                }
            ).send_http_request()

            return response_validator(response)
        except requests.exceptions.RequestException as e:
            logger.exception(f"Failed to connect due to {e}")
            sys.exit(-1)
