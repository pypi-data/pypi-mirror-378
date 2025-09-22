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

__version__ = "1.0.0-simplified"
__author__ = "Claude"
__email__ = "noreply@anthropic.com"

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