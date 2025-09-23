#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标准输入输出处理器
支持通过stdin获取JSON配置，执行航线规划，输出结果到stdout

功能特点：
- 支持JSON配置输入
- 支持配置文件路径输入
- 生成可视化图像
- 结构化JSON输出
"""

import datetime
import json
import logging
import os
import sys
from typing import Any, Dict, Optional

# 独立实现的导入始终可用
from ..core.standalone import (
    StandaloneBoundaryParser,
    StandalonePlanner,
    validate_config,
)


def setup_logging(log_file_path: str) -> logging.Logger:
    """
    设置日志系统

    参数:
        log_file_path: 日志文件路径

    返回:
        配置好的logger
    """
    # 确保日志文件目录存在
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    # 创建logger
    logger = logging.getLogger("stdin_processor")
    logger.setLevel(logging.INFO)

    # 清除已有的处理器
    logger.handlers.clear()

    # 创建文件处理器
    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setLevel(logging.INFO)

    # 创建格式器
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    # 添加处理器到logger
    logger.addHandler(file_handler)

    return logger


def read_stdin_input() -> str:
    """
    从标准输入读取内容

    返回:
        输入的字符串内容
    """
    try:
        if sys.platform == "win32":
            # Windows系统：直接检测stdin是否为tty
            if sys.stdin.isatty():
                # 交互式终端，没有管道输入
                raise RuntimeError("没有检测到标准输入数据")

            # 非交互式，有管道/重定向输入，直接读取
            input_content = sys.stdin.read().strip()
            if not input_content:
                raise RuntimeError("标准输入为空")
            return input_content
        else:
            # Unix/Linux系统：使用select检测
            import select

            # 首先检测是否有数据可读（1秒超时）
            ready, _, _ = select.select([sys.stdin], [], [], 1.0)
            if not ready:
                # 1秒内没有数据，认为没有管道输入
                raise RuntimeError("没有检测到标准输入数据")

            # 有数据可读，执行实际读取
            input_content = sys.stdin.read().strip()
            return input_content
    except RuntimeError:
        # 重新抛出RuntimeError，让调用者处理
        raise
    except Exception as e:
        # 其他异常才输出错误
        error_data = {"error": f"读取标准输入失败: {str(e)}"}
        print(json.dumps(error_data, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


def parse_config(
    input_content: str, logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """
    解析配置内容

    参数:
        input_content: 输入内容（JSON配置或文件路径）
        logger: 日志记录器

    返回:
        配置字典
    """
    # 首先尝试作为JSON解析
    try:
        config = json.loads(input_content)
        if logger:
            logger.info("成功解析JSON配置")
        return config
    except json.JSONDecodeError:
        if logger:
            logger.info("输入内容不是有效JSON，尝试作为文件路径")

    # 如果不是JSON，尝试作为文件路径
    file_path = input_content.strip()

    if not os.path.exists(file_path):
        error_msg = f"无法解析输入内容，既不是有效JSON也不是存在的文件路径: {file_path}"
        if logger:
            logger.error(error_msg)
        error_data = {"error": error_msg}
        print(json.dumps(error_data, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        if logger:
            logger.info(f"成功从文件读取配置: {file_path}")
        return config
    except Exception as e:
        error_msg = f"读取配置文件失败: {str(e)}"
        if logger:
            logger.error(error_msg)
        error_data = {"error": error_msg}
        print(json.dumps(error_data, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


def create_timestamp_dir(base_dir: str) -> str:
    """
    创建时间戳目录

    参数:
        base_dir: 基础目录路径

    返回:
        创建的时间戳目录路径
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    timestamp_dir = os.path.join(base_dir, f"sif_planning_{timestamp}")
    os.makedirs(timestamp_dir, exist_ok=True)
    return timestamp_dir


def generate_output_files(timestamp_dir: str) -> Dict[str, str]:
    """
    生成输出文件路径字典

    参数:
        timestamp_dir: 时间戳目录路径

    返回:
        文件路径字典
    """
    return {
        "coords_json": os.path.join(timestamp_dir, "coordinates.json"),
        "visualization": os.path.join(timestamp_dir, "flight_plan.png"),
        "log_file": os.path.join(timestamp_dir, "processing.log"),
        "result_json": os.path.join(timestamp_dir, "result.json"),
    }


def process_with_standalone(
    config: Dict[str, Any],
    timestamp_dir: str,
    output_files: Dict[str, str],
    logger: Optional[logging.Logger] = None,) -> Dict[str, Any]:
    """
    使用独立实现处理航线规划

    参数:
        config: 配置字典
        timestamp_dir: 时间戳目录
        output_files: 输出文件路径字典
        logger: 日志记录器

    返回:
        处理结果
    """
    if logger:
        logger.info("使用独立实现进行航线规划")

    try:
        # 验证配置
        validate_config(config, logger)

        # 解析KML文件
        parser = StandaloneBoundaryParser()
        boundary_lats, boundary_lons = parser.parse_kml_coordinates(
            config["kml_file"], logger
        )

        # 执行航线规划
        planner = StandalonePlanner()
        turn_points = planner.plan_flight_lines(
            boundary_lats=boundary_lats,
            boundary_lons=boundary_lons,
            line_spacing=config["line_spacing"],
            rotation_angle=config["rotation_angle"],
            logger=logger,
        )

        # 计算统计信息
        total_distance = planner.calculate_total_distance(turn_points)

        # 构建结果
        result = {
            "success": True,
            "turn_points": [
                {
                    "lat": lat,
                    "lon": lon,
                    "type": "start"
                    if i == 0
                    else ("end" if i == len(turn_points) - 1 else "turn"),
                    "index": i,
                }
                for i, (lat, lon) in enumerate(turn_points)
            ],
            "statistics": {
                "total_points": len(turn_points),
                "total_distance_m": total_distance,
                "total_distance_km": total_distance / 1000,
                "estimated_flight_time_10ms_min": (total_distance / 10) / 60,
                "estimated_flight_time_15ms_min": (total_distance / 15) / 60,
            },
            "parameters": {
                "line_spacing": config["line_spacing"],
                "rotation_angle": config["rotation_angle"],
                "boundary_file": config["kml_file"],
            },
        }

        # 生成可视化（如果matplotlib可用）
        try:
            import matplotlib.pyplot as plt
            # 设置matplotlib支持中文，防止中文乱码
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'Microsoft YaHei']
            plt.rcParams['axes.unicode_minus'] = False

            plt.figure(figsize=(12, 8))

            # 绘制边界
            boundary_lons_closed = boundary_lons + [boundary_lons[0]]
            boundary_lats_closed = boundary_lats + [boundary_lats[0]]
            plt.plot(
                boundary_lons_closed,
                boundary_lats_closed,
                "k-",
                linewidth=2,
                label="边界",
            )
            plt.fill(
                boundary_lons_closed, boundary_lats_closed, color="lightgray", alpha=0.3
            )

            # 绘制拐点和路径
            if turn_points:
                lats, lons = zip(*turn_points)
                plt.plot(lons, lats, "ro-", linewidth=1, markersize=4, label="航线")

                # 标记起点和终点
                plt.plot(lons[0], lats[0], "go", markersize=8, label="起点")
                plt.plot(lons[-1], lats[-1], "ro", markersize=8, label="终点")

            plt.xlabel("经度")
            plt.ylabel("纬度")
            plt.title(
                f"航线规划结果\n间距: {config['line_spacing']}m, 角度: {config['rotation_angle']}°"
            )
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.axis("equal")

            plt.tight_layout()
            plt.savefig(output_files["visualization"], dpi=300, bbox_inches="tight")
            plt.close()

            result["visualization_path"] = output_files["visualization"]
            if logger:
                logger.info(f"可视化图像已保存: {output_files['visualization']}")

        except ImportError:
            if logger:
                logger.warning("matplotlib不可用，跳过可视化生成")
        except Exception as e:
            if logger:
                logger.warning(f"生成可视化失败: {str(e)}")
            result["visualization_error"] = str(e)

        # 保存坐标JSON文件
        try:
            coords = [[lon, lat] for lat, lon in turn_points]
            coords_data = {"coords": coords}

            with open(output_files["coords_json"], "w", encoding="utf-8") as f:
                json.dump(coords_data, f, ensure_ascii=False, indent=2)

            if logger:
                logger.info(f"坐标JSON已保存: {output_files['coords_json']}")

            result["coords_json_path"] = output_files["coords_json"]

        except Exception as e:
            if logger:
                logger.warning(f"保存坐标JSON失败: {str(e)}")

        # 保存完整结果JSON文件
        try:
            with open(output_files["result_json"], "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            if logger:
                logger.info(f"完整结果已保存: {output_files['result_json']}")

            result["result_json_path"] = output_files["result_json"]

        except Exception as e:
            if logger:
                logger.warning(f"保存完整结果失败: {str(e)}")

        # 添加输出目录信息
        result["output_directory"] = timestamp_dir

        return result

    except Exception as e:
        error_msg = str(e)
        if logger:
            logger.error(f"航线规划失败: {error_msg}")

        return {"success": False, "error": error_msg}


def process_stdin_request(use_standalone: bool = False) -> Dict[str, Any]:
    """
    处理标准输入请求

    参数:
        use_standalone: 是否强制使用独立实现

    返回:
        处理结果
    """
    logger = None

    try:
        # 1. 读取标准输入
        input_content = read_stdin_input()

        if not input_content:
            error_data = {"error": "未收到输入内容"}
            return error_data

        # 2. 解析配置
        config = parse_config(input_content)

        # 3. 创建时间戳目录和输出文件路径
        base_dir = config.get("save_dir", "./output")
        timestamp_dir = create_timestamp_dir(base_dir)
        output_files = generate_output_files(timestamp_dir)

        # 4. 设置日志
        try:
            logger = setup_logging(output_files["log_file"])
            logger.info("开始处理航线规划请求")
            logger.info(f"输出目录: {timestamp_dir}")
            logger.info(f"配置: {json.dumps(config, ensure_ascii=False)}")
        except Exception:
            pass  # 如果日志设置失败，继续处理但不记录日志

        # 5. 使用独立实现（恢复到原始简单逻辑）
        if logger:
            logger.info("使用独立实现模式")
        result = process_with_standalone(config, timestamp_dir, output_files, logger)

        if logger:
            if result["success"]:
                logger.info("航线规划成功完成")
            else:
                logger.error(f"航线规划失败: {result.get('error', '未知错误')}")

        return result

    except Exception as e:
        error_msg = f"处理请求时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)

        return {"success": False, "error": error_msg}
