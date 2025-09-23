from argparse import SUPPRESS, ArgumentDefaultsHelpFormatter, ArgumentParser
from yeeducli.utility.json_utils import check_boolean, check_non_empty_string, validate_string_and_null
from yeeducli.utility.logger_utils import Logger

logger = Logger.get_logger(__name__, True)

class GlueCatalogParser:
    def glue_catalog_parser(subparser):
        databricks_subparsers = subparser.add_subparsers(dest="action", required=True)
        
        # create
        create_parser = databricks_subparsers.add_parser(
            "create",
            help="Create a new Glue metastore catalog",
            formatter_class=ArgumentDefaultsHelpFormatter
        )
        create_parser.add_argument(
            "--name", 
            type=check_non_empty_string, 
            nargs=1, 
            default=SUPPRESS, 
            required=True, 
            help="Specify the name of the Glue metastore catalog."
        )
        create_parser.add_argument(
            "--description", 
            type=check_non_empty_string, 
            nargs=1, 
            default=SUPPRESS, 
            help="Specify the description of the Glue metastore catalog."
        )
        create_parser.add_argument(
            "--json-output", 
            type=check_non_empty_string, 
            nargs='?', 
            choices=['pretty', 'default'], 
            default='pretty', 
            help="Specifies the format of JSON output."
        )
        create_parser.add_argument(
            "--yaml-output", 
            type=check_boolean, 
            nargs='?', 
            choices=['true', 'false'], 
            default='false', 
            help="Displays the information in YAML format if set to 'true'."
        )
        
        # edit
        edit_parser = databricks_subparsers.add_parser(
            "edit",
            help="Edit an existing Glue metastore catalog",
            formatter_class=ArgumentDefaultsHelpFormatter
        )
        edit_parser.add_argument(
            "--metastore_catalog_id", 
            type=int, 
            required=True, 
            default=SUPPRESS, 
            help="ID of the catalog to edit"
        )
        edit_parser.add_argument(
            "--name", 
            type=check_non_empty_string, 
            nargs=1, 
            default=SUPPRESS, 
            required=False, 
            help="Specify the name of the Glue metastore catalog."
        )
        edit_parser.add_argument(
            "--description", 
            type=validate_string_and_null, 
            nargs=1, 
            default=SUPPRESS, 
            help="Specify the description of the Glue metastore catalog."
        )
        edit_parser.add_argument(
            "--json-output", 
            type=check_non_empty_string, 
            nargs='?', 
            choices=['pretty', 'default'], 
            default='pretty', 
            help="Specifies the format of JSON output."
        )
        edit_parser.add_argument(
            "--yaml-output", 
            type=check_boolean, 
            nargs='?', 
            choices=['true', 'false'], 
            default='false', 
            help="Displays the information in YAML format if set to 'true'."
        )

        # delete
        delete_parser = databricks_subparsers.add_parser(
            "delete",
            help="Delete a Glue metastore catalog",
            formatter_class=ArgumentDefaultsHelpFormatter
        )
        delete_parser.add_argument(
            "--metastore_catalog_id",
            type=int,
            nargs=1,
            required=True,
            default=SUPPRESS,
            help="ID of the Glue metastore catalog to delete"
        )
        delete_parser.add_argument(
            "--json-output",
            type=check_non_empty_string,
            nargs='?',
            choices=['pretty', 'default'],
            default='pretty',
            help="Specifies the format of JSON output."
        )
        delete_parser.add_argument(
            "--yaml-output",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default='false',
            help="Displays the output in YAML format if set to true."
        )
    
