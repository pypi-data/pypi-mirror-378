from yeeducli.utility.file_utils import FileUtils
from yeeducli.utility.json_utils import response_validator
from yeeducli.utility.request_utils import Requests
from yeeducli.utility.logger_utils import Logger
from yeeducli import config
import requests
import sys

logger = Logger.get_logger(__name__, True)


class NotebookConfig:
    def list_notebook_configs(workspace_id, enable, pageNumber, limit, cluster_ids=None, language=None, has_run=None, last_run_status=None, created_by_ids=None, modified_by_ids=None):
        try:
            url = f"{config.YEEDU_RESTAPI_URL}/workspace/{workspace_id}/notebooks"

            response = Requests(
                url=url,
                method="GET",
                headers=config.headers,
                params={
                    "enable": enable,
                    "cluster_ids": cluster_ids,
                    "job_type_langs": language,
                    "has_run": has_run,
                    "last_run_status": [status.upper() for status in last_run_status] if isinstance(last_run_status, list) else None,
                    "created_by_ids": created_by_ids,
                    "modified_by_ids": modified_by_ids,
                    "pageNumber": pageNumber,
                    "limit": limit
                }
            ).send_http_request()

            return response_validator(response)
        except requests.exceptions.RequestException as e:
            logger.exception(f"Failed to connect due to {e}")
            sys.exit(-1)

    def search_notebook_config_by_workspaceId_and_name(workspace_id, notebook_name, enable, pageNumber, limit, cluster_ids=None, language=None, has_run=None, last_run_status=None, created_by_ids=None, modified_by_ids=None):
        try:
            url = f"{config.YEEDU_RESTAPI_URL}/workspace/{workspace_id}/notebooks/search"

            response = Requests(
                url=url,
                method="GET",
                headers=config.headers,
                params={
                    "notebook_name": notebook_name,
                    "enable": enable,
                    "cluster_ids": cluster_ids,
                    "job_type_langs": language,
                    "has_run": has_run,
                    "last_run_status": [status.upper() for status in last_run_status] if isinstance(last_run_status, list) else None,
                    "created_by_ids": created_by_ids,
                    "modified_by_ids": modified_by_ids,
                    "pageNumber": pageNumber,
                    "limit": limit
                }
            ).send_http_request()

            return response_validator(response)
        except requests.exceptions.RequestException as e:
            logger.exception(f"Failed to connect due to {e}")
            sys.exit(-1)

    def add_notebook_config(workspace_id, json_data):
        try:
            url = f"{config.YEEDU_RESTAPI_URL}/workspace/{workspace_id}/notebook"

            response = Requests(
                url=url,
                method="POST",
                headers=config.headers,
                json=json_data
            ).send_http_request()

            return response_validator(response)
        except requests.exceptions.RequestException as e:
            logger.exception(f"Failed to connect due to {e}")
            sys.exit(-1)

    def get_notebook_config_by_id_or_name(workspace_id, notebook_id=None, notebook_name=None):
        try:
            url = f"{config.YEEDU_RESTAPI_URL}/workspace/{workspace_id}/notebook"

            response = Requests(
                url=url,
                method="GET",
                headers=config.headers,
                params={
                    "notebook_id": notebook_id,
                    "notebook_name": notebook_name
                }
            ).send_http_request()

            return response_validator(response)
        except requests.exceptions.RequestException as e:
            logger.exception(f"Failed to connect due to {e}")
            sys.exit(-1)

    def edit_notebook_config(workspace_id, json_data, notebook_id=None, notebook_name=None):
        try:
            url = f"{config.YEEDU_RESTAPI_URL}/workspace/{workspace_id}/notebook"

            response = Requests(
                url=url,
                method="PUT",
                headers=config.headers,
                data=json_data,
                params={
                    "notebook_id": notebook_id,
                    "notebook_name": notebook_name
                }
            ).send_http_request()

            return response_validator(response)
        except requests.exceptions.RequestException as e:
            logger.exception(f"Failed to connect due to {e}")
            sys.exit(-1)

    def enable_notebook_config_by_id_or_name(workspace_id, notebook_id=None, notebook_name=None):
        try:
            url = f"{config.YEEDU_RESTAPI_URL}/workspace/{workspace_id}/notebook/enable"

            response = Requests(
                url=url,
                method="PUT",
                headers=config.headers,
                params={
                    "notebook_id": notebook_id,
                    "notebook_name": notebook_name
                }
            ).send_http_request()

            return response_validator(response)
        except requests.exceptions.RequestException as e:
            logger.exception(f"Failed to connect due to {e}")
            sys.exit(-1)

    def disable_notebook_config_by_id_or_name(workspace_id, notebook_id=None, notebook_name=None):
        try:
            url = f"{config.YEEDU_RESTAPI_URL}/workspace/{workspace_id}/notebook/disable"

            response = Requests(
                url=url,
                method="PUT",
                headers=config.headers,
                params={
                    "notebook_id": notebook_id,
                    "notebook_name": notebook_name
                }
            ).send_http_request()

            return response_validator(response)
        except requests.exceptions.RequestException as e:
            logger.exception(f"Failed to connect due to {e}")
            sys.exit(-1)

    def export_notebook_config(workspace_id, notebook_id=None, notebook_name=None):
        try:
            url = f"{config.YEEDU_RESTAPI_URL}/workspace/{workspace_id}/notebook/export"

            response = Requests(
                url=url,
                method="GET",
                headers=config.headers,
                params={
                    "notebook_name": notebook_name,
                    "notebook_id": notebook_id
                }
            ).send_http_request()

            return FileUtils.process_file_response(response, save_to_disk=True)

        except requests.exceptions.RequestException as e:
            logger.exception(f"Failed to connect due to {e}")
            sys.exit(-1)

    def clone_notebook_config_by_id_or_name(workspace_id, new_notebook_name, notebook_id=None, notebook_name=None, clone_file_path=None):
        try:
            url = f"{config.YEEDU_RESTAPI_URL}/workspace/{workspace_id}/notebook/clone"

            response = Requests(
                url=url,
                method="POST",
                headers=config.headers,
                params={
                    "notebook_id": notebook_id,
                    "notebook_name": notebook_name,
                    "new_notebook_name": new_notebook_name,
                    "clone_file_path": clone_file_path
                }
            ).send_http_request()

            return response_validator(response)
        except requests.exceptions.RequestException as e:
            logger.exception(f"Failed to connect due to {e}")
            sys.exit(-1)

