import os
import boto3
import logging
from typing import Optional

from pixel.sdk.models.node_decorator import node
from pixel.core import Metadata
from pixel.sdk import StorageClient

logger = logging.getLogger(__name__)

def s3_input_exec(
    access_key_id: str,
    secret_access_key: str,
    region: str,
    bucket: str,
    meta: Metadata,
    endpoint: Optional[str] = None
):
    logger.info(f"S3 configuration - Region: {region}, Bucket: {bucket}")
    files = set()

    session = boto3.Session(
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name=region
    )

    s3_config = {}
    if endpoint and endpoint.strip():
        clean_endpoint = endpoint.strip().rstrip('/')
        s3_config['endpoint_url'] = clean_endpoint
        s3_config['use_ssl'] = clean_endpoint.startswith('https')

    try:
        s3_client = session.client('s3', **s3_config)
        response = s3_client.list_objects_v2(Bucket=bucket)

        if 'Contents' in response:
            logger.info(f"Found {len(response['Contents'])} objects in bucket")
            for obj in response['Contents']:
                filename = obj['Key']
                file_response = s3_client.get_object(Bucket=bucket, Key=filename)
                content = file_response['Body'].read()

                temp_file_path = f"/tmp/{filename}"
                with open(temp_file_path, 'wb') as f:
                    f.write(content)

                file_path = StorageClient.store_to_task(
                    task_id=meta.task_id,
                    node_id=meta.node_id,
                    file_path=temp_file_path,
                    target=filename
                )
                logger.info(f'Saved {file_path}')
                files.add(file_path)
                os.remove(temp_file_path)
        else:
            logger.info("No files found in bucket")

    except Exception as e:
        logger.error(f"S3 error: {str(e)}")
        raise ValueError(f"Failed to connect to S3: {str(e)}")

    return {"files": files}


def s3_input_validate(
    access_key_id: str,
    secret_access_key: str,
    region: str,
    bucket: str,
    meta: Metadata,
    endpoint: Optional[str] = None
):
    if not access_key_id:
        raise ValueError("Access key ID cannot be blank.")
    if not secret_access_key:
        raise ValueError("Secret cannot be blank.")
    if not region:
        raise ValueError("Region cannot be blank.")
    if not bucket:
        raise ValueError("Bucket cannot be blank.")


@node(
    tasks={"exec": s3_input_exec, "validate": s3_input_validate},
    inputs={
        "access_key_id": {"type": "STRING", "required": True, "widget": "INPUT", "default": ""},
        "secret_access_key": {"type": "STRING", "required": True, "widget": "INPUT", "default": ""},
        "region": {"type": "STRING", "required": True, "widget": "INPUT", "default": ""},
        "bucket": {"type": "STRING", "required": True, "widget": "INPUT", "default": ""},
        "endpoint": {"type": "STRING", "required": False, "widget": "INPUT", "default": ""}
    },
    outputs={
        "files": {"type": "FILEPATH_ARRAY", "required": True}
    },
    display_name="S3 Input",
    category="IO",
    description="Load files from S3",
    color="#AED581",
    icon="S3Icon"
)
def s3_input(
    access_key_id: str,
    secret_access_key: str,
    region: str,
    bucket: str,
    meta: Metadata,
    endpoint: Optional[str] = None
):
    pass
