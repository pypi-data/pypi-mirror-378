#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
航线规划器统一入口
支持多种调用方式：命令行参数、JSON配置文件、标准输入

功能特点：
- 命令行参数模式
- 标准输入JSON配置模式
- 智能实现选择（标准API/独立实现）
- 友好的错误处理和帮助信息
"""

import argparse
import json
import os
import select
import sys
from typing import Any, Dict

from .api.stdin_processor import process_stdin_request


def has_stdin_data() -> bool:
    """
    检测标准输入是否有数据可读

    返回:
        bool: True如果有数据，False如果没有
    """
    try:
        # 使用select检测，超时时间0意味着非阻塞检测
        ready, _, _ = select.select([sys.stdin], [], [], 0)
        return bool(ready)
    except Exception:
        # 如果select不可用，返回False（无数据）
        return False


def create_sample_config(output_path: str = "config_template.json") -> None:
    """
    创建示例配置文件

    参数:
        output_path: 输出文件路径
    """
    sample_config = {
        "kml_file": "boundary.kml",
        "line_spacing": 25.0,
        "rotation_angle": 0.0,
        "save_dir": "./output",
    }

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(sample_config, f, indent=2, ensure_ascii=False)

        print(f"✓ 示例配置文件已创建: {output_path}")
        print("请编辑此文件后使用 --config 参数运行")

    except Exception as e:
        print(f"✗ 创建配置文件失败: {str(e)}", file=sys.stderr)
        sys.exit(1)


def process_with_config_file(
    config_file: str, quiet: bool = False, use_standalone: bool = False) -> Dict[str, Any]:
    """
    使用配置文件处理航线规划

    参数:
        config_file: 配置文件路径
        quiet: 静默模式
        use_standalone: 强制使用独立实现

    返回:
        处理结果
    """
    try:
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"配置文件不存在: {config_file}")

        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)

        if not quiet:
            print(f"从配置文件读取: {config_file}")
            print(f"  KML文件: {config.get('kml_file', 'N/A')}")
            print(f"  航线间距: {config.get('line_spacing', 'N/A')}m")
            print(f"  旋转角度: {config.get('rotation_angle', 'N/A')}°")
            print(f"  输出目录: {config.get('save_dir', 'N/A')}")

        # 简化版本：只使用独立实现
        from .api.stdin_processor import (
            create_timestamp_dir,
            generate_output_files,
            process_with_standalone,
            setup_logging,
        )

        # 创建时间戳目录和输出文件路径
        base_dir = config.get("save_dir", "./output")
        timestamp_dir = create_timestamp_dir(base_dir)
        output_files = generate_output_files(timestamp_dir)

        logger = None
        try:
            logger = setup_logging(output_files["log_file"])
        except Exception:
            pass

        result = process_with_standalone(config, timestamp_dir, output_files, logger)

        return result

    except Exception as e:
        return {"success": False, "error": str(e)}


def process_with_command_args(
    kml_file: str,
    line_spacing: float,
    rotation_angle: float,
    output_dir: str,
    quiet: bool = False,
    use_standalone: bool = False,) -> Dict[str, Any]:
    """
    使用命令行参数处理航线规划

    参数:
        kml_file: KML文件路径
        line_spacing: 航线间距
        rotation_angle: 旋转角度
        output_dir: 输出目录
        quiet: 静默模式
        use_standalone: 强制使用独立实现

    返回:
        处理结果
    """
    config = {
        "kml_file": kml_file,
        "line_spacing": line_spacing,
        "rotation_angle": rotation_angle,
        "save_dir": output_dir,
    }

    if not quiet:
        print("使用命令行参数:")
        print(f"  KML文件: {config['kml_file']}")
        print(f"  航线间距: {config['line_spacing']}m")
        print(f"  旋转角度: {config['rotation_angle']}°")
        print(f"  输出目录: {config['save_dir']}")

    # 简化版本：只使用独立实现
    from .api.stdin_processor import (
        create_timestamp_dir,
        generate_output_files,
        process_with_standalone,
        setup_logging,
    )

    # 创建时间戳目录和输出文件路径
    base_dir = config.get("save_dir", "./output")
    timestamp_dir = create_timestamp_dir(base_dir)
    output_files = generate_output_files(timestamp_dir)

    logger = None
    try:
        logger = setup_logging(output_files["log_file"])
    except:
        pass

    return process_with_standalone(config, timestamp_dir, output_files, logger)


def print_result(result: Dict[str, Any], quiet: bool = False) -> None:
    """
    打印处理结果

    参数:
        result: 处理结果
        quiet: 静默模式
    """
    if result["success"]:
        if quiet:
            # 静默模式只输出坐标JSON
            coords = [[point["lon"], point["lat"]] for point in result["turn_points"]]
            print(json.dumps({"coords": coords}, ensure_ascii=False))
        else:
            print("\n✓ 航线规划成功!")

            # 输出统计信息
            stats = result.get("statistics", {})
            print(f"  拐点数量: {stats.get('total_points', 'N/A')}")
            print(f"  总距离: {stats.get('total_distance_km', 'N/A'):.3f} km")
            print(
                f"  飞行时间@10m/s: {stats.get('estimated_flight_time_10ms_min', 'N/A'):.1f} 分钟"
            )

            # 输出文件信息
            if "output_files" in result:
                print("\n导出文件:")
                for format_name, file_path in result["output_files"].items():
                    print(f"  {format_name.upper()}: {file_path}")

            if "visualization_path" in result:
                print(f"\n可视化图像: {result['visualization_path']}")

            # 输出坐标JSON
            coords = [[point["lon"], point["lat"]] for point in result["turn_points"]]
            print("\n坐标JSON:")
            print(json.dumps({"coords": coords}, ensure_ascii=False))
    else:
        if quiet:
            print(
                json.dumps(
                    {"error": result.get("error", "未知错误")}, ensure_ascii=False
                )
            )
        else:
            print(f"\n✗ 航线规划失败: {result.get('error', '未知错误')}")


def main() -> int:
    """
    主函数

    返回:
        退出代码
    """
    parser = argparse.ArgumentParser(
        description="航线规划器统一入口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
                    使用示例:
                    # 从JSON配置文件规划
                    python main.py --config planning.json
                    
                    # 直接使用命令行参数规划
                    python main.py --kml boundary.kml --spacing 25 --angle 45 --output ./results
                    
                    # 创建示例配置文件
                    python main.py --create-template
                    
                    # 标准输入模式（自动检测，通过管道或重定向，默认静默输出）
                    echo '{"kml_file":"boundary.kml","line_spacing":25,"rotation_angle":0,"save_dir":"./output"}' | python main.py
                    type config.json | python main.py
                    
                    # 详细模式显示完整信息
                    python main.py --config planning.json --verbose
                    
                    # 强制使用独立实现
                    python main.py --kml boundary.kml --spacing 25 --standalone
                """,
    )

    # 模式选择参数（已改为自动检测标准输入）
    parser.add_argument("--config", "-c", help="JSON配置文件路径")
    parser.add_argument(
        "--create-template", action="store_true", help="创建示例配置文件模板"
    )

    # 命令行参数模式
    parser.add_argument("--kml", help="KML/KMZ文件路径")

    parser.add_argument(
        "--spacing", "-s", type=float, default=20.0, help="航线间距(米)，默认20.0"
    )

    parser.add_argument(
        "--angle", "-a", type=float, default=0.0, help="航线旋转角度(度)，默认0.0"
    )

    parser.add_argument(
        "--output", "-o", default="./output", help="输出目录，默认./output"
    )

    # 其他选项
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="详细模式，显示完整信息（默认为静默模式）",
    )

    parser.add_argument(
        "--standalone", action="store_true", help="强制使用独立实现（避免复杂依赖）"
    )

    parser.add_argument("--version", action="version", version="航线规划器 v1.0.0")

    args = parser.parse_args()

    try:
        # 创建配置模板
        if args.create_template:
            create_sample_config()
            return 0

        # 优先检测标准输入模式（自动检测）
        try:
            # 默认quiet模式，verbose时才显示详细信息
            quiet_mode = not args.verbose

            if args.verbose:
                print("检测到标准输入，使用JSON配置模式...")

            result = process_stdin_request(use_standalone=args.standalone)
            print_result(result, quiet_mode)
            return 0 if result["success"] else 1
        except Exception:
            # 没有标准输入数据，继续执行后续逻辑
            pass

        # 配置文件模式
        if args.config:
            quiet_mode = not args.verbose
            result = process_with_config_file(args.config, quiet_mode, args.standalone)
            print_result(result, quiet_mode)
            return 0 if result["success"] else 1

        # 命令行参数模式
        if args.kml:
            quiet_mode = not args.verbose
            result = process_with_command_args(
                kml_file=args.kml,
                line_spacing=args.spacing,
                rotation_angle=args.angle,
                output_dir=args.output,
                quiet=quiet_mode,
                use_standalone=args.standalone,
            )
            print_result(result, quiet_mode)
            return 0 if result["success"] else 1

        # 如果没有提供足够的参数，显示帮助
        parser.print_help()
        print("\n错误: 必须指定 --config 或 --kml 参数，或通过管道/重定向提供标准输入")
        return 1

    except KeyboardInterrupt:
        if args.verbose:
            print("\n操作被用户中断")
        return 130
    except Exception as e:
        if not args.verbose:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"程序执行错误: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
