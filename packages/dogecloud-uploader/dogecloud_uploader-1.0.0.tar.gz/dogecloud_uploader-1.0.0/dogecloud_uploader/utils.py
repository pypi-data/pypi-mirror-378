"""
工具函数和简化API
"""

import os
import re
import base64
import hashlib
import tempfile
import uuid
from typing import Optional, Dict, Any
from pathlib import Path
import asyncio
import aiohttp

from .client import DogecloudClient
from .exceptions import ValidationError, UploadError

# 支持的图片格式
SUPPORTED_IMAGE_TYPES = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']

# Base64解码安全限制
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024
MAX_BASE64_SIZE = MAX_FILE_SIZE * 4 // 3 + 100  # Base64编码的最大理论大小 + 填充
BASE64_CHUNK_SIZE = 8192  # 分块处理大小

# 文件签名映射
FILE_SIGNATURES = {
    'jpg': b'\xFF\xD8\xFF',
    'jpeg': b'\xFF\xD8\xFF',
    'png': b'\x89\x50\x4E\x47',
    'gif': b'\x47\x49\x46',
    'webp': b'\x52\x49\x46\x46',
    'bmp': b'\x42\x4D'
}


class _TempFileManager:
    """临时文件安全管理器"""

    def __init__(self):
        self._temp_files = []

    def create_temp_file(self, suffix: str = '') -> tempfile.NamedTemporaryFile:
        """创建临时文件并追踪"""
        temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        self._temp_files.append(temp_file.name)
        return temp_file

    def cleanup_all(self):
        """清理所有临时文件"""
        for file_path in self._temp_files:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception:
                pass  # 忽略清理错误
        self._temp_files.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup_all()


def validate_image_file(file_path: str) -> Dict[str, Any]:
    """验证图片文件"""
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise ValidationError(f"文件不存在: {file_path}")

    # 检查文件大小
    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValidationError(f"图片文件过大，最大支持 {MAX_FILE_SIZE_MB}MB")

    # 检查文件扩展名
    filename = os.path.basename(file_path)
    _, ext = os.path.splitext(filename)
    ext = ext.lstrip('.').lower()
    if ext not in SUPPORTED_IMAGE_TYPES:
        raise ValidationError(f"不支持的图片格式，支持的格式: {', '.join(SUPPORTED_IMAGE_TYPES)}")

    # 检查文件头
    with open(file_path, 'rb') as f:
        file_header = f.read(12)

    signature = FILE_SIGNATURES.get(ext)
    if signature:
        if ext == 'webp':
            # WebP需要特殊检查
            if not (file_header[:4] == b'RIFF' and file_header[8:12] == b'WEBP'):
                raise ValidationError(f'WebP文件头不匹配 - 期望: RIFF...WEBP, 实际: {file_header.hex()}')
        else:
            if not file_header.startswith(signature):
                raise ValidationError(f'文件头不匹配 - 扩展名: {ext}, 期望签名: {signature.hex()}, 实际文件头: {file_header.hex()}')

    return {
        'valid': True,
        'size': file_size,
        'format': ext.upper()
    }


def convert_to_webp(input_path: str, output_path: str, quality: int = 85) -> str:
    """
    将图片转换为WebP格式

    Args:
        input_path: 输入图片路径
        output_path: 输出WebP路径
        quality: WebP质量 (0-100)

    Returns:
        转换后的WebP文件路径
    """
    try:
        from PIL import Image
    except ImportError:
        raise ValidationError("PIL (Pillow) is required for image conversion. Please install it with: pip install Pillow")

    try:
        with Image.open(input_path) as img:
            # 如果是PNG且有透明度，保持透明度
            if img.format == 'PNG' and img.mode in ('RGBA', 'LA'):
                img.save(output_path, 'WebP', quality=quality, lossless=False)
            else:
                # 转换为RGB模式（WebP不支持某些模式）
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGB')
                img.save(output_path, 'WebP', quality=quality)

        return output_path

    except Exception as e:
        raise ValidationError(f"图片转换为WebP失败: {str(e)}")


def _safe_base64_decode(base64_data: str) -> bytes:
    """安全的Base64解码，防止内存耗尽攻击"""
    # 1. 检查Base64数据大小
    if len(base64_data) > MAX_BASE64_SIZE:
        raise ValidationError(f"Base64数据过大，最大支持 {MAX_BASE64_SIZE // 1024}KB 编码后的数据")

    # 2. 预估解码后的大小
    estimated_size = len(base64_data) * 3 // 4
    if estimated_size > MAX_FILE_SIZE:
        raise ValidationError(f"Base64解码后预估文件大小超限，最大支持 {MAX_FILE_SIZE_MB}MB")

    try:
        # 3. 分块解码以控制内存使用
        decoded_chunks = []
        total_decoded_size = 0

        # 确保Base64数据是4的倍数长度
        padding_needed = len(base64_data) % 4
        if padding_needed:
            base64_data += '=' * (4 - padding_needed)

        # 分块处理
        for i in range(0, len(base64_data), BASE64_CHUNK_SIZE):
            chunk = base64_data[i:i + BASE64_CHUNK_SIZE]
            # 确保块是完整的Base64单元（4字符）
            if len(chunk) % 4 != 0 and i + BASE64_CHUNK_SIZE < len(base64_data):
                # 如果不是最后一个块且不是4的倍数，调整块大小
                chunk = base64_data[i:i + (BASE64_CHUNK_SIZE // 4) * 4]

            decoded_chunk = base64.b64decode(chunk, validate=True)
            total_decoded_size += len(decoded_chunk)

            # 实时检查解码后的总大小
            if total_decoded_size > MAX_FILE_SIZE:
                raise ValidationError(f"Base64解码后文件大小超限，最大支持 {MAX_FILE_SIZE_MB}MB")

            decoded_chunks.append(decoded_chunk)

        return b''.join(decoded_chunks)

    except Exception as e:
        if "Invalid base64" in str(e) or "Incorrect padding" in str(e):
            raise ValidationError("无效的Base64编码格式")
        raise


async def download_image(url: str, save_path: str) -> str:
    """从URL下载图片或处理base64数据"""
    try:
        # 检查是否为 base64 data URL
        if url.startswith('data:'):
            # 解析 data URL: data:image/png;base64,iVBORw0KGgo...
            match = re.match(r'data:image/[^;]+;base64,(.+)', url)
            if not match:
                raise ValidationError("无效的 data URL 格式")

            # 安全解码 base64 数据
            base64_data = match.group(1)
            image_data = _safe_base64_decode(base64_data)

            # 写入文件
            with open(save_path, 'wb') as f:
                f.write(image_data)

            return save_path

        # 处理普通 HTTP/HTTPS URL
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                response.raise_for_status()

                # 异步写入文件
                with open(save_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)

        return save_path

    except Exception as e:
        if os.path.exists(save_path):
            os.remove(save_path)
        raise UploadError(f"下载图片失败: {str(e)}")


async def upload_image(
    image_url: str,
    custom_filename: Optional[str] = None,
    enable_webp_conversion: bool = True,
    client: Optional[DogecloudClient] = None
) -> Dict[str, Any]:
    """
    上传图片到多吉云存储（简化API）

    Args:
        image_url: 图片URL，支持HTTP/HTTPS URL或Base64 data URL
        custom_filename: 自定义文件名（可选）
        enable_webp_conversion: 是否启用WebP转换（默认True）
        client: 多吉云客户端实例（可选，为空时自动创建）

    Returns:
        包含上传结果的字典
    """
    # 使用上下文管理器确保资源清理
    with _TempFileManager() as temp_manager:
        # 图片上传函数增强：在开始处添加空数据检查
        if not image_url:
            return {
                "success": False,
                "error": "image_url参数为空，无法进行图片上传",
                "file_url": None,
                "object_key": None,
                "filename": None,
                "size": 0,
                "format": None
            }

        # 额外检查空字符串
        if isinstance(image_url, str) and image_url.strip() == "":
            return {
                "success": False,
                "error": "image_url参数为空字符串，无法进行图片上传",
                "file_url": None,
                "object_key": None,
                "filename": None,
                "size": 0,
                "format": None
            }

        # 验证URL格式
        if not (image_url.startswith(('http://', 'https://', 'data:'))):
            raise ValidationError(
                "image_url 必须是以下格式之一：\n"
                "1. HTTP/HTTPS URL (如: https://example.com/image.jpg)\n"
                "2. Base64 data URL (如: data:image/jpeg;base64,/9j/4AAQ...)"
            )

        # 创建临时文件
        # 正确解析扩展名：data URL 和普通URL分别处理
        if image_url.startswith('data:image/'):
            # 从 data URL 中提取图片格式：data:image/png;base64,xxx
            format_match = re.match(r'data:image/([^;]+)', image_url)
            if format_match:
                ext = format_match.group(1).lower()
                # 标准化格式名称
                if ext == 'jpeg':
                    ext = 'jpg'
            else:
                ext = 'png'  # data URL默认为PNG
        else:
            # 解析普通URL获取扩展名，处理查询参数
            url_path = image_url.split('?')[0]
            _, ext = os.path.splitext(url_path)
            ext = ext.lstrip('.').lower()

        # 验证扩展名
        if ext not in SUPPORTED_IMAGE_TYPES:
            ext = 'jpg'  # 默认扩展名

        # 使用安全的临时文件管理器
        temp_file = temp_manager.create_temp_file(suffix=f'.{ext}')
        temp_file.close()

        image_path = await download_image(image_url, temp_file.name)

        # 验证图片文件
        validation_result = validate_image_file(image_path)

        # 计算原始文件的MD5
        with open(image_path, 'rb') as f:
            original_data = f.read()
            original_md5 = hashlib.md5(original_data).hexdigest()

        # 获取或创建客户端
        if client is None:
            client = DogecloudClient()

        # 决定是否转换为WebP
        upload_path = image_path
        _, original_ext = os.path.splitext(image_path)
        original_ext = original_ext.lstrip('.').lower()

        # 使用客户端配置的压缩设置，而不是函数参数
        if client.enable_compression and enable_webp_conversion:
            # 创建临时WebP文件
            webp_temp_file = temp_manager.create_temp_file(suffix='.webp')
            webp_temp_file.close()

            # 转换为WebP
            webp_path = convert_to_webp(image_path, webp_temp_file.name)
            upload_path = webp_path

            # 确定文件名 - 使用webp扩展名
            if custom_filename:
                base_name = custom_filename.split('.')[0] if '.' in custom_filename else custom_filename
                filename = f"{base_name}.webp"
            else:
                filename = f"{uuid.uuid4()}.webp"
        else:
            # 确定文件名 - 保持原始扩展名
            if custom_filename:
                if '.' not in custom_filename:
                    filename = f"{custom_filename}.{original_ext}"
                else:
                    filename = custom_filename
            else:
                filename = f"{uuid.uuid4()}.{original_ext}"

        # 上传文件
        upload_result = await client.upload_file(upload_path, filename, 'image')

        # 添加额外信息
        upload_result['size'] = validation_result['size']
        upload_result['format'] = validation_result['format']
        upload_result['original_md5'] = original_md5

        return upload_result


async def upload_file(
    file_path: str,
    filename: Optional[str] = None,
    file_type: str = 'html',
    client: Optional[DogecloudClient] = None
) -> Dict[str, Any]:
    """
    上传文件到多吉云存储（简化API）

    Args:
        file_path: 本地文件路径
        filename: 上传后的文件名（可选，默认使用原文件名）
        file_type: 文件类型 ('html', 'image' 等)
        client: 多吉云客户端实例（可选，为空时自动创建）

    Returns:
        包含上传结果的字典
    """
    if not os.path.exists(file_path):
        raise ValidationError(f"文件不存在: {file_path}")

    if filename is None:
        filename = os.path.basename(file_path)

    # 获取或创建客户端
    if client is None:
        client = DogecloudClient()

    return await client.upload_file(file_path, filename, file_type)


# 同步包装器
def upload_image_sync(*args, **kwargs):
    """upload_image的同步版本"""
    return asyncio.run(upload_image(*args, **kwargs))


def upload_file_sync(*args, **kwargs):
    """upload_file的同步版本"""
    return asyncio.run(upload_file(*args, **kwargs))