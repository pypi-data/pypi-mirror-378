"""
自定义异常类
"""


class DogecloudError(Exception):
    """多吉云操作基础异常"""
    pass


class AuthenticationError(DogecloudError):
    """认证错误"""
    pass


class ValidationError(DogecloudError):
    """验证错误"""
    pass


class UploadError(DogecloudError):
    """上传错误"""
    pass


class ConfigurationError(DogecloudError):
    """配置错误"""
    pass