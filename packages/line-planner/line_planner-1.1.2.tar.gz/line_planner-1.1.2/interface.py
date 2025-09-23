#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
航线规划器 - 统一入口
====================

这是航线规划器的主程序入口，支持多种调用方式：
- 命令行参数模式
- JSON配置文件模式
- 标准输入输出模式
"""

import os
import sys

# 将src目录添加到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# 导入并运行主程序
try:
    from line_planner.main import main
except ImportError as e:
    print(f"错误: 无法导入主模块: {e}", file=sys.stderr)
    print("请确保项目结构正确，src/line_planner/ 目录存在", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())
