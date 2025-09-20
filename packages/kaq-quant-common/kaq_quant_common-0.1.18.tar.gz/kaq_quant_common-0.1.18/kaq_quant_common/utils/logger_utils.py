import logging
import os
import sys
from typing import Union

from dagster import get_dagster_logger
from loguru import logger

# 清除所有已添加的处理器（包括默认控制台输出）
logger.remove()
# 自定义日志输出
logger.add(
    # 输出到标准输出（控制台）
    sink=sys.stdout,
    # TODO 配置
    level="INFO",
    #
    # format="{time} {level} [{extra[module]}] {message}",  # 显示绑定的module
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level}</level> | "
        "<cyan>[{extra[module]}]</cyan>"
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    ),
    # 启用颜色（默认已启用，显式指定更清晰）
    colorize=True,
)


def get_logger(obj: Union[str, object] = None):
    '''
    获取logger
    '''

    # 方法1: 检查Dagster特有的环境变量（推荐）
    # Dagster运行时会设置多个以DAGSTER_开头的环境变量
    is_dagster_env = any(key.startswith("DAGSTER_") for key in os.environ)

    name = obj or ""
    if isinstance(obj, str):
        # do nothing
        name = obj
    elif hasattr(obj, '__class__'):
        name = obj.__class__.__name__
    elif hasattr(obj, '__name__'):
        name = obj.__name__
    else:
        name = ""

    l = None
    if is_dagster_env:
        # TODO
        l = get_dagster_logger()
    else:
        # 使用loguru, 绑定module
        l = logger.bind(module=name)
    return l
