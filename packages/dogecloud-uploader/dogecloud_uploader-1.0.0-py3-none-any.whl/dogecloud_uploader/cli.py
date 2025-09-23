"""
命令行接口
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Optional

import click

from .utils import upload_image, upload_file
from .client import DogecloudClient
from .exceptions import DogecloudError


@click.group()
@click.version_option()
def cli():
    """多吉云上传工具

    支持图片和文件上传到多吉云存储。
    """
    pass


@cli.command()
@click.argument('source', type=str)
@click.option('--filename', '-f', help='自定义文件名')
@click.option('--type', 'file_type', default='auto',
              type=click.Choice(['auto', 'image', 'html', 'file']),
              help='文件类型 (默认: auto)')
@click.option('--no-webp', is_flag=True, help='禁用WebP转换')
@click.option('--quality', default=85, type=int, help='WebP质量 (0-100, 默认: 85)')
@click.option('--verbose', '-v', is_flag=True, help='详细输出')
def upload(source: str, filename: Optional[str], file_type: str,
           no_webp: bool, quality: int, verbose: bool):
    """上传文件或图片到多吉云

    SOURCE 可以是:
    - 本地文件路径
    - HTTP/HTTPS URL
    - Base64 data URL
    """
    if verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)

    async def _upload():
        try:
            # 自动检测文件类型
            if file_type == 'auto':
                if source.startswith(('http://', 'https://', 'data:')):
                    detected_type = 'image'
                else:
                    # 根据文件扩展名判断
                    path = Path(source)
                    ext = path.suffix.lower()
                    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
                        detected_type = 'image'
                    elif ext in ['.html', '.htm']:
                        detected_type = 'html'
                    else:
                        detected_type = 'file'
            else:
                detected_type = file_type

            if detected_type == 'image' or source.startswith(('http://', 'https://', 'data:')):
                # 上传图片
                result = await upload_image(
                    source,
                    custom_filename=filename,
                    enable_webp_conversion=not no_webp
                )
            else:
                # 上传普通文件
                if not os.path.exists(source):
                    click.echo(f"错误: 文件不存在 {source}", err=True)
                    sys.exit(1)

                result = await upload_file(
                    source,
                    filename=filename or os.path.basename(source),
                    file_type=detected_type
                )

            if result['success']:
                click.echo(f"✅ 上传成功!")
                click.echo(f"🔗 文件URL: {result['file_url']}")
                if verbose:
                    click.echo(f"📁 对象键: {result['object_key']}")
                    click.echo(f"📄 文件名: {result['filename']}")
                    if 'size' in result:
                        click.echo(f"📊 文件大小: {result['size']} bytes")
                    if 'md5' in result:
                        click.echo(f"🔐 MD5: {result['md5']}")
            else:
                click.echo(f"❌ 上传失败: {result.get('error', '未知错误')}", err=True)
                sys.exit(1)

        except DogecloudError as e:
            click.echo(f"❌ 多吉云错误: {e}", err=True)
            sys.exit(1)
        except Exception as e:
            click.echo(f"❌ 未知错误: {e}", err=True)
            if verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)

    asyncio.run(_upload())


@cli.command()
@click.option('--access-key', help='多吉云Access Key')
@click.option('--secret-key', help='多吉云Secret Key')
@click.option('--bucket-name', help='存储桶名称')
@click.option('--cdn-domain', help='CDN域名')
def config(access_key: Optional[str], secret_key: Optional[str],
           bucket_name: Optional[str], cdn_domain: Optional[str]):
    """配置多吉云认证信息"""

    # 确定配置文件路径
    config_dir = Path.home() / '.dogecloud'
    config_dir.mkdir(exist_ok=True)
    config_file = config_dir / 'config'

    # 读取现有配置
    config_data = {}
    if config_file.exists():
        with open(config_file, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    config_data[key] = value

    # 更新配置
    if access_key:
        config_data['DOGECLOUD_ACCESS_KEY'] = access_key
    if secret_key:
        config_data['DOGECLOUD_SECRET_KEY'] = secret_key
    if bucket_name:
        config_data['DOGECLOUD_BUCKET_NAME'] = bucket_name
    if cdn_domain:
        config_data['DOGECLOUD_CDN_DOMAIN'] = cdn_domain

    # 写入配置文件
    with open(config_file, 'w') as f:
        for key, value in config_data.items():
            f.write(f"{key}={value}\n")

    click.echo(f"✅ 配置已保存到 {config_file}")
    click.echo("💡 提示: 你也可以使用环境变量来配置这些选项")


@cli.command()
def test():
    """测试连接和配置"""

    async def _test():
        try:
            client = DogecloudClient()
            click.echo("🔍 测试多吉云连接...")

            # 尝试获取临时凭证
            credentials, bucket_info = await client.get_temp_credentials()

            click.echo("✅ 连接测试成功!")
            click.echo(f"📦 存储桶: {bucket_info.get('s3Bucket', 'N/A')}")
            click.echo(f"🌐 终端点: {bucket_info.get('s3Endpoint', 'N/A')}")
            if client.cdn_domain:
                click.echo(f"🔗 CDN域名: {client.cdn_domain}")

            # 清理临时凭证
            client._secure_clear_credentials()

        except DogecloudError as e:
            click.echo(f"❌ 连接测试失败: {e}", err=True)
            sys.exit(1)
        except Exception as e:
            click.echo(f"❌ 测试失败: {e}", err=True)
            sys.exit(1)

    asyncio.run(_test())


@cli.command()
def version():
    """显示版本信息"""
    from . import __version__
    click.echo(f"dogecloud-uploader v{__version__}")


def main():
    """主入口点"""
    # 自动加载配置文件中的环境变量
    config_file = Path.home() / '.dogecloud' / 'config'
    if config_file.exists():
        with open(config_file, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ.setdefault(key, value)

    cli()


if __name__ == '__main__':
    main()