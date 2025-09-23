"""
测试客户端模块
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from dogecloud_uploader.client import DogecloudClient
from dogecloud_uploader.exceptions import ConfigurationError, AuthenticationError


class TestDogecloudClient:
    """测试多吉云客户端"""

    def test_init_with_env_vars(self, mock_env_vars):
        """测试使用环境变量初始化"""
        client = DogecloudClient()
        assert client.access_key == 'test_access_key'
        assert client.secret_key == 'test_secret_key'
        assert client.bucket_name == 'test_bucket'
        assert client.cdn_domain == 'https://test.cdn.com'

    def test_init_with_params(self):
        """测试使用参数初始化"""
        client = DogecloudClient(
            access_key='param_access_key',
            secret_key='param_secret_key',
            bucket_name='param_bucket',
            cdn_domain='https://param.cdn.com'
        )
        assert client.access_key == 'param_access_key'
        assert client.secret_key == 'param_secret_key'
        assert client.bucket_name == 'param_bucket'
        assert client.cdn_domain == 'https://param.cdn.com'

    def test_init_missing_credentials(self):
        """测试缺少认证信息时抛出异常"""
        with pytest.raises(ConfigurationError):
            DogecloudClient()

    def test_generate_signature(self, mock_env_vars):
        """测试签名生成"""
        client = DogecloudClient()
        signature = client._generate_signature('/test/path', 'test_body')
        assert isinstance(signature, str)
        assert len(signature) == 40  # SHA1签名长度

    @pytest.mark.asyncio
    async def test_dogecloud_api_success(self, mock_env_vars):
        """测试API调用成功"""
        client = DogecloudClient()

        mock_response = MagicMock()
        mock_response.json.return_value = {'code': 200, 'data': {'test': 'data'}}
        mock_response.raise_for_status = MagicMock()

        with patch('requests.post', return_value=mock_response):
            result = await client._dogecloud_api('/test', {'param': 'value'})
            assert result == {'test': 'data'}

    @pytest.mark.asyncio
    async def test_dogecloud_api_error(self, mock_env_vars):
        """测试API调用错误"""
        client = DogecloudClient()

        mock_response = MagicMock()
        mock_response.json.return_value = {'code': 400, 'msg': 'Bad Request'}
        mock_response.raise_for_status = MagicMock()

        with patch('requests.post', return_value=mock_response):
            with pytest.raises(Exception) as exc_info:
                await client._dogecloud_api('/test')
            assert 'Bad Request' in str(exc_info.value)

    def test_get_file_info_html(self, mock_env_vars):
        """测试HTML文件信息获取"""
        client = DogecloudClient()
        content_type, object_key = client.get_file_info('test.html', 'html')
        assert content_type == 'text/html'
        assert object_key == 'agent/html/test.html'

    def test_get_file_info_image(self, mock_env_vars):
        """测试图片文件信息获取"""
        client = DogecloudClient()
        content_type, object_key = client.get_file_info('test.jpg', 'image')
        assert content_type == 'image/jpeg'
        assert object_key == 'images/test.jpg'

    @pytest.mark.asyncio
    async def test_upload_file_success(self, mock_dogecloud_client, mock_s3_client, temp_html_file):
        """测试文件上传成功"""
        client = mock_dogecloud_client

        with patch.object(client, 'get_s3_client', return_value=mock_s3_client):
            result = await client.upload_file(temp_html_file, 'test.html')

            assert result['success'] is True
            assert result['filename'] == 'test.html'
            assert 'file_url' in result
            assert 'object_key' in result

    def test_secure_clear_credentials(self, mock_env_vars):
        """测试安全清理凭证"""
        client = DogecloudClient()
        client._temp_credentials = {
            'accessKeyId': 'test_key',
            'secretAccessKey': 'test_secret',
            'sessionToken': 'test_token'
        }
        client._temp_bucket_info = {'test': 'info'}

        client._secure_clear_credentials()

        assert client._temp_credentials is None
        assert client._temp_bucket_info is None
        assert client._credentials_expire_time == 0