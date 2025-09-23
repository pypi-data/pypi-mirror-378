"""
多吉云客户端核心模块
"""

import os
import json
import time
import uuid
import logging
import threading
import hashlib
import hmac
import tempfile
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

import requests
import asyncio
from dotenv import load_dotenv
from botocore.config import Config

from .exceptions import DogecloudError, AuthenticationError, UploadError, ConfigurationError

# 配置日志
logger = logging.getLogger(__name__)

# 常量定义
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024
CREDENTIAL_REFRESH_BUFFER_SECONDS = 300
CREDENTIAL_REFRESH_BUFFER_MS = CREDENTIAL_REFRESH_BUFFER_SECONDS * 1000


class DogecloudClient:
    """多吉云客户端"""

    def __init__(self, access_key: Optional[str] = None, secret_key: Optional[str] = None,
                 bucket_name: Optional[str] = None, cdn_domain: Optional[str] = None,
                 enable_compression: Optional[bool] = None):
        """
        初始化多吉云客户端

        Args:
            access_key: 访问密钥，为空时从环境变量获取
            secret_key: 密钥，为空时从环境变量获取
            bucket_name: 存储桶名称，为空时从环境变量获取
            cdn_domain: CDN域名，为空时从环境变量获取
            enable_compression: 是否启用压缩，为空时从环境变量获取
        """
        # 确保环境变量被加载
        self._ensure_env_loaded()

        self.access_key = access_key or os.getenv('DOGECLOUD_ACCESS_KEY')
        self.secret_key = secret_key or os.getenv('DOGECLOUD_SECRET_KEY')
        self.bucket_name = bucket_name or os.getenv('DOGECLOUD_BUCKET_NAME', 'default-bucket')
        self.cdn_domain = cdn_domain or os.getenv('DOGECLOUD_CDN_DOMAIN')
        self.enable_compression = (
            enable_compression if enable_compression is not None
            else os.getenv('DOGECLOUD_ENABLE_COMPRESSION', 'true').lower() == 'true'
        )

        # 临时凭证缓存
        self._temp_credentials = None
        self._temp_bucket_info = None
        self._credentials_expire_time = 0
        self._credentials_lock = threading.Lock()

        if not self.access_key or not self.secret_key:
            raise ConfigurationError("多吉云 Access Key 和 Secret Key 必须配置")

    def _ensure_env_loaded(self):
        """确保环境变量在各种场景下都能正确加载"""
        # 如果环境变量已经存在，无需重复加载
        if os.getenv('DOGECLOUD_ACCESS_KEY'):
            return

        # 查找 .env 文件的可能位置
        possible_paths = [
            '.env',  # 当前目录
            '../.env',  # 上级目录
            '../../.env',  # 上上级目录
            Path(__file__).parent.parent.parent / '.env',  # 项目根目录
        ]

        for env_path in possible_paths:
            if Path(env_path).exists():
                load_dotenv(env_path)
                if os.getenv('DOGECLOUD_ACCESS_KEY'):  # 验证加载成功
                    break

    def _secure_clear_credentials(self):
        """安全清理临时凭证"""
        if self._temp_credentials:
            # 安全清零敏感字段
            for key in ['accessKeyId', 'secretAccessKey', 'sessionToken']:
                if key in self._temp_credentials:
                    # 用随机数据覆盖原始内存位置
                    self._temp_credentials[key] = 'x' * len(self._temp_credentials[key])
                    self._temp_credentials[key] = None
            self._temp_credentials = None

        if self._temp_bucket_info:
            # 清零可能包含敏感信息的bucket配置
            self._temp_bucket_info = None

        self._credentials_expire_time = 0

    def _generate_signature(self, api_path: str, body: str = '') -> str:
        """生成API请求签名"""
        sign_str = f"{api_path}\n{body}"
        h = hmac.new(self.secret_key.encode(), sign_str.encode(), hashlib.sha1)
        return h.hexdigest()

    async def _dogecloud_api(self, api_path: str, data: Dict = None, json_mode: bool = False) -> Dict:
        """调用多吉云API"""
        if data is None:
            data = {}

        if json_mode:
            body = json.dumps(data)
            content_type = 'application/json'
        else:
            # URL编码格式
            params = []
            for key, value in data.items():
                params.append(f"{key}={value}")
            body = '&'.join(params)
            content_type = 'application/x-www-form-urlencoded'

        sign = self._generate_signature(api_path, body)
        authorization = f"TOKEN {self.access_key}:{sign}"

        headers = {
            'Authorization': authorization,
            'Content-Type': content_type
        }

        try:
            response = requests.post(
                f"https://api.dogecloud.com{api_path}",
                data=body,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
        except requests.RequestException as e:
            raise AuthenticationError(f"多吉云API请求失败: {str(e)}")

        try:
            result = response.json()
        except json.JSONDecodeError as e:
            raise DogecloudError(f"API响应解析失败: {str(e)}")

        if result.get('code') != 200:
            raise DogecloudError(f"多吉云API错误: {result.get('msg', '未知错误')}")

        return result.get('data', result)

    async def get_temp_credentials(self) -> Tuple[Dict, Dict]:
        """获取临时授权凭证"""
        with self._credentials_lock:
            # 检查缓存
            now = time.time() * 1000
            # 如果凭证已过期，安全清理
            if self._temp_credentials and self._credentials_expire_time <= now:
                logger.debug("临时凭证已过期，进行安全清理")
                self._secure_clear_credentials()

            # 检查有效缓存
            if self._temp_credentials and self._credentials_expire_time > now + 60000:
                return self._temp_credentials, self._temp_bucket_info

        # 获取新凭证前，清理旧凭证
        self._secure_clear_credentials()

        # 获取新凭证
        response = await self._dogecloud_api(
            '/auth/tmp_token.json',
            {
                'channel': 'OSS_FULL',
                'scopes': ['*']
            },
            json_mode=True
        )

        if not response.get('Credentials') or not response.get('Buckets'):
            raise AuthenticationError("获取临时凭证失败: 响应格式不正确")

        with self._credentials_lock:
            self._temp_credentials = response['Credentials']
            self._temp_bucket_info = response['Buckets'][0]

            # 设置过期时间（提前5分钟）
            # 多吉云返回的是 ExpiredAt Unix时间戳
            expire_timestamp = response.get('ExpiredAt', 0)
            self._credentials_expire_time = expire_timestamp * 1000 - CREDENTIAL_REFRESH_BUFFER_MS

            return self._temp_credentials, self._temp_bucket_info

    async def get_s3_client(self):
        """获取S3客户端实例"""
        try:
            import boto3
        except ImportError:
            raise ConfigurationError("boto3 is required for S3 operations. Please install it with: pip install boto3")

        credentials, bucket_info = await self.get_temp_credentials()

        return boto3.client(
            's3',
            endpoint_url=bucket_info['s3Endpoint'],  # 使用正确的endpoint，不包含桶名
            region_name='ap-guangzhou',
            aws_access_key_id=credentials['accessKeyId'],
            aws_secret_access_key=credentials['secretAccessKey'],
            aws_session_token=credentials['sessionToken'],
            config=Config(
                s3={
                    'addressing_style': 'virtual'  # 使用虚拟主机风格
                },
                request_checksum_calculation='when_required',
                response_checksum_validation='when_required'
            )
        )

    def get_file_info(self, filename: str, file_type: str = 'html') -> Tuple[str, str]:
        """获取文件类型和存储路径"""
        _, ext = os.path.splitext(filename)
        ext = ext.lstrip('.').lower()

        content_types = {
            'html': 'text/html',
            'htm': 'text/html',
            'txt': 'text/plain',
            'json': 'application/json',
            'xml': 'application/xml',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'bmp': 'image/bmp'
        }

        content_type = content_types.get(ext, 'application/octet-stream')

        # 根据文件类型设置路径前缀
        if file_type == 'image' or ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']:
            object_key = f"images/{filename}"
        else:
            object_key = f"agent/html/{filename}"

        return content_type, object_key

    async def upload_file(self, file_path: str, filename: str, file_type: str = 'html') -> Dict[str, Any]:
        """
        上传文件到多吉云

        Args:
            file_path: 本地文件路径
            filename: 上传后的文件名
            file_type: 文件类型 ('html', 'image' 等)

        Returns:
            包含上传结果的字典
        """
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                # 获取文件信息
                content_type, object_key = self.get_file_info(filename, file_type)

                # 获取S3客户端和bucket信息
                s3 = await self.get_s3_client()
                _, bucket_info = await self.get_temp_credentials()

                # 调试信息 - 打印上传参数
                logger.debug("上传参数调试:")
                logger.debug(f"  file_path: {file_path}")
                logger.debug(f"  bucket: {bucket_info['s3Bucket']}")
                logger.debug(f"  object_key: {object_key}")
                logger.debug(f"  content_type: {content_type}")

                # 计算上传前的文件hash
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                    upload_md5 = hashlib.md5(file_data).hexdigest()
                logger.info(f"上传前文件MD5: {upload_md5}")

                # 上传文件 - 使用upload_fileobj方法
                with open(file_path, 'rb') as f:
                    s3.upload_fileobj(
                        f,
                        bucket_info['s3Bucket'],  # 使用完整的S3桶名
                        object_key,
                        ExtraArgs={'ContentType': content_type}
                    )

                # 验证文件是否真的上传成功
                try:
                    head_response = s3.head_object(
                        Bucket=bucket_info['s3Bucket'],  # 同样使用S3桶名
                        Key=object_key
                    )
                    logger.info(f"文件上传成功，对象信息: ETag={head_response.get('ETag')}")
                except Exception as head_e:
                    raise UploadError(f"文件上传后无法找到: {head_e}")

                # 构建文件URL - CDN已经绑定到特定桶，URL中不需要桶名
                file_url = (
                    f"{self.cdn_domain}/{object_key}"
                    if self.cdn_domain
                    else f"{bucket_info['s3EndpointHost']}/{object_key}"
                )

                return {
                    'success': True,
                    'file_url': file_url,
                    'object_key': object_key,
                    'filename': filename,
                    'md5': upload_md5
                }

            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    raise UploadError(f"上传文件到多吉云失败: {str(e)}")
                await asyncio.sleep(2 * retry_count)