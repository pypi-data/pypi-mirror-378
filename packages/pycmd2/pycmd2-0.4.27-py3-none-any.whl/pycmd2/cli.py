import logging

from pycmd2 import __build_date__
from pycmd2 import __version__
from pycmd2.common.cli import get_client

cli = get_client()
logger = logging.getLogger(__name__)


@cli.app.command("v", help="显示版本, 等效命令: version")
@cli.app.command("version", help="显示版本")
def version() -> None:
    logger.info(f"当前版本: {__version__}, 构建日期: {__build_date__}")
