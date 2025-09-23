from argparse import SUPPRESS, ArgumentDefaultsHelpFormatter
from yeeducli.utility.json_utils import check_boolean, check_non_empty_string


class DownloadNotebookInstanceLogParser:

    def download_notebook_instance_log_parser(subparser):

        download_notebook_instance_logs = subparser.add_parser(
            'logs',
            help='To download Notebook run logs.',
            formatter_class=ArgumentDefaultsHelpFormatter
        )
        download_notebook_instance_logs.add_argument(
            "--workspace_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="Provide Workspace Id to download Notebook run logs."
        )
        download_notebook_instance_logs.add_argument(
            "--run_id",
            type=int,
            nargs=1,
            default=SUPPRESS,
            required=True,
            help="Provide Notebook Id to download Notebook run logs."
        )
        download_notebook_instance_logs.add_argument(
            "--log_type",
            type=check_non_empty_string,
            nargs=1,
            default='stdout',
            choices=['stdout', 'stderr'],
            help="Provide log type to download Notebook run logs."
        )
        download_notebook_instance_logs.add_argument(
            "--last_n_lines",
            type=int,
            nargs=1,
            default=SUPPRESS,
            help="Number of lines to retrieve from the end of the log file (sample preview)."
        )
        download_notebook_instance_logs.add_argument(
            "--file_size_bytes",
            type=int,
            nargs=1,
            default=SUPPRESS,
            help="Number of bytes to preview from the beginning of the log file (sample preview)."
        )
        download_notebook_instance_logs.add_argument(
            "--json-output",
            type=check_non_empty_string,
            nargs='?',
            choices=['pretty', 'default'],
            default='pretty',
            help="Specifies the format of JSON output."
        )
        download_notebook_instance_logs.add_argument(
            "--yaml-output",
            type=check_boolean,
            nargs='?',
            choices=['true', 'false'],
            default='false',
            help="Displays the information in YAML format if set to 'true'."
        )
