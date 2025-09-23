from yeeducli.openapi.catalog_explorer.catalog_explorer import CatalogExplorer
from yeeducli.utility.logger_utils import Logger
from yeeducli.utility.json_utils import *
import sys

logger = Logger.get_logger(__name__, True)


def list_catalogs(args):
    try:
        json_data = change_output(trim_namespace_json(args))

        response_json = CatalogExplorer.list_catalogs(
            json_data.get('metastore_catalog_id'),
            json_data.get('workspace_id')
        )

        confirm_output(response_json, json_data)
    except Exception as e:
        logger.exception(e)
        sys.exit(-1)


def list_schemas(args):
    try:
        json_data = change_output(trim_namespace_json(args))
        response_json = CatalogExplorer.list_schemas(
            json_data.get('metastore_catalog_id'),
            json_data.get('workspace_id'),
            json_data.get('catalog_name')
        )

        confirm_output(response_json, json_data)
    except Exception as e:
        logger.exception(e)
        sys.exit(-1)


def list_tables(args):
    try:
        json_data = change_output(trim_namespace_json(args))

        response_json = CatalogExplorer.list_tables(
            json_data.get('metastore_catalog_id'),
            json_data.get('workspace_id'),
            json_data.get('schema_name'),
            json_data.get('catalog_name'),
        )

        confirm_output(response_json, json_data)
    except Exception as e:
        logger.exception(e)
        sys.exit(-1)


def list_columns(args):
    try:
        json_data = change_output(trim_namespace_json(args))

        response_json = CatalogExplorer.list_columns(
            json_data.get('metastore_catalog_id'),
            json_data.get('workspace_id'),
            json_data.get('schema_name'),
            json_data.get('table_name'),
            json_data.get('catalog_name')
        )

        confirm_output(response_json, json_data)
    except Exception as e:
        logger.exception(e)
        sys.exit(-1)


def list_table_summaries(args):
    try:
        json_data = change_output(trim_namespace_json(args))

        response_json = CatalogExplorer.list_table_summaries(
            json_data.get('metastore_catalog_id'),
            json_data.get('workspace_id'),
            json_data.get('cached_tables'),
            json_data.get('catalog_name')
        )

        confirm_output(response_json, json_data)
    except Exception as e:
        logger.exception(e)
        sys.exit(-1)


def get_table_ddl(args):
    try:
        json_data = change_output(trim_namespace_json(args))

        response_json = CatalogExplorer.get_table_ddl(
            json_data.get('metastore_catalog_id'),
            json_data.get('workspace_id'),
            json_data.get('cached_tables')
        )

        confirm_output(response_json, json_data)
    except Exception as e:
        logger.exception(e)
        sys.exit(-1)


def list_functions(args):
    try:
        json_data = change_output(trim_namespace_json(args))

        response_json = CatalogExplorer.list_functions(
            json_data.get('metastore_catalog_id'),
            json_data.get('workspace_id'),
            json_data.get('catalog_name'),
            json_data.get('schema_name')
        )

        confirm_output(response_json, json_data)
    except Exception as e:
        logger.exception(e)
        sys.exit(-1)


def list_volumes(args):
    try:
        json_data = change_output(trim_namespace_json(args))

        response_json = CatalogExplorer.list_volumes(
            json_data.get('metastore_catalog_id'),
            json_data.get('workspace_id'),
            json_data.get('catalog_name'),
            json_data.get('schema_name')
        )

        confirm_output(response_json, json_data)
    except Exception as e:
        logger.exception(e)
        sys.exit(-1)
