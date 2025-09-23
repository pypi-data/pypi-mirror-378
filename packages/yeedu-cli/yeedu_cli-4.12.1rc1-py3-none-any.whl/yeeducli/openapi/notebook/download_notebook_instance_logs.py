from yeeducli.utility.file_utils import FileUtils
from yeeducli.utility.request_utils import Requests
from yeeducli.utility.logger_utils import Logger
from yeeducli import config
import requests
import sys

logger = Logger.get_logger(__name__, True)


class DownloadNotebookInstanceLogs:
    def get_notebook_instance_logs(workspace_id, run_id, log_type, last_n_lines=None, file_size_bytes=None):
        try:
            url = f"{config.YEEDU_RESTAPI_URL}/workspace/{workspace_id}/notebook/run/{run_id}/log/{log_type}"

            response = Requests(
                url=url,
                method="GET",
                headers=config.headers,
                stream=True,
                params={
                    "last_n_lines": last_n_lines,
                    "file_size_bytes": file_size_bytes
                }
            ).send_http_request()

            return FileUtils.process_file_response(response, save_to_disk=False)

        except requests.exceptions.RequestException as e:
            logger.exception(f"Failed to connect due to {e}")
            sys.exit(-1)
