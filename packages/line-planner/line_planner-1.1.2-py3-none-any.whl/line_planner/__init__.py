#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
航线规划器 - 简化版

专为SIF设备优化的航线规划工具，使用独立实现。

主要功能:
- 从KML文件读取边界数据
- 生成蛇形航线拐点
- 支持标准输入JSON配置
- 内置可视化功能

快速开始:
    通过标准输入使用：
    echo '{"kml_file":"test.kml","line_spacing":25,"rotation_angle":0}' | python interface.py
"""

# 版本号获取，优先级：包元数据 > _version.py > fallback
try:
    from importlib.metadata import version, PackageNotFoundError
    try:
        __version__ = version("line-planner")
    except PackageNotFoundError:
        # 开发环境或未安装的包，尝试从_version.py获取
        try:
            from ._version import __version__
        except ImportError:
            __version__ = "1.0.0"  # fallback版本
except ImportError:
    # Python < 3.8，使用importlib_metadata
    try:
        from importlib_metadata import version, PackageNotFoundError
        try:
            __version__ = version("line-planner")
        except PackageNotFoundError:
            try:
                from ._version import __version__
            except ImportError:
                __version__ = "1.0.0"
    except ImportError:
        # 完全fallback
        try:
            from ._version import __version__
        except ImportError:
            __version__ = "1.0.0"

__author__ = "WayPoint Planning Team"
__email__ = "waypoint@example.com"

# 只导入必要的模块（用于调试或扩展时）
from .core.standalone import StandalonePlanner, StandaloneBoundaryParser

# 定义公开接口
__all__ = [
    # 独立实现
    'StandalonePlanner',
    'StandaloneBoundaryParser',
    
    # 版本信息
    '__version__',
]