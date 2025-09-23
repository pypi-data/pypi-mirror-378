"""
测试工具函数模块
"""

import pytest
import os
import tempfile
from unittest.mock import patch, AsyncMock

from dogecloud_uploader.utils import (
    validate_image_file,
    upload_image,
    upload_file,
    _safe_base64_decode,
    download_image
)
from dogecloud_uploader.exceptions import ValidationError


class TestValidateImageFile:
    """测试图片文件验证"""

    def test_validate_valid_image(self, temp_image_file):
        """测试验证有效图片"""
        result = validate_image_file(temp_image_file)
        assert result['valid'] is True
        assert result['size'] > 0
        assert result['format'] == 'PNG'

    def test_validate_nonexistent_file(self):
        """测试验证不存在的文件"""
        with pytest.raises(ValidationError) as exc_info:
            validate_image_file('/nonexistent/file.jpg')
        assert '文件不存在' in str(exc_info.value)

    def test_validate_unsupported_format(self):
        """测试验证不支持的格式"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b'test content')
            f.flush()

            try:
                with pytest.raises(ValidationError) as exc_info:
                    validate_image_file(f.name)
                assert '不支持的图片格式' in str(exc_info.value)
            finally:
                os.unlink(f.name)

    def test_validate_large_file(self):
        """测试验证过大的文件"""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            # 写入超过限制的数据 (10MB + 1KB)
            large_data = b'x' * (10 * 1024 * 1024 + 1024)
            f.write(large_data)
            f.flush()

            try:
                with pytest.raises(ValidationError) as exc_info:
                    validate_image_file(f.name)
                assert '图片文件过大' in str(exc_info.value)
            finally:
                os.unlink(f.name)


class TestBase64Decode:
    """测试Base64解码"""

    def test_safe_base64_decode_valid(self):
        """测试有效的Base64解码"""
        data = 'SGVsbG8gV29ybGQ='  # "Hello World"
        result = _safe_base64_decode(data)
        assert result == b'Hello World'

    def test_safe_base64_decode_invalid(self):
        """测试无效的Base64数据"""
        with pytest.raises(ValidationError) as exc_info:
            _safe_base64_decode('invalid base64!')
        assert '无效的Base64编码格式' in str(exc_info.value)

    def test_safe_base64_decode_too_large(self):
        """测试过大的Base64数据"""
        # 创建过大的Base64数据
        large_data = 'A' * (10 * 1024 * 1024 * 4 // 3 + 1000)  # 超过10MB的Base64
        with pytest.raises(ValidationError) as exc_info:
            _safe_base64_decode(large_data)
        assert 'Base64数据过大' in str(exc_info.value)


class TestDownloadImage:
    """测试图片下载"""

    @pytest.mark.asyncio
    async def test_download_base64_image(self):
        """测试下载Base64图片"""
        # 最小的PNG图片的Base64编码
        base64_png = (
            'data:image/png;base64,'
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=='
        )

        with tempfile.NamedTemporaryFile(delete=False) as f:
            try:
                result_path = await download_image(base64_png, f.name)
                assert result_path == f.name
                assert os.path.exists(f.name)
                assert os.path.getsize(f.name) > 0
            finally:
                if os.path.exists(f.name):
                    os.unlink(f.name)

    @pytest.mark.asyncio
    async def test_download_invalid_data_url(self):
        """测试下载无效的data URL"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            try:
                with pytest.raises(Exception) as exc_info:
                    await download_image('data:invalid', f.name)
                assert '无效的 data URL 格式' in str(exc_info.value)
            finally:
                if os.path.exists(f.name):
                    os.unlink(f.name)


class TestUploadFunctions:
    """测试上传函数"""

    @pytest.mark.asyncio
    async def test_upload_file_success(self, mock_env_vars, temp_html_file):
        """测试文件上传成功"""
        mock_result = {
            'success': True,
            'file_url': 'https://test.cdn.com/test.html',
            'object_key': 'agent/html/test.html',
            'filename': 'test.html'
        }

        with patch('dogecloud_uploader.utils.DogecloudClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.upload_file = AsyncMock(return_value=mock_result)
            mock_client_class.return_value = mock_client

            result = await upload_file(temp_html_file)
            assert result['success'] is True
            assert result['file_url'] == 'https://test.cdn.com/test.html'

    @pytest.mark.asyncio
    async def test_upload_file_not_exists(self, mock_env_vars):
        """测试上传不存在的文件"""
        with pytest.raises(ValidationError) as exc_info:
            await upload_file('/nonexistent/file.html')
        assert '文件不存在' in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_upload_image_empty_url(self):
        """测试上传空URL"""
        result = await upload_image('')
        assert result['success'] is False
        assert 'image_url参数为空' in result['error']

    @pytest.mark.asyncio
    async def test_upload_image_invalid_url(self):
        """测试上传无效URL"""
        with pytest.raises(ValidationError) as exc_info:
            await upload_image('invalid_url')
        assert 'image_url 必须是以下格式之一' in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_upload_image_base64_success(self, mock_env_vars):
        """测试Base64图片上传成功"""
        # 最小的PNG图片的Base64编码
        base64_png = (
            'data:image/png;base64,'
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=='
        )

        mock_result = {
            'success': True,
            'file_url': 'https://test.cdn.com/test.png',
            'object_key': 'images/test.png',
            'filename': 'test.png',
            'size': 100,
            'format': 'PNG'
        }

        with patch('dogecloud_uploader.utils.DogecloudClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.upload_file = AsyncMock(return_value=mock_result)
            mock_client.enable_compression = False
            mock_client_class.return_value = mock_client

            result = await upload_image(base64_png)
            assert result['success'] is True
            assert 'file_url' in result