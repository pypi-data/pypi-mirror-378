"""
测试配置和fixture
"""

import pytest
import os
import tempfile
from unittest.mock import AsyncMock, MagicMock

from dogecloud_uploader.client import DogecloudClient


@pytest.fixture
def mock_env_vars(monkeypatch):
    """模拟环境变量"""
    monkeypatch.setenv('DOGECLOUD_ACCESS_KEY', 'test_access_key')
    monkeypatch.setenv('DOGECLOUD_SECRET_KEY', 'test_secret_key')
    monkeypatch.setenv('DOGECLOUD_BUCKET_NAME', 'test_bucket')
    monkeypatch.setenv('DOGECLOUD_CDN_DOMAIN', 'https://test.cdn.com')


@pytest.fixture
def temp_image_file():
    """创建临时图片文件"""
    # 创建一个最小的PNG图片文件
    png_data = (
        b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d\x49\x48\x44\x52'
        b'\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4'
        b'\x89\x00\x00\x00\x0a\x49\x44\x41\x54\x78\x9c\x63\x00\x01\x00\x00'
        b'\x05\x00\x01\x0d\x0a\x2d\xb4\x00\x00\x00\x00\x49\x45\x4e\x44\xae'
        b'\x42\x60\x82'
    )

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        f.write(png_data)
        f.flush()
        yield f.name

    # 清理
    try:
        os.unlink(f.name)
    except FileNotFoundError:
        pass


@pytest.fixture
def temp_html_file():
    """创建临时HTML文件"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Test</title>
</head>
<body>
    <h1>Test HTML</h1>
</body>
</html>"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html_content)
        f.flush()
        yield f.name

    # 清理
    try:
        os.unlink(f.name)
    except FileNotFoundError:
        pass


@pytest.fixture
def mock_dogecloud_client(mock_env_vars):
    """模拟多吉云客户端"""
    client = DogecloudClient()

    # 模拟临时凭证
    mock_credentials = {
        'accessKeyId': 'mock_access_key_id',
        'secretAccessKey': 'mock_secret_access_key',
        'sessionToken': 'mock_session_token'
    }

    mock_bucket_info = {
        's3Bucket': 'test-bucket-123',
        's3Endpoint': 'https://s3.test.com',
        's3EndpointHost': 'https://s3.test.com'
    }

    # 模拟获取临时凭证方法
    async def mock_get_temp_credentials():
        return mock_credentials, mock_bucket_info

    client.get_temp_credentials = mock_get_temp_credentials

    return client


@pytest.fixture
def mock_s3_client():
    """模拟S3客户端"""
    mock_client = MagicMock()

    # 模拟上传成功
    mock_client.upload_fileobj = MagicMock()
    mock_client.head_object = MagicMock(return_value={'ETag': '"test_etag"'})

    return mock_client