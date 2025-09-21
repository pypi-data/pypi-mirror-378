"""功能: 重命名文件级别后缀.

用法: filelevel -f FILES [FILES ...] -l level
"""

from __future__ import annotations

import logging
import typing
from functools import partial
from pathlib import Path
from typing import ClassVar
from typing import List

from typer import Argument
from typing_extensions import Annotated

from pycmd2.client import get_client
from pycmd2.config import TomlConfigMixin


class FileLevelConfig(TomlConfigMixin):
    """文件级别配置."""

    LEVELS: ClassVar[dict[str, str]] = {
        "0": "",
        "1": "PUB,NOR",
        "2": "INT",
        "3": "CON",
        "4": "CLA",
    }
    BRACKETS: ClassVar[list[str]] = [" ([_（【-", " )]_）】"]  # noqa: RUF001


cli = get_client()
conf = FileLevelConfig()
logger = logging.getLogger(__name__)


class FileLevel(typing.NamedTuple):
    """文件级别定义."""

    code: int
    names: list[str]


levels = [FileLevel(int(c), n.split(",")) for c, n in conf.LEVELS.items()]


def remove_marks(
    filename: str,
    marks: list[str],
) -> str:
    """移除文件名中的标记符.

    Returns:
        移除标记符后的文件名.
    """
    for mark in marks:
        pos = filename.find(mark)
        if pos != -1:
            b, e = pos - 1, pos + len(mark)
            if b >= 0 and e <= len(filename) - 1:
                if (
                    filename[b] not in conf.BRACKETS[0]
                    or filename[e] not in conf.BRACKETS[1]
                ):
                    return filename[:e] + remove_marks(filename[e:], marks)
                filename = filename.replace(filename[b : e + 1], "")
                return remove_marks(filename, marks)
    return filename


def remove_level_and_digital_mark(
    filename: str,
) -> str:
    for file_level in levels[1:]:
        filename = remove_marks(filename, file_level.names)

    return remove_marks(
        filename,
        list("".join([str(x) for x in range(1, 10)])),
    )


def add_level_mark(
    filepath: Path,
    filelevel: int,
    suffix: int,
) -> Path:
    cleared_stem = remove_level_and_digital_mark(filepath.stem)
    dst_stem = (
        f"{cleared_stem}({levels[filelevel].names[0]})"
        if filelevel
        else cleared_stem
    )

    if dst_stem == filepath.stem:
        logger.info(f"destination stem [{dst_stem}] equals to current.")
        return filepath
    dst_name = (
        f"{dst_stem}({suffix}){filepath.suffix}"
        if suffix
        else f"{dst_stem}{filepath.suffix}"
    )

    if filepath.with_name(dst_name).exists():
        logger.info(f"[{dst_name}] already exists.")
        return add_level_mark(filepath, filelevel, suffix + 1)
    logger.info(f"rename [{filepath.name}] to [{dst_name}].")
    return filepath.with_name(dst_name)


def rename(
    target: Path,
    level: int,
) -> None:
    target.rename(add_level_mark(target, level, 0))


@cli.app.command()
def main(
    targets: Annotated[List[Path], Argument(help="目标文件或目录")],
    level: Annotated[int, Argument(help="文件级别")] = 0,
) -> None:
    rename_func = partial(rename, level=level)
    cli.run(rename_func, targets)
