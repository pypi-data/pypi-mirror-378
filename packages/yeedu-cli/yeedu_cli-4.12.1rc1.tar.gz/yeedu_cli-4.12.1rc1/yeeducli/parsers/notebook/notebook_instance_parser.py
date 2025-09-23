from yeeducli.constants import SPARK_JOB_STATUS, NOTEBOOK_LANG
from argparse import SUPPRESS, ArgumentDefaultsHelpFormatter
from yeeducli.utility.json_utils import check_boolean, check_non_empty_string, validate_array_of_intgers, check_choices


class NotebookInstanceParser:
    def notebook_instance_parser(subparser):
        start_notebook_instance = subparser.add_parser(
            'start',
            help='To start a Notebook run.',
            formatter_class=ArgumentDefaultsHelpFormatter)
        start_notebook_instance.add_argument(
            "--workspace_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="To start a Notebook run, enter workspace_id."
        )
        start_notebook_instance.add_argument(
            "--notebook_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            help="To start a Notebook run, enter notebook_id."
        )
        start_notebook_instance.add_argument(
            "--notebook_name",
            type=check_non_empty_string,
            nargs=1,
            default=SUPPRESS,
            help="To start a Notebook run, enter notebook_name."
        )
        start_notebook_instance.add_argument(
            "--json-output",
            type=check_non_empty_string,
            nargs='?',
            choices=['pretty', 'default'],
            default='pretty',
            help="Specifies the format of JSON output."
        )
        start_notebook_instance.add_argument(
            "--yaml-output",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default='false',
            help="Displays the information in YAML format if set to 'true'."
        )

        notebook_instance_kernel_start = subparser.add_parser(
            'kernel-start',
            help='To start a kernel of a Notebook run.',
            formatter_class=ArgumentDefaultsHelpFormatter)
        notebook_instance_kernel_start.add_argument(
            "--workspace_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="To start a kernel of a Notebook run, enter workspace_id."
        )
        notebook_instance_kernel_start.add_argument(
            "--run_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="To start a kernel of a Notebook run, enter notebook run id."
        )
        notebook_instance_kernel_start.add_argument(
            "--json-output",
            type=check_non_empty_string,
            nargs='?',
            choices=['pretty', 'default'],
            default='pretty',
            help="Specifies the format of JSON output."
        )
        notebook_instance_kernel_start.add_argument(
            "--yaml-output",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default='false',
            help="Displays the information in YAML format if set to 'true'."
        )

        notebook_instance_kernel_status = subparser.add_parser(
            'kernel-status',
            help='To get the status of the kernel of a Notebook run.',
            formatter_class=ArgumentDefaultsHelpFormatter)
        notebook_instance_kernel_status.add_argument(
            "--workspace_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="To get the status of the kernel, enter workspace_id."
        )
        notebook_instance_kernel_status.add_argument(
            "--run_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="To get the status of the kernel for a Notebook run, enter notebook run id."
        )
        notebook_instance_kernel_status.add_argument(
            "--json-output",
            type=check_non_empty_string,
            nargs='?',
            choices=['pretty', 'default'],
            default='pretty',
            help="Specifies the format of JSON output."
        )
        notebook_instance_kernel_status.add_argument(
            "--yaml-output",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default='false',
            help="Displays the information in YAML format if set to 'true'."
        )

        notebook_instance_kernel_interrupt = subparser.add_parser(
            'kernel-interrupt',
            help='To interrupt a kernel of a Notebook run.',
            formatter_class=ArgumentDefaultsHelpFormatter)
        notebook_instance_kernel_interrupt.add_argument(
            "--workspace_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="To interrupt a kernel of a Notebook run, enter workspace_id."
        )
        notebook_instance_kernel_interrupt.add_argument(
            "--run_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="To interrupt a kernel of a Notebook run, enter notebook run id."
        )
        notebook_instance_kernel_interrupt.add_argument(
            "--json-output",
            type=check_non_empty_string,
            nargs='?',
            choices=['pretty', 'default'],
            default='pretty',
            help="Specifies the format of JSON output."
        )
        notebook_instance_kernel_interrupt.add_argument(
            "--yaml-output",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default='false',
            help="Displays the information in YAML format if set to 'true'."
        )

        notebook_instance_kernel_restart = subparser.add_parser(
            'kernel-restart',
            help='To restart a kernel of a Notebook run.',
            formatter_class=ArgumentDefaultsHelpFormatter)
        notebook_instance_kernel_restart.add_argument(
            "--workspace_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="To restart a kernel of a Notebook run, enter workspace_id."
        )
        notebook_instance_kernel_restart.add_argument(
            "--run_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="To restart a kernel of a Notebook run, enter notebook run id."
        )
        notebook_instance_kernel_restart.add_argument(
            "--json-output",
            type=check_non_empty_string,
            nargs='?',
            choices=['pretty', 'default'],
            default='pretty',
            help="Specifies the format of JSON output."
        )
        notebook_instance_kernel_restart.add_argument(
            "--yaml-output",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default='false',
            help="Displays the information in YAML format if set to 'true'."
        )

        list_notebook_instances = subparser.add_parser(
            'list-runs',
            help='To list all the available Notebook runs.',
            formatter_class=ArgumentDefaultsHelpFormatter)
        list_notebook_instances.add_argument(
            "--workspace_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="To list Notebook runs of a specific workspace_id."
        )
        list_notebook_instances.add_argument(
            "--cluster_ids",
            type=validate_array_of_intgers,
            nargs='?',
            default=SUPPRESS,
            help="To list Notebook runs for optional set of cluster Ids."
        )
        list_notebook_instances.add_argument(
            "--notebook_ids",
            type=validate_array_of_intgers,
            nargs='?',
            default=SUPPRESS,
            help="To list Notebook runs for optional set of Notebook Ids."
        )
        list_notebook_instances.add_argument(
            "--run_status",
            type=lambda values: check_choices(
                values, choices=SPARK_JOB_STATUS),
            nargs='?',
            default=SUPPRESS,
            help="To list Notebook runs for optional set of run_status. Choices are: " +
            ", ".join(SPARK_JOB_STATUS)
        )
        list_notebook_instances.add_argument(
            "--job_type_langs",
            type=lambda values: check_choices(values, choices=NOTEBOOK_LANG),
            nargs='?',
            default=SUPPRESS,
            help="An optional set of language filter for Notebook runs. Choices are: " +
            ", ".join(NOTEBOOK_LANG)
        )
        list_notebook_instances.add_argument(
            "--created_by_ids",
            type=validate_array_of_intgers,
            nargs='?',
            default=SUPPRESS,
            help="To list Notebook runs for optional set of created by user Ids."
        )
        list_notebook_instances.add_argument(
            "--modified_by_ids",
            type=validate_array_of_intgers,
            nargs='?',
            default=SUPPRESS,
            help="To list Notebook runs for optional set of modified by user Ids."
        )
        list_notebook_instances.add_argument(
            "--page_number",
            type=int,
            nargs=1,
            default=1,
            help="To list Notebook runs for a specific page_number."
        )
        list_notebook_instances.add_argument(
            "--limit",
            type=int,
            nargs=1,
            default=100,
            help="Provide limit to list number of job runs."
        )
        list_notebook_instances.add_argument(
            "--json-output",
            type=check_non_empty_string,
            nargs='?',
            choices=['pretty', 'default'],
            default='pretty',
            help="Specifies the format of JSON output."
        )
        list_notebook_instances.add_argument(
            "--yaml-output",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default='false',
            help="Displays the information in YAML format if set to 'true'."
        )

        search_notebook_instances = subparser.add_parser(
            'search-runs',
            help='To search Notebook runs by similar notebook name.',
            formatter_class=ArgumentDefaultsHelpFormatter)
        search_notebook_instances.add_argument(
            "--workspace_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="Provide workspace id to search Notebook runs in it."
        )
        search_notebook_instances.add_argument(
            "--notebook_name",
            type=check_non_empty_string,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="Provide notebook_name to search Notebook runs."
        )
        search_notebook_instances.add_argument(
            "--cluster_ids",
            type=validate_array_of_intgers,
            nargs='?',
            default=SUPPRESS,
            help="To search Notebook runs for optional set of cluster Ids."
        )
        search_notebook_instances.add_argument(
            "--notebook_ids",
            type=validate_array_of_intgers,
            nargs='?',
            default=SUPPRESS,
            help="To search Notebook runs for optional set of Notebook Ids."
        )
        search_notebook_instances.add_argument(
            "--run_status",
            type=lambda values: check_choices(
                values, choices=SPARK_JOB_STATUS),
            nargs='?',
            default=SUPPRESS,
            help="To search Notebook runs for optional set of run_status. Choices are: " +
            ", ".join(SPARK_JOB_STATUS)
        )
        search_notebook_instances.add_argument(
            "--job_type_langs",
            type=lambda values: check_choices(values, choices=NOTEBOOK_LANG),
            nargs='?',
            default=SUPPRESS,
            help="An optional set of language filter for Notebook runs. Choices are: " +
            ", ".join(NOTEBOOK_LANG)
        )
        search_notebook_instances.add_argument(
            "--created_by_ids",
            type=validate_array_of_intgers,
            nargs='?',
            default=SUPPRESS,
            help="To search Notebook runs for optional set of created by user Ids."
        )
        search_notebook_instances.add_argument(
            "--modified_by_ids",
            type=validate_array_of_intgers,
            nargs='?',
            default=SUPPRESS,
            help="To search Notebook runs for optional set of modified by user Ids."
        )
        search_notebook_instances.add_argument(
            "--page_number",
            type=int,
            nargs=1,
            default=1,
            help="To search Notebook runs for a specific page_number."
        )
        search_notebook_instances.add_argument(
            "--limit",
            type=int,
            nargs=1,
            default=100,
            help="Provide limit to search number of Notebook runs."
        )
        search_notebook_instances.add_argument(
            "--json-output",
            type=check_non_empty_string,
            nargs='?',
            choices=['pretty', 'default'],
            default='pretty',
            help="Specifies the format of JSON output."
        )
        search_notebook_instances.add_argument(
            "--yaml-output",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default='false',
            help="Displays the information in YAML format if set to 'true'."
        )

        get_notebook_instance = subparser.add_parser(
            'get-run',
            help='To get information about a specific Notebook run.',
            formatter_class=ArgumentDefaultsHelpFormatter)
        get_notebook_instance.add_argument(
            "--workspace_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="Provide workspace id to get information about a specific Notebook run."
        )
        get_notebook_instance.add_argument(
            "--run_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="Provide notebook run id to get information about a specific Notebook run."
        )
        get_notebook_instance.add_argument(
            "--json-output",
            type=check_non_empty_string,
            nargs='?',
            choices=['pretty', 'default'],
            default='pretty',
            help="Specifies the format of JSON output."
        )
        get_notebook_instance.add_argument(
            "--yaml-output",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default='false',
            help="Displays the information in YAML format if set to 'true'."
        )

        stop_notebook_instance = subparser.add_parser(
            'stop',
            help='To stop a specific Notebook run.',
            formatter_class=ArgumentDefaultsHelpFormatter)
        stop_notebook_instance.add_argument(
            "--workspace_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="Provide workspace id to stop a specific Notebook run."
        )
        stop_notebook_instance.add_argument(
            "--run_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="Provide notebook run id to stop a specific Notebook run."
        )
        stop_notebook_instance.add_argument(
            "--json-output",
            type=check_non_empty_string,
            nargs='?',
            choices=['pretty', 'default'],
            default='pretty',
            help="Specifies the format of JSON output."
        )
        stop_notebook_instance.add_argument(
            "--yaml-output",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default='false',
            help="Displays the information in YAML format if set to 'true'."
        )
