"""
多吉云上传工具包

支持图片和文件上传到多吉云存储，提供简单易用的API接口。
"""

from .client import DogecloudClient
from .utils import upload_image, upload_file

__version__ = "1.0.0"
__all__ = ["DogecloudClient", "upload_image", "upload_file"]