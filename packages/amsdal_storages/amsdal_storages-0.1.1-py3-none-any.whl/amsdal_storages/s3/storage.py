from __future__ import annotations

import io
import os
from contextlib import asynccontextmanager
from typing import IO
from typing import Any
from typing import BinaryIO

from amsdal_models.storage.backends.db import AsyncFileWrapper
from amsdal_models.storage.base import Storage
from amsdal_models.storage.errors import ConfigurationError
from amsdal_models.storage.errors import StorageError
from amsdal_models.storage.types import FileProtocol
from amsdal_utils.config.manager import AmsdalConfigManager


class S3Storage(Storage):
    """S3-backed storage implementation.

    Sync methods use boto3. Async methods use aioboto3.
    """

    keeps_local_copy = False

    def __init__(
        self,
        object_prefix: str = '',
        presign_ttl: int = 3600,
    ) -> None:
        self.bucket = os.environ.get('AWS_S3_BUCKET_NAME')
        self.region_name = os.environ.get('AWS_S3_REGION_NAME') or os.environ.get('AWS_REGION')
        self.endpoint_url = os.environ.get('AWS_S3_ENDPOINT_URL')
        self.access_key_id = os.environ.get('AWS_S3_ACCESS_KEY_ID') or os.environ.get('AWS_ACCESS_KEY_ID')
        self.secret_access_key = os.environ.get('AWS_S3_SECRET_ACCESS_KEY') or os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.security_token = os.environ.get('AWS_SESSION_TOKEN') or os.environ.get('AWS_SECURITY_TOKEN')
        self.object_prefix = object_prefix.strip('/')
        self.presign_ttl = presign_ttl

        if not self.bucket:
            msg = 'S3Storage requires a bucket name'
            raise ConfigurationError(msg)

        try:
            if AmsdalConfigManager().get_config().async_mode:
                import aioboto3  # noqa: F401
            else:
                import boto3  # noqa: F401
        except ImportError:
            msg = 'S3 dependencies are missing. Install it with `pip install amsdal_storages[s3]`.'
            raise ConfigurationError(msg) from None

    @property
    def _s3(self) -> Any:
        import boto3

        return boto3.client(
            's3',
            region_name=self.region_name,
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            aws_session_token=self.security_token,
        )

    @asynccontextmanager
    async def _async_s3(self) -> Any:
        import aioboto3

        session = aioboto3.Session()
        async with session.client(
            's3',
            region_name=self.region_name,
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            aws_session_token=self.security_token,
        ) as client:
            yield client

    def _key(self, file: FileProtocol) -> str:
        base = file.filename.lstrip('/')
        return f'{self.object_prefix}/{base}' if self.object_prefix else base

    def _export_kwargs(self) -> dict[str, Any]:
        return {
            'object_prefix': self.object_prefix,
        }

    def save(self, file: FileProtocol, content: BinaryIO) -> str:
        import botocore.exceptions

        key = self._key(file)

        try:
            self._s3.upload_fileobj(content, self.bucket, key)
        except botocore.exceptions.ClientError as e:
            msg = f'Failed to upload to s3://{self.bucket}/{key}: {e}'
            raise StorageError(msg) from e
        return key

    def open(self, file: FileProtocol, mode: str = 'rb') -> IO[Any]:  # noqa: ARG002
        import botocore.exceptions

        key = self._key(file)

        try:
            obj = self._s3.get_object(Bucket=self.bucket, Key=key)
        except botocore.exceptions.ClientError as e:
            msg = f'Failed to open s3://{self.bucket}/{key}: {e}'
            raise StorageError(msg) from e
        body = obj['Body']

        return body  # StreamingBody implements a file-like interface

    def delete(self, file: FileProtocol) -> None:
        import botocore.exceptions

        key = self._key(file)

        try:
            self._s3.delete_object(Bucket=self.bucket, Key=key)
        except botocore.exceptions.ClientError as e:
            msg = f'Failed to delete s3://{self.bucket}/{key}: {e}'
            raise StorageError(msg) from e

    def exists(self, file: FileProtocol) -> bool:
        import botocore.exceptions

        key = self._key(file)

        try:
            self._s3.head_object(Bucket=self.bucket, Key=key)
            return True
        except botocore.exceptions.ClientError as e:
            code = e.response.get('Error', {}).get('Code')
            if code in {'404', 'NotFound', 'NoSuchKey'}:
                return False
            raise

    def url(self, file: FileProtocol) -> str:
        key = self._key(file)

        # fall back to presigned URL
        return self._s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': key},
            ExpiresIn=self.presign_ttl,
        )

    async def asave(self, file: FileProtocol, content: BinaryIO) -> str:
        key = self._key(file)

        async with self._async_s3() as client:
            try:
                await client.upload_fileobj(content, self.bucket, key)
            except Exception as e:  # pragma: no cover - network dependent
                msg = f'Failed to upload to s3://{self.bucket}/{key}: {e}'
                raise StorageError(msg) from e
        return key

    async def aopen(self, file: FileProtocol, mode: str = 'rb') -> AsyncFileWrapper:  # noqa: ARG002
        key = self._key(file)

        async with self._async_s3() as client:
            try:
                obj = await client.get_object(Bucket=self.bucket, Key=key)
                body = await obj['Body'].read()
            except Exception as e:  # pragma: no cover
                await client.__aexit__(None, None, None)
                msg = f'Failed to open s3://{self.bucket}/{key}: {e}'
                raise StorageError(msg) from e
        return AsyncFileWrapper(io.BytesIO(body))

    async def adelete(self, file: FileProtocol) -> None:
        key = self._key(file)

        async with self._async_s3() as client:
            await client.delete_object(Bucket=self.bucket, Key=key)

    async def aexists(self, file: FileProtocol) -> bool:
        key = self._key(file)

        async with self._async_s3() as client:
            try:
                await client.head_object(Bucket=self.bucket, Key=key)
                return True
            except Exception as e:  # pragma: no cover
                # aiobotocore raises ClientError similarly; detect 404-ish
                msg = getattr(e, 'response', {}).get('Error', {}).get('Code') if hasattr(e, 'response') else None
                if msg in {'404', 'NotFound', 'NoSuchKey'}:
                    return False
                raise

    async def aurl(self, file: FileProtocol) -> str:
        key = self._key(file)

        async with self._async_s3() as client:
            return await client.generate_presigned_url(
                'get_object', Params={'Bucket': self.bucket, 'Key': key}, ExpiresIn=self.presign_ttl
            )
