
from yeeducli.utility.json_utils import check_non_empty_string, check_boolean
from argparse import SUPPRESS, ArgumentDefaultsHelpFormatter


class CatalogExplorerParser:
    def catalog_explorer_parser(subparser):
        list_catalogs = subparser.add_parser(
            'list-catalogs',
            help='To list catalogs for a metastore.',
            formatter_class=ArgumentDefaultsHelpFormatter)
        list_catalogs.add_argument(
            "--metastore_catalog_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="To list catalogs of a specific metastore"
        )
        list_catalogs.add_argument(
            "--workspace_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="To list catalogs of a metastore using the secrets of sepcific workspace."
        )
        list_catalogs.add_argument(
            "--json-output",
            type=check_non_empty_string,
            nargs='?',
            choices=['pretty', 'default'],
            default='pretty',
            help="Specifies the format of JSON output."
        )
        list_catalogs.add_argument(
            "--yaml-output",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default='false',
            help="Displays the information in YAML format if set to 'true'."
        )
        list_schemas = subparser.add_parser(
            'list-schemas',
            help='To list schemas for a metastore.',
            formatter_class=ArgumentDefaultsHelpFormatter)
        list_schemas.add_argument(
            "--metastore_catalog_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="To list schemas of for specific metastore"
        )
        list_schemas.add_argument(
            "--workspace_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="To list schemas of a metastore using the secrets of sepcific workspace."
        )
        list_schemas.add_argument(
            "--catalog_name",
            type=check_non_empty_string,
            nargs=1,
            default=SUPPRESS,
            help="To list schemas for a specific catalog."
        )
        list_schemas.add_argument(
            "--json-output",
            type=check_non_empty_string,
            nargs='?',
            choices=['pretty', 'default'],
            default='pretty',
            help="Specifies the format of JSON output."
        )
        list_schemas.add_argument(
            "--yaml-output",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default='false',
            help="Displays the information in YAML format if set to 'true'."
        )
        list_tables = subparser.add_parser(
            'list-tables',
            help='To list tables of a schema for a metastore.',
            formatter_class=ArgumentDefaultsHelpFormatter)
        list_tables.add_argument(
            "--metastore_catalog_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="To list tables of for specific metastore"
        )
        list_tables.add_argument(
            "--workspace_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="To list tables of a metastore using the secrets of sepcific workspace."
        )
        list_tables.add_argument(
            "--catalog_name",
            type=check_non_empty_string,
            nargs=1,
            default=SUPPRESS,
            help="To list tables for a specific catalog."
        )
        list_tables.add_argument(
            "--schema_name",
            type=check_non_empty_string,
            default=SUPPRESS,
            required=True,
            help="To list tables for a specific schema."
        )
        list_tables.add_argument(
            "--json-output",
            type=check_non_empty_string,
            nargs='?',
            choices=['pretty', 'default'],
            default='pretty',
            help="Specifies the format of JSON output."
        )
        list_tables.add_argument(
            "--yaml-output",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default='false',
            help="Displays the information in YAML format if set to 'true'."
        )
        list_columns = subparser.add_parser(
            'list-columns',
            help='To list columns of a table for a metastore.',
            formatter_class=ArgumentDefaultsHelpFormatter)
        list_columns.add_argument(
            "--metastore_catalog_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="To list columns of table for specific metastore"
        )
        list_columns.add_argument(
            "--workspace_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="To list columns of a table of using the secrets of sepcific workspace."
        )
        list_columns.add_argument(
            "--catalog_name",
            type=check_non_empty_string,
            nargs=1,
            default=SUPPRESS,
            help="To list columns of a tables for a specific catalog."
        )
        list_columns.add_argument(
            "--schema_name",
            type=check_non_empty_string,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="To list columns of a table for a specific schema."
        )
        list_columns.add_argument(
            "--table_name",
            type=check_non_empty_string,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="To list columns for a specific table."
        )
        list_columns.add_argument(
            "--json-output",
            type=check_non_empty_string,
            nargs='?',
            choices=['pretty', 'default'],
            default='pretty',
            help="Specifies the format of JSON output."
        )
        list_columns.add_argument(
            "--yaml-output",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default='false',
            help="Displays the information in YAML format if set to 'true'."
        )
        list_table_summaries = subparser.add_parser(
            'list-table-summaries',
            help='To list table summaries for a metastore.',
            formatter_class=ArgumentDefaultsHelpFormatter)
        list_table_summaries.add_argument(
            "--metastore_catalog_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="To list table summaries for specific metastore"
        )
        list_table_summaries.add_argument(
            "--workspace_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="To list table summaries by using the secrets of sepcific workspace."
        )
        list_table_summaries.add_argument(
            "--catalog_name",
            type=check_non_empty_string,
            nargs=1,
            default=SUPPRESS,
            help="To list columns of a tables for a specific catalog."
        )
        list_table_summaries.add_argument(
            "--cached_tables",
            type=check_non_empty_string,
            nargs=1,
            default=SUPPRESS,
            help="To list columns of a table for a specific schema."
        )
        list_table_summaries.add_argument(
            "--json-output",
            type=check_non_empty_string,
            nargs='?',
            choices=['pretty', 'default'],
            default='pretty',
            help="Specifies the format of JSON output."
        )
        list_table_summaries.add_argument(
            "--yaml-output",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default='false',
            help="Displays the information in YAML format if set to 'true'."
        )
        get_table_ddl = subparser.add_parser(
            'get-table-ddl',
            help='To list table ddl for a metastore.',
            formatter_class=ArgumentDefaultsHelpFormatter)
        get_table_ddl.add_argument(
            "--metastore_catalog_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="To list table summaries for specific metastore"
        )
        get_table_ddl.add_argument(
            "--workspace_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="To list table ddl of a metastore of sepcific workspace."
        )
        get_table_ddl.add_argument(
            "--cached_tables",
            type=check_non_empty_string,
            nargs=1,
            default=SUPPRESS,
            help="To list table ddl for a table."
        )
        get_table_ddl.add_argument(
            "--json-output",
            type=check_non_empty_string,
            nargs='?',
            choices=['pretty', 'default'],
            default='pretty',
            help="Specifies the format of JSON output."
        )
        get_table_ddl.add_argument(
            "--yaml-output",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default='false',
            help="Displays the information in YAML format if set to 'true'."
        )
        list_functions = subparser.add_parser(
            'list-functions',
            help='To list functions of a schema for a metastore.',
            formatter_class=ArgumentDefaultsHelpFormatter)
        list_functions.add_argument(
            "--metastore_catalog_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="The ID of the Metastore Catalog to retrieve functions from."
        )
        list_functions.add_argument(
            "--workspace_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="The ID of the workspace to retrieve functions for."
        )
        list_functions.add_argument(
            "--catalog_name",
            type=check_non_empty_string,
            nargs=1,
            default=SUPPRESS,
            help="The name of the catalog to retrieve functions from."
        )
        list_functions.add_argument(
            "--schema_name",
            type=check_non_empty_string,
            nargs=1,
            default=SUPPRESS,
            help="The name of the schema to retrieve functions from."
        )
        list_functions.add_argument(
            "--json-output",
            type=check_non_empty_string,
            nargs='?',
            choices=['pretty', 'default'],
            default='pretty',
            help="Specifies the format of JSON output."
        )
        list_functions.add_argument(
            "--yaml-output",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default='false',
            help="Displays the information in YAML format if set to 'true'."
        )
        list_volumes = subparser.add_parser(
            'list-volumes',
            help='To list volumes of a schema for a metastore.',
            formatter_class=ArgumentDefaultsHelpFormatter)
        list_volumes.add_argument(
            "--metastore_catalog_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="The ID of the Metastore Catalog to retrieve volumes from."
        )
        list_volumes.add_argument(
            "--workspace_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="The ID of the workspace to retrieve volumes for."
        )
        list_volumes.add_argument(
            "--catalog_name",
            type=check_non_empty_string,
            nargs=1,
            default=SUPPRESS,
            help="The name of the catalog to retrieve volumes from."
        )
        list_volumes.add_argument(
            "--schema_name",
            type=check_non_empty_string,
            nargs=1,
            default=SUPPRESS,
            help="The name of the schema to retrieve volumes from."
        )
        list_volumes.add_argument(
            "--json-output",
            type=check_non_empty_string,
            nargs='?',
            choices=['pretty', 'default'],
            default='pretty',
            help="Specifies the format of JSON output."
        )
        list_volumes.add_argument(
            "--yaml-output",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default='false',
            help="Displays the information in YAML format if set to 'true'."
        )
