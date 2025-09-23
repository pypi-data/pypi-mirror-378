import io
import os
import sys
import types

import pytest
from amsdal_models.storage.errors import StorageError

from amsdal_storages.s3.storage import S3Storage


class DummyFile:
    def __init__(self, filename: str):
        self.filename = filename


class DummyClient:
    def __init__(self):
        self.calls = []
        self.objects = {}

    def upload_fileobj(self, content, Bucket, Key):
        self.calls.append(('upload_fileobj', Bucket, Key))
        self.objects[(Bucket, Key)] = content.read()

    def get_object(self, Bucket, Key):
        self.calls.append(('get_object', Bucket, Key))
        data = self.objects.get((Bucket, Key))
        if data is None:
            raise self._client_error('NoSuchKey')
        return {'Body': io.BytesIO(data)}

    def delete_object(self, Bucket, Key):
        self.calls.append(('delete_object', Bucket, Key))
        if (Bucket, Key) in self.objects:
            del self.objects[(Bucket, Key)]

    def head_object(self, Bucket, Key):
        self.calls.append(('head_object', Bucket, Key))
        if (Bucket, Key) not in self.objects:
            raise self._client_error('404')
        return {}

    def generate_presigned_url(self, op, Params, ExpiresIn):
        self.calls.append(('generate_presigned_url', op, Params, ExpiresIn))
        return f'https://example.local/{Params["Bucket"]}/{Params["Key"]}?ttl={ExpiresIn}'

    class _ClientError(Exception):
        def __init__(self, code):
            self.response = {'Error': {'Code': code}}

    def _client_error(self, code):
        # create a fake botocore.exceptions.ClientError subclass enough for code to catch
        err = self._ClientError(code)
        return err


class DummyAioClient:
    def __init__(self):
        self.calls = []
        self.objects = {}

    async def upload_fileobj(self, content, Bucket, Key):
        self.calls.append(('upload_fileobj', Bucket, Key))
        self.objects[(Bucket, Key)] = content.read()

    async def get_object(self, Bucket, Key):
        self.calls.append(('get_object', Bucket, Key))
        data = self.objects.get((Bucket, Key))
        if data is None:
            raise Exception()

        class Body:
            async def read(self_non):
                return data

        return {'Body': Body()}

    async def delete_object(self, Bucket, Key):
        self.calls.append(('delete_object', Bucket, Key))
        if (Bucket, Key) in self.objects:
            del self.objects[(Bucket, Key)]

    async def head_object(self, Bucket, Key):
        self.calls.append(('head_object', Bucket, Key))
        if (Bucket, Key) not in self.objects:
            e = Exception()
            e.response = {'Error': {'Code': '404'}}
            raise e
        return {}

    async def generate_presigned_url(self, op, Params, ExpiresIn):
        self.calls.append(('generate_presigned_url', op, Params, ExpiresIn))
        return f'https://example.local/{Params["Bucket"]}/{Params["Key"]}?ttl={ExpiresIn}'


class DummyAioSession:
    def __init__(self, client: DummyAioClient):
        self._client = client

    def client(self, *args, **kwargs):
        class _Ctx:
            async def __aenter__(self_non):
                return self._client

            async def __aexit__(self_non, exc_type, exc, tb):
                return False

        return _Ctx()


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    # ensure no leakage from host environment
    for k in list(os.environ.keys()):
        if k.startswith('AWS_'):
            monkeypatch.delenv(k, raising=False)

    # Set required environment variable for S3Storage
    monkeypatch.setenv('AWS_S3_BUCKET_NAME', 'my-bucket')


@pytest.fixture
def inject_sync_boto(monkeypatch):
    # install a fake boto3 and botocore.exceptions in sys.modules
    dummy_client = DummyClient()
    fake_boto3 = types.ModuleType('boto3')

    def client(service, **kwargs):
        assert service == 's3'
        return dummy_client

    fake_boto3.client = client

    fake_botocore = types.SimpleNamespace()

    class _Exceptions(types.SimpleNamespace):
        ClientError = DummyClient._ClientError

    fake_botocore.exceptions = _Exceptions()

    sys.modules['boto3'] = fake_boto3
    sys.modules['botocore'] = fake_botocore
    sys.modules['botocore.exceptions'] = fake_botocore.exceptions

    return dummy_client


@pytest.fixture
def inject_async_boto(monkeypatch):
    dummy = DummyAioClient()
    fake_aioboto3 = types.ModuleType('aioboto3')

    def Session():
        return DummyAioSession(dummy)

    fake_aioboto3.Session = Session
    sys.modules['aioboto3'] = fake_aioboto3
    return dummy


class DummyConfig:
    def __init__(self, async_mode: bool):
        self.async_mode = async_mode


class DummyConfigManager:
    def __init__(self, async_mode: bool):
        self._cfg = DummyConfig(async_mode)

    def get_config(self):
        return self._cfg


@pytest.fixture
def set_config_sync(monkeypatch):
    # Make AmsdalConfigManager().get_config().async_mode == False
    monkeypatch.setattr('amsdal_storages.s3.storage.AmsdalConfigManager', lambda: DummyConfigManager(False))


@pytest.fixture
def set_config_async(monkeypatch):
    monkeypatch.setattr('amsdal_storages.s3.storage.AmsdalConfigManager', lambda: DummyConfigManager(True))


def test_keeps_local_copy_flag():
    assert S3Storage.keeps_local_copy is False


def test_key_and_export_kwargs(set_config_sync, inject_sync_boto):
    s = S3Storage(object_prefix='/prefix//')
    f = DummyFile('/path/to/file.txt')
    assert s._key(f) == 'prefix/path/to/file.txt'
    assert s._export_kwargs() == {'object_prefix': 'prefix'}


def test_sync_save_open_exists_delete_url(set_config_sync, inject_sync_boto):
    s = S3Storage(presign_ttl=123)
    f = DummyFile('file.bin')

    # not exists initially
    assert s.exists(f) is False

    key = s.save(f, io.BytesIO(b'hello'))
    assert key == 'file.bin'
    assert s.exists(f) is True

    # open returns file-like
    bio = s.open(f)
    assert bio.read() == b'hello'

    # url generation
    url = s.url(f)
    assert url.endswith('my-bucket/file.bin?ttl=123')

    # delete
    s.delete(f)
    assert s.exists(f) is False


def test_sync_save_error_wrapped(set_config_sync, inject_sync_boto, monkeypatch):
    s = S3Storage()
    f = DummyFile('x.txt')

    # Force upload to raise ClientError
    class Boom(DummyClient._ClientError):
        pass

    def bad_upload(*args, **kwargs):
        raise Boom('NoSuchBucket')

    # swap upload method
    client = sys.modules['boto3'].client('s3')
    monkeypatch.setattr(client, 'upload_fileobj', bad_upload)

    with pytest.raises(StorageError) as ei:
        s.save(f, io.BytesIO(b'data'))
    assert 'Failed to upload' in str(ei.value)


@pytest.mark.asyncio
async def test_async_save_open_exists_delete_url(set_config_async, inject_async_boto):
    s = S3Storage(presign_ttl=999)
    f = DummyFile('data.bin')

    assert await s.aexists(f) is False
    key = await s.asave(f, io.BytesIO(b'abc'))
    assert key == 'data.bin'
    assert await s.aexists(f) is True

    bio = await s.aopen(f)
    from amsdal_models.storage.backends.db import AsyncFileWrapper

    assert isinstance(bio, AsyncFileWrapper)
    assert await bio.read() == b'abc'

    url = await s.aurl(f)
    assert url.endswith('my-bucket/data.bin?ttl=999')

    await s.adelete(f)
    assert await s.aexists(f) is False
