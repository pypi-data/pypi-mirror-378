import os

import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class StorageClient:
    BASE_URL = "http://engine:8080/v1/storage"

    @staticmethod
    def store_from_workspace_to_scene(scene_id: int, source: str, folder: Optional[str] = None,
                                      prefix: Optional[str] = None) -> str:
        url = f"{StorageClient.BASE_URL}/workspace-to-scene"

        params = {
            "sceneId": scene_id,
            "source": source
        }

        if folder is not None:
            params["folder"] = folder

        if prefix is not None:
            params["prefix"] = prefix

        logger.info(f"Storing file from workspace to scene: scene_id={scene_id}, source={source}, "
                    f"folder={folder}, prefix={prefix}")

        try:
            response = requests.post(url, params=params)
            response.raise_for_status()

            result_path = response.json()["path"]
            logger.info(f"Successfully stored file to scene: {result_path}")

            return result_path

        except requests.exceptions.RequestException as e:
            logger.error(f"Error storing file from workspace to scene: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response status: {e.response.status_code}, "
                             f"Response body: {e.response.text}")
            raise

    @staticmethod
    def store_to_task(task_id, node_id, file_path: str, target: str) -> str:
        url = f"{StorageClient.BASE_URL}/to-task"

        params = {
            "taskId": task_id,
            "nodeId": node_id,
            "target": target
        }

        logger.info(f"Storing file to executionTask: task_id={task_id}, node_id={node_id}, "
                    f"file_path={file_path}, target={target}")

        try:
            with open(file_path, 'rb') as f:
                logger.debug(f"Opened file for upload: {file_path}")
                files = {'file': f}

                logger.debug(f"Sending POST request to {url}")
                response = requests.post(url, params=params, files=files)

            response.raise_for_status()

            result_path = response.json()["path"]
            logger.info(f"Successfully stored file to executionTask: {result_path}")

            return result_path

        except requests.exceptions.RequestException as e:
            logger.error(f"Error storing file to executionTask: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response status: {e.response.status_code}, "
                             f"Response body: {e.response.text}")
            raise
        except IOError as e:
            logger.error(f"Error opening file {file_path}: {str(e)}")
            raise

    @staticmethod
    def store_from_workspace_to_task(task_id: int, node_id: int, source: str) -> str:
        url = "http://engine:8080/v1/storage/workspace"

        params = {
            "taskId": task_id,
            "nodeId": node_id,
            "source": source
        }

        logger.info(f"Storing file from workspace to executionTask: task_id={task_id}, "
                    f"node_id={node_id}, source={source}")

        try:
            response = requests.post(
                url,
                params=params,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            response.raise_for_status()

            result_path = response.json()["path"]
            logger.info(f"Successfully stored file from workspace to executionTask: {result_path}")

            return result_path

        except requests.exceptions.RequestException as e:
            logger.error(f"Error storing file from workspace to executionTask: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response status: {e.response.status_code}, "
                             f"Response body: {e.response.text}")
            raise