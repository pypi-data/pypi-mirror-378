from yeeducli.constants import NOTEBOOK_LANGUAGE_LIST, NOTEBOOK_LANG, SPARK_JOB_STATUS
from yeeducli.utility.json_utils import check_boolean, check_non_empty_string, validate_integer_and_null, validate_string_and_null, validate_array_of_intgers, check_choices
from argparse import SUPPRESS, ArgumentDefaultsHelpFormatter


class NotebookConfigurationParser:

    def notebook_configuration_parser(subparser):

        create_notebook_conf = subparser.add_parser(
            'create',
            help='To create a Notebook.',
            formatter_class=ArgumentDefaultsHelpFormatter)
        create_notebook_conf.add_argument(
            "--workspace_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="Provide workspace_id to create a Notebook."
        )
        create_notebook_conf.add_argument(
            "--cluster_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            help="Provide cluster_id to create a Notebook."
        )
        create_notebook_conf.add_argument(
            "--cluster_name",
            type=check_non_empty_string,
            nargs=1,
            default=SUPPRESS,
            help="Provide cluster_name to create a Notebook."
        )
        create_notebook_conf.add_argument(
            "--notebook_name",
            type=check_non_empty_string,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="Provide notebook_name to create a Notebook."
        )
        create_notebook_conf.add_argument(
            "--notebook_type",
            type=check_non_empty_string,
            nargs=1,
            default=SUPPRESS,
            metavar='python3,scala,sql',
            choices=NOTEBOOK_LANGUAGE_LIST,
            required=True,
            help="Provide notebook type to create a Notebook."
        )
        create_notebook_conf.add_argument(
            "--notebook_path",
            type=check_non_empty_string,
            nargs=1,
            default=SUPPRESS,
            help="Provide notebook_path to create a Notebook."
        )
        create_notebook_conf.add_argument(
            "--conf",
            type=check_non_empty_string,
            action='append',
            nargs='+',
            default=SUPPRESS,
            help="Provide conf to create a Notebook."
        )
        create_notebook_conf.add_argument(
            "--files",
            type=check_non_empty_string,
            nargs='?',
            default=SUPPRESS,
            help="Provide files to create a Notebook."
        )
        create_notebook_conf.add_argument(
            "--jars",
            type=check_non_empty_string,
            nargs='?',
            default=SUPPRESS,
            help="Provide jars to create a Notebook."
        )
        create_notebook_conf.add_argument(
            "--packages",
            type=check_non_empty_string,
            nargs='?',
            default=SUPPRESS,
            help="Provide packages to create a Notebook."
        )
        create_notebook_conf.add_argument(
            "--driver-memory",
            type=check_non_empty_string,
            nargs='?',
            default=SUPPRESS,
            help="Provide driver-memory to create a Notebook."
        )
        create_notebook_conf.add_argument(
            "--executor-memory",
            type=check_non_empty_string,
            nargs='?',
            default=SUPPRESS,
            help="Provide executor-memory to create a Notebook."
        )
        create_notebook_conf.add_argument(
            "--driver-cores",
            type=int,
            nargs='?',
            default=SUPPRESS,
            help="Provide driver-cores to create a Notebook."
        )
        create_notebook_conf.add_argument(
            "--total-executor-cores",
            type=int,
            nargs='?',
            default=SUPPRESS,
            help="Provide total-executor-cores to create a Notebook."
        )
        create_notebook_conf.add_argument(
            "--executor-cores",
            type=int,
            nargs='?',
            default=SUPPRESS,
            help="Provide executor-cores to create a Notebook."
        )
        create_notebook_conf.add_argument(
            "--num-executors",
            type=int,
            nargs='?',
            default=SUPPRESS,
            help="Provide num-executors to create a Notebook."
        )
        create_notebook_conf.add_argument(
            "--should_append_params",
            type=check_boolean,
            nargs='?',
            default=SUPPRESS,
            choices=['true', 'false'],
            help="Determines whether the job-level Spark configuration should append to or override the cluster-level Spark configuration."
        )
        create_notebook_conf.add_argument(
            "--json-output",
            type=check_non_empty_string,
            nargs='?',
            choices=['pretty', 'default'],
            default='pretty',
            help="Specifies the format of JSON output."
        )
        create_notebook_conf.add_argument(
            "--yaml-output",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default='false',
            help="Displays the information in YAML format if set to 'true'."
        )

        list_notebook_conf = subparser.add_parser(
            'list',
            help='To list all the available Notebooks.',
            formatter_class=ArgumentDefaultsHelpFormatter)
        list_notebook_conf.add_argument(
            "--workspace_id",
            type=int,
            nargs=1,
            required=True,
            default=SUPPRESS,
            help="To list Notebooks of a specific workspace."
        )
        list_notebook_conf.add_argument(
            "--enable",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default=SUPPRESS,
            help="Provide enable as true or false to list Notebooks of a specific workspace."
        )
        list_notebook_conf.add_argument(
            "--cluster_ids",
            type=validate_array_of_intgers,
            nargs='?',
            default=SUPPRESS,
            help="An optional set of cluster instance IDs to filter on."
        )
        list_notebook_conf.add_argument(
            "--language",
            type=lambda values: check_choices(values, choices=NOTEBOOK_LANG),
            nargs='?',
            default=SUPPRESS,
            help="An optional set of language filter for notebooks. Choices are: " +
            ", ".join(NOTEBOOK_LANG)
        )
        list_notebook_conf.add_argument(
            "--has_run",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default=SUPPRESS,
            help="Provide has_run as true or false to list Notebooks of a specific workspace."
        )
        list_notebook_conf.add_argument(
            "--last_run_status",
            type=lambda values: check_choices(
                values, choices=SPARK_JOB_STATUS),
            nargs='?',
            default=SUPPRESS,
            help="An optional set of last run statuses to filter notebooks. Choices are: " +
            ", ".join(SPARK_JOB_STATUS)
        )
        list_notebook_conf.add_argument(
            "--created_by_ids",
            type=validate_array_of_intgers,
            nargs='?',
            default=SUPPRESS,
            help="An optional set of created by user IDs to filter on."
        )
        list_notebook_conf.add_argument(
            "--modified_by_ids",
            type=validate_array_of_intgers,
            nargs='?',
            default=SUPPRESS,
            help="An optional set of modified by user IDs to filter on."
        )
        list_notebook_conf.add_argument(
            "--page_number",
            type=int,
            nargs=1,
            default=1,
            help="To list Notebooks for a specific page_number."
        )
        list_notebook_conf.add_argument(
            "--limit",
            type=int,
            nargs=1,
            default=100,
            help="Provide limit to list number of Notebooks."
        )
        list_notebook_conf.add_argument(
            "--json-output",
            type=check_non_empty_string,
            nargs='?',
            choices=['pretty', 'default'],
            default='pretty',
            help="Specifies the format of JSON output."
        )
        list_notebook_conf.add_argument(
            "--yaml-output",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default='false',
            help="Displays the information in YAML format if set to 'true'."
        )

        search_notebook_confs = subparser.add_parser(
            'search',
            help='To search Notebooks by notebook name in a workspace.',
            formatter_class=ArgumentDefaultsHelpFormatter)
        search_notebook_confs.add_argument(
            "--workspace_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="Provide workspace_id to search Notebooks in it."
        )
        search_notebook_confs.add_argument(
            "--notebook_name",
            type=check_non_empty_string,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="Provide notebook_name to search Notebooks."
        )
        search_notebook_confs.add_argument(
            "--enable",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default=SUPPRESS,
            help="Provide enable as true or false to search Notebooks."
        )
        search_notebook_confs.add_argument(
            "--cluster_ids",
            type=validate_array_of_intgers,
            nargs='?',
            default=SUPPRESS,
            help="An optional set of cluster instance IDs to filter on."
        )
        search_notebook_confs.add_argument(
            "--has_run",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default=SUPPRESS,
            help="Provide has_run as true or false to list Notebooks of a specific workspace."
        )
        search_notebook_confs.add_argument(
            "--language",
            type=lambda values: check_choices(values, choices=NOTEBOOK_LANG),
            nargs='?',
            default=SUPPRESS,
            help="An optional set of language filter for notebooks. Choices are: " +
            ", ".join(NOTEBOOK_LANG)
        )
        search_notebook_confs.add_argument(
            "--last_run_status",
            type=lambda values: check_choices(
                values, choices=SPARK_JOB_STATUS),
            nargs='?',
            default=SUPPRESS,
            help="An optional set of last run statuses to filter notebooks. Choices are: " +
            ", ".join(SPARK_JOB_STATUS)
        )
        search_notebook_confs.add_argument(
            "--created_by_ids",
            type=validate_array_of_intgers,
            nargs='?',
            default=SUPPRESS,
            help="An optional set of created by user IDs to filter on."
        )
        search_notebook_confs.add_argument(
            "--modified_by_ids",
            type=validate_array_of_intgers,
            nargs='?',
            default=SUPPRESS,
            help="An optional set of modified by user IDs to filter on."
        )
        search_notebook_confs.add_argument(
            "--page_number",
            type=int,
            nargs=1,
            default=1,
            help="To search Notebooks for a specific page_number."
        )
        search_notebook_confs.add_argument(
            "--limit",
            type=int,
            nargs=1,
            default=100,
            help="Provide limit to search number of Notebooks."
        )
        search_notebook_confs.add_argument(
            "--json-output",
            type=check_non_empty_string,
            nargs='?',
            choices=['pretty', 'default'],
            default='pretty',
            help="Specifies the format of JSON output."
        )
        search_notebook_confs.add_argument(
            "--yaml-output",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default='false',
            help="Displays the information in YAML format if set to 'true'."
        )

        get_notebook_conf = subparser.add_parser(
            'get',
            help='To get the information about a specific Notebook.',
            formatter_class=ArgumentDefaultsHelpFormatter)
        get_notebook_conf.add_argument(
            "--workspace_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="Provide workspace id to get information about a specific Notebook."
        )
        get_notebook_conf.add_argument(
            "--notebook_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            help="Provide Notebook Conf Id to get information about a specific Notebook."
        )
        get_notebook_conf.add_argument(
            "--notebook_name",
            type=check_non_empty_string,
            nargs=1,
            default=SUPPRESS,
            help="Provide Notebook Name to get information about a specific Notebook."
        )
        get_notebook_conf.add_argument(
            "--json-output",
            type=check_non_empty_string,
            nargs='?',
            choices=['pretty', 'default'],
            default='pretty',
            help="Specifies the format of JSON output."
        )
        get_notebook_conf.add_argument(
            "--yaml-output",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default='false',
            help="Displays the information in YAML format if set to 'true'."
        )

        edit_notebook_conf = subparser.add_parser(
            'edit',
            help='To edit the Notebook.',
            formatter_class=ArgumentDefaultsHelpFormatter)
        edit_notebook_conf.add_argument(
            "--workspace_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="Provide Workspace Id to edit a Notebook."
        )
        edit_notebook_conf.add_argument(
            "--notebook_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            help="Provide Notbeook Conf Id to edit a Notebook."
        )
        edit_notebook_conf.add_argument(
            "--notebook_name",
            type=check_non_empty_string,
            nargs=1,
            default=SUPPRESS,
            help="Provide Notebook Name to edit a Notebook."
        )
        edit_notebook_conf.add_argument(
            "--cluster_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            help="Provide cluster_id to edit a Notebook."
        )
        edit_notebook_conf.add_argument(
            "--cluster_name",
            type=check_non_empty_string,
            nargs=1,
            default=SUPPRESS,
            help="Provide cluster_name to edit a Notebook."
        )
        edit_notebook_conf.add_argument(
            "--name",
            type=check_non_empty_string,
            nargs='?',
            default=SUPPRESS,
            help="Provide name to edit notebook_name of a Notebook."
        )
        edit_notebook_conf.add_argument(
            "--conf",
            type=validate_string_and_null,
            action='append',
            nargs='+',
            default=SUPPRESS,
            help="Provide conf to edit a Notebook."
        )
        edit_notebook_conf.add_argument(
            "--files",
            type=validate_string_and_null,
            nargs='?',
            default=SUPPRESS,
            help="Provide files to edit a Notebook."
        )
        edit_notebook_conf.add_argument(
            "--jars",
            type=validate_string_and_null,
            nargs='?',
            default=SUPPRESS,
            help="Provide jars to edit a Notebook."
        )
        edit_notebook_conf.add_argument(
            "--packages",
            type=validate_string_and_null,
            nargs='?',
            default=SUPPRESS,
            help="Provide packages to edit a Notebook."
        )
        edit_notebook_conf.add_argument(
            "--driver-memory",
            type=validate_string_and_null,
            nargs='?',
            default=SUPPRESS,
            help="Provide driver-memory to edit a Notebook."
        )
        edit_notebook_conf.add_argument(
            "--executor-memory",
            type=validate_string_and_null,
            nargs='?',
            default=SUPPRESS,
            help="Provide executor-memory to edit a Notebook."
        )
        edit_notebook_conf.add_argument(
            "--driver-cores",
            type=validate_integer_and_null,
            nargs='?',
            default=SUPPRESS,
            help="Provide driver-cores to edit a Notebook."
        )
        edit_notebook_conf.add_argument(
            "--total-executor-cores",
            type=validate_integer_and_null,
            nargs='?',
            default=SUPPRESS,
            help="Provide total-executor-cores to edit a Notebook."
        )
        edit_notebook_conf.add_argument(
            "--executor-cores",
            type=validate_integer_and_null,
            nargs='?',
            default=SUPPRESS,
            help="Provide executor-cores to edit a Notebook."
        )
        edit_notebook_conf.add_argument(
            "--num-executors",
            type=validate_integer_and_null,
            nargs='?',
            default=SUPPRESS,
            help="Provide num-executors to edit a Notebook."
        )
        edit_notebook_conf.add_argument(
            "--should_append_params",
            type=check_boolean,
            nargs='?',
            default=SUPPRESS,
            choices=['true', 'false'],
            help="Determines whether the job-level Spark configuration should append to or override the cluster-level Spark configuration."
        )
        edit_notebook_conf.add_argument(
            "--json-output",
            type=check_non_empty_string,
            nargs='?',
            choices=['pretty', 'default'],
            default='pretty',
            help="Specifies the format of JSON output."
        )
        edit_notebook_conf.add_argument(
            "--yaml-output",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default='false',
            help="Displays the information in YAML format if set to 'true'."
        )

        enable_notebook_conf = subparser.add_parser(
            'enable',
            help='To enable a specific Notebook.',
            formatter_class=ArgumentDefaultsHelpFormatter)
        enable_notebook_conf.add_argument(
            "--workspace_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="Provide Workspace Id to enable the Notebook."
        )
        enable_notebook_conf.add_argument(
            "--notebook_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            help="Provide Notebook Conf Id to enable the Notebook."
        )
        enable_notebook_conf.add_argument(
            "--notebook_name",
            type=check_non_empty_string,
            nargs=1,
            default=SUPPRESS,
            help="Provide Notebook Name to enable the Notebook."
        )
        enable_notebook_conf.add_argument(
            "--json-output",
            type=check_non_empty_string,
            nargs='?',
            choices=['pretty', 'default'],
            default='pretty',
            help="Specifies the format of JSON output."
        )
        enable_notebook_conf.add_argument(
            "--yaml-output",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default='false',
            help="Displays the information in YAML format if set to 'true'."
        )

        disable_notebook_conf = subparser.add_parser(
            'disable',
            help='To disable a specific Notebook.',
            formatter_class=ArgumentDefaultsHelpFormatter)
        disable_notebook_conf.add_argument(
            "--workspace_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="Provide Workspace Id to disable the Notebook."
        )
        disable_notebook_conf.add_argument(
            "--notebook_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            help="Provide Notebook Conf Id to disable the Notebook."
        )
        disable_notebook_conf.add_argument(
            "--notebook_name",
            type=check_non_empty_string,
            nargs=1,
            default=SUPPRESS,
            help="Provide Notebook Name to disable the Notebook."
        )
        disable_notebook_conf.add_argument(
            "--json-output",
            type=check_non_empty_string,
            nargs='?',
            choices=['pretty', 'default'],
            default='pretty',
            help="Specifies the format of JSON output."
        )
        disable_notebook_conf.add_argument(
            "--yaml-output",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default='false',
            help="Displays the information in YAML format if set to 'true'."
        )

        export_notebook_conf = subparser.add_parser(
            'export',
            help='Export a specific Notebook.',
            formatter_class=ArgumentDefaultsHelpFormatter)
        export_notebook_conf.add_argument(
            "--workspace_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="Provide workspace id to export a specific Notebook from it."
        )
        export_notebook_conf.add_argument(
            "--notebook_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            help="Provide Notebook Id to export a specific Notebook."
        )
        export_notebook_conf.add_argument(
            "--notebook_name",
            type=check_non_empty_string,
            nargs=1,
            default=SUPPRESS,
            help="Provide Notebook name to export a specific Notebook."
        )
        export_notebook_conf.add_argument(
            "--json-output",
            type=check_non_empty_string,
            nargs='?',
            choices=['pretty', 'default'],
            default='pretty',
            help="Specifies the format of JSON output."
        )
        export_notebook_conf.add_argument(
            "--yaml-output",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default='false',
            help="Displays the information in YAML format if set to 'true'."
        )
        clone_notebook_conf = subparser.add_parser(
            'clone',
            help='To clone a Notebook.',
            formatter_class=ArgumentDefaultsHelpFormatter)
        clone_notebook_conf.add_argument(
            "--workspace_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="Provide workspace_id to clone a Notebook."
        )
        clone_notebook_conf.add_argument(
            "--notebook_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            help="Provide Notbeook Conf Id to clone a Notebook."
        )
        clone_notebook_conf.add_argument(
            "--notebook_name",
            type=check_non_empty_string,
            nargs=1,
            default=SUPPRESS,
            help="Provide Notebook Name to clone a Notebook."
        )
        clone_notebook_conf.add_argument(
            "--new_notebook_name",
            type=check_non_empty_string,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="Provide notebook_name to clone a Notebook."
        )
        clone_notebook_conf.add_argument(
            "--clone_file_path",
            type=check_non_empty_string,
            nargs=1,
            default=SUPPRESS,
            help="Provide notebook_path to clone a Notebook."
        )
        clone_notebook_conf.add_argument(
            "--json-output",
            type=check_non_empty_string,
            nargs='?',
            choices=['pretty', 'default'],
            default='pretty',
            help="Specifies the format of JSON output."
        )
        clone_notebook_conf.add_argument(
            "--yaml-output",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default='false',
            help="Displays the information in YAML format if set to 'true'."
        )
