#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
镜像工具模块
提供镜像相关的工具函数
"""

import time
from typing import List, Dict


class ImageUtils:
    """镜像工具类"""
    
    @staticmethod
    def is_docker_hub_image(image_name: str) -> bool:
        """判断是否为Docker Hub镜像
        
        Docker Hub镜像特点：
        - 不包含'/'或只包含一个'/'（命名空间/镜像名）
        - 非Docker Hub镜像通常包含两个或更多'/'（如registry.example.com/namespace/image）
        """
        # 计算斜杠数量
        slash_count = image_name.count('/')
        
        # Docker Hub镜像：没有斜杠（如nginx:latest）或只有一个斜杠（如library/nginx:latest）
        # 非Docker Hub镜像：两个或更多斜杠（如gcr.io/google/cadvisor:latest）
        return slash_count <= 1
    
    @staticmethod
    def clean_mirror_url(mirror_url: str) -> str:
        """清理镜像源URL，移除协议前缀"""
        return mirror_url.replace('https://', '').replace('http://', '')
    
    @staticmethod
    def format_mirror_image(image_name: str, mirror_url: str) -> str:
        """格式化镜像地址，构建带镜像源的完整地址
        
        对于没有命名空间的官方库镜像（如nginx:latest），自动添加library/前缀
        """
        clean_url = ImageUtils.clean_mirror_url(mirror_url)
        
        # 检查是否为官方库镜像（没有'/'或只有'library/'前缀）
        if '/' not in image_name or image_name.startswith('library/'):
            # 如果已经是library格式，直接使用；否则添加library前缀
            if image_name.startswith('library/'):
                formatted_image = image_name
            else:
                formatted_image = f"library/{image_name}"
            return f"{clean_url}/{formatted_image}"
        else:
            # 非官方库镜像，直接使用原名称
            return f"{clean_url}/{image_name}"
    
    @staticmethod
    def format_time_duration(seconds: float) -> str:
        """格式化时间持续时间为易读的字符串"""
        if seconds < 60:
            return f"{seconds:.1f}秒"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}分钟"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}小时"
    
    @staticmethod
    def print_mirror_list(mirrors: List[Dict]):
        """打印镜像源列表"""
        print("🌐 可用镜像源列表:")
        for i, mirror in enumerate(mirrors, 1):
            status = "🟢" if mirror.get('status') == 'online' else "🔴"
            print(f"{status} {i}. {mirror['name']}")
            print(f"   URL: {mirror['url']}")
            print(f"   最后检查: {mirror.get('lastCheck', '未知')}")
            if mirror.get('tags'):
                tags = ', '.join([tag['name'] for tag in mirror['tags']])
                print(f"   标签: {tags}")
            print()
    
    @staticmethod
    def print_progress_header(image_name: str):
        """打印进度条头部信息"""
        print(f"🎯 开始智能拉取镜像: {image_name}")
        print("=" * 50)
    
    @staticmethod
    def print_progress_footer(image_name: str, mirror_name: str, total_time: float, success: bool = True):
        """打印进度条底部信息"""
        print("=" * 50)
        if success:
            print(f"🎉 镜像拉取成功: {image_name}")
            print(f"📍 使用的镜像源: {mirror_name}")
        else:
            print(f"❌ 镜像拉取失败: {image_name}")
        print(f"⏱️  总耗时: {ImageUtils.format_time_duration(total_time)}")
    
    @staticmethod
    def sleep_with_message(seconds: float, message: str = "等待中..."):
        """带消息的延迟
        
        Args:
            seconds: 延迟秒数
            message: 显示的消息
        """
        print(f"⏳ {message} ({seconds}秒)")
        time.sleep(seconds)