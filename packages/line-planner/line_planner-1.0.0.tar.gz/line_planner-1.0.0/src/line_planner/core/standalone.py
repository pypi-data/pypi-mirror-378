#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
航线规划独立实现模块
提供不依赖复杂模块的备用实现，当标准实现不可用时使用

特点：
- 最小化依赖
- 自包含实现
- 与标准实现接口兼容
"""

import math
import xml.etree.ElementTree as ET
import json
import logging
from typing import List, Tuple, Dict, Any, Optional


class StandaloneBoundaryParser:
    """独立的边界文件解析器"""
    
    @staticmethod
    def parse_kml_coordinates(kml_file: str, logger: Optional[logging.Logger] = None) -> Tuple[List[float], List[float]]:
        """
        解析KML文件获取坐标
        
        参数:
            kml_file: KML文件路径
            logger: 日志记录器
            
        返回:
            (boundary_lats, boundary_lons) 元组
        """
        try:
            if logger:
                logger.info(f"开始解析KML文件: {kml_file}")
                
            tree = ET.parse(kml_file)
            root = tree.getroot()
            
            # 处理命名空间
            ns = {'kml': 'http://www.opengis.net/kml/2.2'}
            
            # 查找coordinates元素
            coordinates_elem = root.find('.//kml:coordinates', ns)
            if coordinates_elem is None:
                # 尝试没有命名空间的情况
                coordinates_elem = root.find('.//coordinates')
            
            if coordinates_elem is None:
                raise ValueError("KML文件中未找到coordinates元素")
            
            # 解析坐标文本
            coordinates_text = coordinates_elem.text.strip()
            if logger:
                logger.info(f"找到coordinates文本，长度: {len(coordinates_text)}")
            
            # 分割坐标
            coordinate_pairs = []
            lines = coordinates_text.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line:
                    coordinate_pairs.extend(line.split())
            
            boundary_lats = []
            boundary_lons = []
            
            for coord_str in coordinate_pairs:
                coord_str = coord_str.strip()
                if coord_str:
                    try:
                        parts = coord_str.split(',')
                        if len(parts) >= 2:
                            lon = float(parts[0])
                            lat = float(parts[1])
                            boundary_lons.append(lon)
                            boundary_lats.append(lat)
                    except (ValueError, IndexError):
                        if logger:
                            logger.warning(f"跳过无效坐标: {coord_str}")
                        continue
            
            if logger:
                logger.info(f"解析完成，获得 {len(boundary_lats)} 个坐标点")
            
            if len(boundary_lats) < 3:
                raise ValueError(f"边界点数量不足，至少需要3个点，当前只有{len(boundary_lats)}个")
            
            return boundary_lats, boundary_lons
            
        except Exception as e:
            error_msg = f"解析KML文件失败: {str(e)}"
            if logger:
                logger.error(error_msg)
            raise ValueError(error_msg)


class StandalonePlanner:
    """独立的航线规划器"""
    
    def __init__(self):
        # 地球相关常数
        self.EARTH_RADIUS = 6378137.0  # WGS84椭球长半轴(米)
        self.METERS_PER_DEGREE_LAT = 111319.55  # 纬度每度对应米数(近似)
    
    def plan_flight_lines(self, 
                         boundary_lats: List[float], 
                         boundary_lons: List[float],
                         line_spacing: float,
                         rotation_angle: float = 0.0,
                         logger: Optional[logging.Logger] = None) -> List[Tuple[float, float]]:
        """
        生成蛇形航线的拐点
        
        参数:
            boundary_lats: 边界纬度列表 (WGS84)
            boundary_lons: 边界经度列表 (WGS84)  
            line_spacing: 航线间距 (米)
            rotation_angle: 航线旋转角度 (度，0-360)
            logger: 日志记录器
            
        返回:
            拐点列表: [(lat1, lon1), (lat2, lon2), ...]
        """
        
        if logger:
            logger.info("开始航线规划计算")
            logger.info(f"边界点数: {len(boundary_lats)}")
            logger.info(f"航线间距: {line_spacing}米")
            logger.info(f"旋转角度: {rotation_angle}度")
        
        if len(boundary_lats) < 3 or len(boundary_lons) < 3:
            raise ValueError("至少需要3个边界点组成多边形")
        
        if len(boundary_lats) != len(boundary_lons):
            raise ValueError("纬度和经度列表长度必须相等")
            
        if line_spacing <= 0:
            raise ValueError("航线间距必须大于0")
        
        # 1. 计算经纬度距离系数
        mean_lat = sum(boundary_lats) / len(boundary_lats)
        meters_per_degree_lon = self.METERS_PER_DEGREE_LAT * math.cos(math.radians(mean_lat))
        
        if logger:
            logger.info(f"区域中心纬度: {mean_lat:.6f}")
            logger.info(f"经度每度距离: {meters_per_degree_lon:.2f}米")
        
        # 2. 转换为局部坐标系（米）
        min_lat, max_lat = min(boundary_lats), max(boundary_lats)
        min_lon, max_lon = min(boundary_lons), max(boundary_lons)
        
        # 坐标转换：经纬度 -> 米
        local_x = [(lon - min_lon) * meters_per_degree_lon for lon in boundary_lons]
        local_y = [(lat - min_lat) * self.METERS_PER_DEGREE_LAT for lat in boundary_lats]
        
        if logger:
            logger.info(f"转换为局部坐标系，范围: X={min(local_x):.1f}~{max(local_x):.1f}m, Y={min(local_y):.1f}~{max(local_y):.1f}m")
        
        # 3. 应用旋转
        if rotation_angle != 0:
            angle_rad = math.radians(rotation_angle)
            cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
            
            # 计算旋转中心
            center_x = sum(local_x) / len(local_x)
            center_y = sum(local_y) / len(local_y)
            
            # 旋转坐标
            rotated_x = []
            rotated_y = []
            for x, y in zip(local_x, local_y):
                dx, dy = x - center_x, y - center_y
                new_x = center_x + dx * cos_a - dy * sin_a
                new_y = center_y + dx * sin_a + dy * cos_a
                rotated_x.append(new_x)
                rotated_y.append(new_y)
            
            local_x, local_y = rotated_x, rotated_y
            if logger:
                logger.info(f"应用旋转 {rotation_angle}度")
        
        # 4. 生成扫描线
        min_y, max_y = min(local_y), max(local_y)
        scan_lines = []
        current_y = min_y + line_spacing / 2
        
        while current_y < max_y:
            scan_lines.append(current_y)
            current_y += line_spacing
        
        if logger:
            logger.info(f"生成 {len(scan_lines)} 条扫描线")
        
        # 5. 计算每条扫描线与边界的交点
        turn_points = []
        
        for i, scan_y in enumerate(scan_lines):
            intersections = []
            
            # 计算与每条边的交点
            for j in range(len(local_x)):
                x1, y1 = local_x[j], local_y[j]
                x2, y2 = local_x[(j + 1) % len(local_x)], local_y[(j + 1) % len(local_x)]
                
                # 检查边是否跨越扫描线
                if (y1 <= scan_y <= y2) or (y2 <= scan_y <= y1):
                    if abs(y2 - y1) > 1e-10:  # 避免除零错误
                        # 线性插值计算交点x坐标
                        t = (scan_y - y1) / (y2 - y1)
                        intersect_x = x1 + t * (x2 - x1)
                        intersections.append(intersect_x)
            
            # 排序交点并提取拐点
            intersections.sort()
            
            if len(intersections) >= 2:
                # 蛇形路径：奇数行从左到右，偶数行从右到左
                if i % 2 == 0:
                    # 从左到右
                    start_x, end_x = intersections[0], intersections[-1]
                else:
                    # 从右到左
                    start_x, end_x = intersections[-1], intersections[0]
                
                # 转换回经纬度坐标
                if rotation_angle != 0:
                    # 逆旋转
                    angle_rad = math.radians(-rotation_angle)
                    cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
                    
                    # 逆旋转起点
                    dx, dy = start_x - center_x, scan_y - center_y
                    start_x_orig = center_x + dx * cos_a - dy * sin_a
                    start_y_orig = center_y + dx * sin_a + dy * cos_a
                    
                    # 逆旋转终点
                    dx, dy = end_x - center_x, scan_y - center_y
                    end_x_orig = center_x + dx * cos_a - dy * sin_a
                    end_y_orig = center_y + dx * sin_a + dy * cos_a
                    
                    start_x, start_y = start_x_orig, start_y_orig
                    end_x, end_y = end_x_orig, end_y_orig
                else:
                    start_y = end_y = scan_y
                
                # 转换回经纬度
                start_lat = min_lat + start_y / self.METERS_PER_DEGREE_LAT
                start_lon = min_lon + start_x / meters_per_degree_lon
                end_lat = min_lat + end_y / self.METERS_PER_DEGREE_LAT
                end_lon = min_lon + end_x / meters_per_degree_lon
                
                turn_points.append((start_lat, start_lon))
                turn_points.append((end_lat, end_lon))
        
        if logger:
            logger.info(f"生成 {len(turn_points)} 个拐点")
        
        return turn_points
    
    def calculate_total_distance(self, waypoints: List[Tuple[float, float]]) -> float:
        """
        计算总飞行距离
        
        参数:
            waypoints: 航点列表 [(lat, lon), ...]
            
        返回:
            总距离(米)
        """
        if len(waypoints) < 2:
            return 0.0
        
        total_distance = 0.0
        
        for i in range(len(waypoints) - 1):
            lat1, lon1 = waypoints[i]
            lat2, lon2 = waypoints[i + 1]
            
            # 使用简化的距离公式（适用于小范围）
            mean_lat = (lat1 + lat2) / 2
            meters_per_degree_lon = self.METERS_PER_DEGREE_LAT * math.cos(math.radians(mean_lat))
            
            dx = (lon2 - lon1) * meters_per_degree_lon
            dy = (lat2 - lat1) * self.METERS_PER_DEGREE_LAT
            distance = math.sqrt(dx*dx + dy*dy)
            
            total_distance += distance
        
        return total_distance


def validate_config(config: Dict[str, Any], logger: Optional[logging.Logger] = None) -> None:
    """
    验证配置参数
    
    参数:
        config: 配置字典
        logger: 日志记录器
    """
    if logger:
        logger.info("开始验证配置参数")
    
    required_fields = ['kml_file', 'line_spacing', 'rotation_angle', 'save_dir']
    
    for field in required_fields:
        if field not in config:
            error_msg = f"缺少必要配置项: {field}"
            if logger:
                logger.error(error_msg)
            raise ValueError(error_msg)
    
    # 验证KML文件存在
    import os
    kml_file = config['kml_file']
    if not os.path.exists(kml_file):
        error_msg = f"KML文件不存在: {kml_file}"
        if logger:
            logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    # 验证参数类型和范围
    try:
        line_spacing = float(config['line_spacing'])
        if line_spacing <= 0:
            raise ValueError("航线间距必须大于0")
    except (ValueError, TypeError):
        raise ValueError("航线间距必须是有效正数")
    
    try:
        rotation_angle = float(config['rotation_angle'])
    except (ValueError, TypeError):
        raise ValueError("旋转角度必须是有效数字")
    
    # 确保保存目录存在
    import os
    save_dir = config['save_dir']
    if not os.path.exists(save_dir):
        try:
            os.makedirs(save_dir, exist_ok=True)
            if logger:
                logger.info(f"创建保存目录: {save_dir}")
        except Exception as e:
            error_msg = f"无法创建保存目录: {str(e)}"
            if logger:
                logger.error(error_msg)
            raise OSError(error_msg)
    
    if logger:
        logger.info("配置验证完成")