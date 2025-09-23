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
import urllib.request
import tempfile
import os
import ssl
from typing import List, Tuple, Dict, Any, Optional


class StandaloneBoundaryParser:
    """独立的边界文件解析器"""
    
    @staticmethod
    def parse_kml_coordinates(kml_file: str, logger: Optional[logging.Logger] = None) -> Tuple[List[float], List[float]]:
        """
        解析KML文件获取坐标
        
        参数:
            kml_file: KML文件路径或URL
            logger: 日志记录器
            
        返回:
            (boundary_lats, boundary_lons) 元组
        """
        try:
            if logger:
                logger.info(f"开始解析KML文件: {kml_file}")
            
            # 检查是否为URL
            if kml_file.startswith(('http://', 'https://')):
                if logger:
                    logger.info("检测到URL，开始下载KML文件")
                
                # 下载文件到临时目录
                with tempfile.NamedTemporaryFile(mode='w+b', suffix='.kml', delete=False) as temp_file:
                    temp_path = temp_file.name
                    
                try:
                    # 创建SSL上下文，忽略证书验证
                    ssl_context = ssl.create_default_context()
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
                    
                    # 使用urllib.request.urlopen下载文件
                    with urllib.request.urlopen(kml_file, context=ssl_context) as response:
                        with open(temp_path, 'wb') as f:
                            f.write(response.read())
                    
                    if logger:
                        logger.info(f"KML文件下载完成: {temp_path}")
                    
                    # 解析下载的文件
                    tree = ET.parse(temp_path)
                    root = tree.getroot()
                    
                finally:
                    # 清理临时文件
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
            else:
                # 本地文件处理
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
    
    def point_in_polygon(self, x: float, y: float, polygon_x: List[float], polygon_y: List[float]) -> bool:
        """
        使用射线法判断点是否在多边形内部
        
        参数:
            x, y: 待检测点的坐标
            polygon_x, polygon_y: 多边形顶点坐标列表
            
        返回:
            True表示在内部，False表示在外部
        """
        n = len(polygon_x)
        inside = False
        
        j = n - 1
        for i in range(n):
            xi, yi = polygon_x[i], polygon_y[i]
            xj, yj = polygon_x[j], polygon_y[j]
            
            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
            
        return inside
    
    def line_segment_intersect_polygon(self, x1: float, y1: float, x2: float, y2: float, 
                                     polygon_x: List[float], polygon_y: List[float]) -> List[Tuple[float, float]]:
        """
        计算线段与多边形的所有交点
        
        参数:
            x1, y1, x2, y2: 线段端点坐标
            polygon_x, polygon_y: 多边形顶点坐标列表
            
        返回:
            交点列表 [(x, y), ...]
        """
        intersections = []
        n = len(polygon_x)
        
        for i in range(n):
            px1, py1 = polygon_x[i], polygon_y[i]
            px2, py2 = polygon_x[(i + 1) % n], polygon_y[(i + 1) % n]
            
            # 计算两条线段的交点
            intersection = self._line_intersection(x1, y1, x2, y2, px1, py1, px2, py2)
            if intersection:
                intersections.append(intersection)
        
        # 按照沿线段方向排序
        if intersections:
            intersections.sort(key=lambda p: (p[0] - x1) ** 2 + (p[1] - y1) ** 2)
        
        return intersections
    
    def _line_intersection(self, x1: float, y1: float, x2: float, y2: float,
                          x3: float, y3: float, x4: float, y4: float) -> Optional[Tuple[float, float]]:
        """
        计算两条线段的交点
        
        参数:
            (x1,y1)-(x2,y2): 第一条线段
            (x3,y3)-(x4,y4): 第二条线段
            
        返回:
            交点坐标或None
        """
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(denom) < 1e-10:
            return None
        
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
        
        if 0 <= t <= 1 and 0 <= u <= 1:
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            return (x, y)
        
        return None
    
    def clip_line_to_polygon(self, x1: float, y1: float, x2: float, y2: float,
                           polygon_x: List[float], polygon_y: List[float]) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
        """
        将线段裁剪到多边形内部
        
        参数:
            x1, y1, x2, y2: 线段端点
            polygon_x, polygon_y: 多边形顶点
            
        返回:
            裁剪后的线段列表 [((x1, y1), (x2, y2)), ...]
        """
        # 检查端点是否在多边形内
        start_inside = self.point_in_polygon(x1, y1, polygon_x, polygon_y)
        end_inside = self.point_in_polygon(x2, y2, polygon_x, polygon_y)
        
        if start_inside and end_inside:
            # 整条线段都在内部
            return [((x1, y1), (x2, y2))]
        
        # 计算与多边形的交点
        intersections = self.line_segment_intersect_polygon(x1, y1, x2, y2, polygon_x, polygon_y)
        
        if not intersections:
            # 没有交点，整条线段在外部
            return []
        
        # 构建候选线段
        points = [(x1, y1)] + intersections + [(x2, y2)]
        segments = []
        
        for i in range(len(points) - 1):
            p1, p2 = points[i], points[i + 1]
            # 检查线段中点是否在多边形内
            mid_x = (p1[0] + p2[0]) / 2
            mid_y = (p1[1] + p2[1]) / 2
            
            if self.point_in_polygon(mid_x, mid_y, polygon_x, polygon_y):
                segments.append((p1, p2))
        
        return segments
    
    def generate_boundary_following_path(self, start_point: Tuple[float, float], end_point: Tuple[float, float],
                                       polygon_x: List[float], polygon_y: List[float]) -> List[Tuple[float, float]]:
        """
        生成沿边界的跟踪路径
        
        参数:
            start_point: 起始点 (x, y)
            end_point: 结束点 (x, y)
            polygon_x, polygon_y: 多边形顶点
            
        返回:
            边界跟踪路径点列表
        """
        # 找到距离起始点和结束点最近的边界点
        start_boundary = self._find_nearest_boundary_point(start_point, polygon_x, polygon_y)
        end_boundary = self._find_nearest_boundary_point(end_point, polygon_x, polygon_y)
        
        if start_boundary == end_boundary:
            return [start_point, end_point]
        
        # 沿边界生成路径
        boundary_path = self._trace_boundary_path(start_boundary, end_boundary, polygon_x, polygon_y)
        
        # 构建完整路径
        full_path = [start_point] + boundary_path + [end_point]
        return full_path
    
    def _find_nearest_boundary_point(self, point: Tuple[float, float], 
                                   polygon_x: List[float], polygon_y: List[float]) -> int:
        """找到距离指定点最近的边界顶点索引"""
        px, py = point
        min_dist = float('inf')
        nearest_idx = 0
        
        for i, (bx, by) in enumerate(zip(polygon_x, polygon_y)):
            dist = math.sqrt((px - bx) ** 2 + (py - by) ** 2)
            if dist < min_dist:
                min_dist = dist
                nearest_idx = i
        
        return nearest_idx
    
    def _trace_boundary_path(self, start_idx: int, end_idx: int,
                           polygon_x: List[float], polygon_y: List[float]) -> List[Tuple[float, float]]:
        """沿边界追踪路径"""
        if start_idx == end_idx:
            return []
        
        n = len(polygon_x)
        path = []
        
        # 选择较短的路径方向
        forward_dist = (end_idx - start_idx) % n
        backward_dist = (start_idx - end_idx) % n
        
        if forward_dist <= backward_dist:
            # 正向追踪
            current = start_idx
            while current != end_idx:
                current = (current + 1) % n
                path.append((polygon_x[current], polygon_y[current]))
        else:
            # 反向追踪
            current = start_idx
            while current != end_idx:
                current = (current - 1) % n
                path.append((polygon_x[current], polygon_y[current]))
        
        return path
    
    def detect_concave_regions(self, polygon_x: List[float], polygon_y: List[float], 
                             line_spacing: float) -> List[Dict]:
        """
        检测凹陷区域并评估其对航线的影响
        
        参数:
            polygon_x, polygon_y: 多边形顶点坐标
            line_spacing: 航线间距
            
        返回:
            凹陷区域信息列表 [{"start_idx": int, "end_idx": int, "affected_lines": int}, ...]
        """
        concave_regions = []
        n = len(polygon_x)
        
        # 计算每个顶点的转向角
        for i in range(n):
            prev_i = (i - 1) % n
            next_i = (i + 1) % n
            
            # 计算向量
            v1_x = polygon_x[i] - polygon_x[prev_i]
            v1_y = polygon_y[i] - polygon_y[prev_i]
            v2_x = polygon_x[next_i] - polygon_x[i]
            v2_y = polygon_y[next_i] - polygon_y[i]
            
            # 计算叉积判断转向
            cross_product = v1_x * v2_y - v1_y * v2_x
            
            if cross_product > 0:  # 右转，凹陷点
                # 估算凹陷影响的航线数
                min_y = min(polygon_y[prev_i], polygon_y[i], polygon_y[next_i])
                max_y = max(polygon_y[prev_i], polygon_y[i], polygon_y[next_i])
                affected_lines = int((max_y - min_y) / line_spacing) + 1
                
                concave_regions.append({
                    "vertex_idx": i,
                    "affected_lines": affected_lines,
                    "severity": affected_lines
                })
        
        return concave_regions
    
    def should_split_region(self, concave_regions: List[Dict]) -> bool:
        """
        判断是否需要分割区域
        
        参数:
            concave_regions: 凹陷区域信息
            
        返回:
            True表示需要分割，False表示可以简单绕行
        """
        # 暂时禁用区域分割，统一使用边界裁剪策略
        return False
        
        # 如果有凹陷影响超过2条航线，则需要分割
        # for region in concave_regions:
        #     if region["affected_lines"] > 2:
        #         return True
        # return False
    
    def simple_polygon_decomposition(self, polygon_x: List[float], polygon_y: List[float]) -> List[List[Tuple[float, float]]]:
        """
        简单多边形分解：将复杂多边形分解为多个简单区域
        
        参数:
            polygon_x, polygon_y: 多边形顶点坐标
            
        返回:
            分解后的简单多边形列表
        """
        # 简化版本：对于复杂多边形，尝试按凸包分解
        # 这里实现一个基础版本，可以后续优化
        
        # 计算凸包
        points = list(zip(polygon_x, polygon_y))
        convex_hull = self._compute_convex_hull(points)
        
        # 如果原多边形接近凸包，不需要分解
        if len(convex_hull) >= len(points) * 0.8:
            return [points]
        
        # 否则返回凸包作为主区域（简化处理）
        return [convex_hull]
    
    def _compute_convex_hull(self, points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        计算凸包（使用Graham扫描法的简化版）
        """
        def cross_product(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
        
        points = sorted(set(points))
        if len(points) <= 1:
            return points
        
        # 构建下凸包
        lower = []
        for p in points:
            while len(lower) >= 2 and cross_product(lower[-2], lower[-1], p) <= 0:
                lower.pop()
            lower.append(p)
        
        # 构建上凸包
        upper = []
        for p in reversed(points):
            while len(upper) >= 2 and cross_product(upper[-2], upper[-1], p) <= 0:
                upper.pop()
            upper.append(p)
        
        return lower[:-1] + upper[:-1]
    
    def _plan_with_region_splitting(self, local_x: List[float], local_y: List[float],
                                  line_spacing: float, rotation_angle: float,
                                  min_lat: float, min_lon: float, meters_per_degree_lon: float,
                                  logger: Optional[logging.Logger] = None) -> List[Tuple[float, float]]:
        """
        使用区域分割策略进行航线规划
        """
        if logger:
            logger.info("执行区域分割航线规划")
        
        # 分解为简单区域
        simple_regions = self.simple_polygon_decomposition(local_x, local_y)
        
        all_turn_points = []
        
        for i, region in enumerate(simple_regions):
            if logger:
                logger.info(f"规划第{i+1}个区域，包含{len(region)}个顶点")
            
            # 提取区域坐标
            region_x = [p[0] for p in region]
            region_y = [p[1] for p in region]
            
            # 对每个简单区域独立规划
            region_points = self._plan_simple_region(
                region_x, region_y, line_spacing, rotation_angle,
                min_lat, min_lon, meters_per_degree_lon, logger
            )
            
            all_turn_points.extend(region_points)
        
        if logger:
            logger.info(f"所有区域规划完成，总计 {len(all_turn_points)} 个拐点")
        
        return all_turn_points
    
    def _plan_with_simple_bypass(self, local_x: List[float], local_y: List[float],
                               line_spacing: float, rotation_angle: float,
                               min_lat: float, min_lon: float, meters_per_degree_lon: float,
                               logger: Optional[logging.Logger] = None) -> List[Tuple[float, float]]:
        """
        使用简单绕行策略进行航线规划
        """
        if logger:
            logger.info("执行简单绕行航线规划")
        
        return self._plan_with_boundary_clipping(
            local_x, local_y, line_spacing, rotation_angle,
            min_lat, min_lon, meters_per_degree_lon, logger
        )
    
    def _plan_with_boundary_clipping(self, local_x: List[float], local_y: List[float],
                                   line_spacing: float, rotation_angle: float,
                                   min_lat: float, min_lon: float, meters_per_degree_lon: float,
                                   logger: Optional[logging.Logger] = None) -> List[Tuple[float, float]]:
        """
        改进的边界裁剪航线规划：保持平行线主体+局部边界适应
        """
        if logger:
            logger.info("执行改进的边界裁剪航线规划")
        
        # 应用旋转
        center_x, center_y = sum(local_x) / len(local_x), sum(local_y) / len(local_y)
        if rotation_angle != 0:
            angle_rad = math.radians(rotation_angle)
            cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
            
            rotated_x, rotated_y = [], []
            for x, y in zip(local_x, local_y):
                dx, dy = x - center_x, y - center_y
                new_x = center_x + dx * cos_a - dy * sin_a
                new_y = center_y + dx * sin_a + dy * cos_a
                rotated_x.append(new_x)
                rotated_y.append(new_y)
            local_x, local_y = rotated_x, rotated_y
        
        # 生成扫描线
        min_y, max_y = min(local_y), max(local_y)
        scan_lines = []
        current_y = min_y + line_spacing / 2
        while current_y < max_y:
            scan_lines.append(current_y)
            current_y += line_spacing
        
        turn_points = []
        
        for i, scan_y in enumerate(scan_lines):
            # 计算扫描线与边界的交点
            intersections = []
            for j in range(len(local_x)):
                x1, y1 = local_x[j], local_y[j]
                x2, y2 = local_x[(j + 1) % len(local_x)], local_y[(j + 1) % len(local_x)]
                
                if (y1 <= scan_y <= y2) or (y2 <= scan_y <= y1):
                    if abs(y2 - y1) > 1e-10:
                        t = (scan_y - y1) / (y2 - y1)
                        intersect_x = x1 + t * (x2 - x1)
                        intersections.append(intersect_x)
            
            intersections.sort()
            
            if len(intersections) >= 2:
                # 提取有效的航线段（处理凹多边形的多个分段）
                valid_segments = []
                for k in range(0, len(intersections), 2):
                    if k + 1 < len(intersections):
                        seg_start = intersections[k]
                        seg_end = intersections[k + 1]
                        
                        # 检查线段中点是否在多边形内
                        mid_x = (seg_start + seg_end) / 2
                        if self.point_in_polygon(mid_x, scan_y, local_x, local_y):
                            valid_segments.append((seg_start, seg_end))
                
                if valid_segments:
                    # 选择最长的有效段作为主航线
                    main_segment = max(valid_segments, key=lambda s: s[1] - s[0])
                    start_x, end_x = main_segment
                    
                    # 蛇形路径
                    if i % 2 == 1:
                        start_x, end_x = end_x, start_x
                    
                    # 转换回经纬度
                    start_lat, start_lon = self._convert_to_latlon(
                        start_x, scan_y, rotation_angle, center_x, center_y,
                        min_lat, min_lon, meters_per_degree_lon
                    )
                    end_lat, end_lon = self._convert_to_latlon(
                        end_x, scan_y, rotation_angle, center_x, center_y,
                        min_lat, min_lon, meters_per_degree_lon
                    )
                    
                    turn_points.extend([(start_lat, start_lon), (end_lat, end_lon)])
        
        if logger:
            logger.info(f"生成 {len(turn_points)} 个拐点")
        
        return turn_points
    
    def _convert_to_latlon(self, x: float, y: float, rotation_angle: float,
                         center_x: float, center_y: float, min_lat: float, min_lon: float,
                         meters_per_degree_lon: float) -> Tuple[float, float]:
        """坐标转换辅助方法"""
        if rotation_angle != 0:
            angle_rad = math.radians(-rotation_angle)
            cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
            dx, dy = x - center_x, y - center_y
            x = center_x + dx * cos_a - dy * sin_a
            y = center_y + dx * sin_a + dy * cos_a
        
        lat = min_lat + y / self.METERS_PER_DEGREE_LAT
        lon = min_lon + x / meters_per_degree_lon
        return lat, lon
    
    def _plan_simple_region(self, local_x: List[float], local_y: List[float],
                          line_spacing: float, rotation_angle: float,
                          min_lat: float, min_lon: float, meters_per_degree_lon: float,
                          logger: Optional[logging.Logger] = None) -> List[Tuple[float, float]]:
        """
        对单个简单区域进行航线规划（使用原有的简单算法）
        """
        # 应用旋转
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
        
        # 生成扫描线
        min_y, max_y = min(local_y), max(local_y)
        scan_lines = []
        current_y = min_y + line_spacing / 2
        
        while current_y < max_y:
            scan_lines.append(current_y)
            current_y += line_spacing
        
        # 计算航线拐点
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
            
            # 排序交点并生成航线段
            intersections.sort()
            
            if len(intersections) >= 2:
                # 简单策略：只取首尾交点
                start_x, end_x = intersections[0], intersections[-1]
                
                # 蛇形路径：奇数行从左到右，偶数行从右到左
                if i % 2 == 1:
                    start_x, end_x = end_x, start_x
                
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
        
        return turn_points
    
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
        
        # 2.5. 智能分区分析
        concave_regions = self.detect_concave_regions(local_x, local_y, line_spacing)
        need_split = self.should_split_region(concave_regions)
        
        if logger:
            logger.info(f"检测到 {len(concave_regions)} 个凹陷区域")
            if need_split:
                logger.info("需要进行区域分割")
            else:
                logger.info("使用简单绕行策略")
        
        # 根据分析结果选择处理策略
        if need_split:
            return self._plan_with_region_splitting(
                local_x, local_y, line_spacing, rotation_angle, 
                min_lat, min_lon, meters_per_degree_lon, logger
            )
        else:
            return self._plan_with_simple_bypass(
                local_x, local_y, line_spacing, rotation_angle,
                min_lat, min_lon, meters_per_degree_lon, logger
            )
    
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
    
    # 验证KML文件存在或URL有效
    import os
    kml_file = config['kml_file']
    
    # 检查是否为URL
    if kml_file.startswith(('http://', 'https://')):
        if logger:
            logger.info("KML文件为URL，跳过本地文件检查")
    else:
        # 本地文件检查
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