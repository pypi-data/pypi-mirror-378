#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Docker镜像拉取智能工具
自动检测可用镜像加速轮询拉取镜像
"""

import sys
import time
import argparse
from typing import List, Dict

from .mirror_client import MirrorClient
from .docker_executor import DockerCommandExecutor
from .image_utils import ImageUtils
    
class DockerPullSmart:
    """Docker镜像拉取智能工具"""
    
    def __init__(self, debug: bool = False):
        """初始化Docker拉取智能工具"""
        self.debug = debug  # 调试模式
        self.mirror_client = MirrorClient()
        self.docker_executor = DockerCommandExecutor(debug=debug)
        self.image_utils = ImageUtils()
    
    def get_available_mirrors(self) -> List[Dict]:
        """获取可用的镜像源列表"""
        return self.mirror_client.get_available_mirrors()
    
    def pull_image_with_mirror(self, image_name: str, mirror_url: str) -> bool:
        """使用镜像源拉取镜像"""
        # 清理镜像源URL，移除协议前缀
        clean_mirror_url = self.image_utils.clean_mirror_url(mirror_url)
        mirror_image = self.image_utils.format_mirror_image(image_name, mirror_url)
        print(f"🔄 尝试从镜像源拉取: {mirror_image}")
        
        # 拉取镜像
        pull_command = ["docker", "pull", mirror_image]
        if self.docker_executor.run_docker_command(pull_command):
            print(f"✅ 成功拉取镜像: {mirror_image}")
            return True
        else:
            print(f"❌ 从镜像源拉取失败: {mirror_image}")
            return False
    
    def pull_image_directly(self, image_name: str) -> bool:
        """直接使用默认docker pull命令拉取镜像"""
        return self.docker_executor.pull_image_directly(image_name)
    
    def tag_image(self, source_image: str, target_image: str) -> bool:
        """为镜像打标签"""
        return self.docker_executor.tag_image(source_image, target_image)
    
    def remove_image(self, image_name: str) -> bool:
        """删除镜像"""
        return self.docker_executor.remove_image(image_name)
    
    def list_local_images(self):
        """列出本地镜像"""
        self.docker_executor.list_local_images()
    
    def smart_pull(self, image_name: str, max_retries: int = 3, timeout: int = 300, force_mirror: bool = False) -> bool:
        """智能拉取镜像
        
        Args:
            image_name: 镜像名称
            max_retries: 最大重试次数
            timeout: 超时时间
            force_mirror: 是否强制使用镜像站（即使非Docker Hub镜像）
        """
        # 打印进度头部信息
        self.image_utils.print_progress_header(image_name)
        
        # 记录开始时间
        start_time = time.time()
        
        # 判断是否为Docker Hub镜像
        is_docker_hub = self.image_utils.is_docker_hub_image(image_name)
        
        if not is_docker_hub:
            print(f"📦 检测到非Docker Hub镜像: {image_name}")
            if not force_mirror:
                print("🔄 非Docker Hub镜像默认不使用镜像站加速")
                success = self.pull_image_directly(image_name)
                # 输出总耗时
                total_time = time.time() - start_time
                self.image_utils.print_progress_footer(image_name, "默认拉取", total_time, success)
                return success
            else:
                print("⚡ 强制使用镜像站模式")
        
        # 获取可用镜像源
        available_mirrors = self.get_available_mirrors()
        if not available_mirrors:
            print("⚠️  没有可用的镜像加速源")
            print("🔄 将使用默认命令直接拉取镜像...")
            success = self.pull_image_directly(image_name)
            # 输出总耗时
            total_time = time.time() - start_time
            self.image_utils.print_progress_footer(image_name, "默认拉取", total_time, success)
            return success
        
        print(f"📋 找到 {len(available_mirrors)} 个可用镜像源")
        for i, mirror in enumerate(available_mirrors, 1):
            print(f"  {i}. {mirror['name']} - {mirror['url']}")
        print()
        
        # 尝试每个镜像源
        for i, mirror in enumerate(available_mirrors):
            mirror_name = mirror['name']
            mirror_url = mirror['url'].rstrip('/')
            
            print(f"🔄 尝试镜像源 {i+1}/{len(available_mirrors)}: {mirror_name}")
            print(f"🔗 URL: {mirror_url}")
            
            # 尝试拉取镜像
            if self.pull_image_with_mirror(image_name, mirror_url):
                # 拉取成功，设置标签
                clean_mirror_url = self.image_utils.clean_mirror_url(mirror_url)
                mirror_image = self.image_utils.format_mirror_image(image_name, mirror_url)
                if self.tag_image(mirror_image, image_name):
                    print(f"✅ 成功设置镜像标签: {image_name}")
                    
                    # 删除带镜像前缀的镜像
                    self.remove_image(mirror_image)
                    
                    # 输出成功信息
                    total_time = time.time() - start_time
                    self.image_utils.print_progress_footer(image_name, mirror_name, total_time, True)
                    return True
                else:
                    print(f"⚠️  设置标签失败，继续尝试其他镜像源")
            
            print(f"❌ 镜像源 {mirror_name} 失败，尝试下一个...")
            print("-" * 30)
            self.image_utils.sleep_with_message(1, "短暂延迟避免过快请求")
        
        print("❌ 所有镜像源都失败了")
        print("🔄 将使用默认命令尝试拉取...")
        success = self.pull_image_directly(image_name)
        
        # 输出总耗时
        total_time = time.time() - start_time
        self.image_utils.print_progress_footer(image_name, "默认拉取", total_time, success)
        
        return success
    
    def list_local_images(self):
        """列出本地镜像"""
        print("📦 本地镜像列表:")
        command = ["docker", "images", "--format", "table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}"]
        self.run_docker_command(command)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Docker镜像智能拉取工具 - 自动选择最优镜像源",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s nginx:latest                    # 拉取nginx镜像
  %(prog)s python:3.9                     # 拉取python镜像
  %(prog)s --list-mirrors                   # 列出可用镜像源
  %(prog)s --local-images                   # 列出本地镜像
  %(prog)s -h                              # 显示帮助信息

项目地址: https://gitee.com/liumou_site/docker-pull
        """
    )
    
    # 创建互斥组，确保镜像名称和其他选项不会同时使用
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        'image_name', 
        nargs='?', 
        help='要拉取的镜像名称，如 nginx:latest'
    )
    group.add_argument(
        '--list-mirrors', 
        action='store_true',
        help='列出所有可用的镜像源'
    )
    group.add_argument(
        '--local-images', 
        action='store_true',
        help='列出本地Docker镜像'
    )
    
    # 可选参数
    parser.add_argument(
        '--timeout', 
        type=int, 
        default=300,
        help='Docker命令超时时间（秒），默认300秒'
    )
    parser.add_argument(
        '--max-retries', 
        type=int, 
        default=3,
        help='每个镜像源的最大重试次数，默认3次'
    )
    parser.add_argument(
        '-d', '--debug', 
        action='store_true',
        help='调试模式，输出实际执行的完整命令'
    )
    parser.add_argument(
        '--force-mirror', 
        action='store_true',
        help='强制使用镜像站（即使非Docker Hub镜像）'
    )
    
    args = parser.parse_args()
    
    tool = DockerPullSmart(debug=args.debug)
    
    if args.list_mirrors:
        mirrors = tool.get_available_mirrors()
        tool.image_utils.print_mirror_list(mirrors)
    
    elif args.local_images:
        tool.list_local_images()
    
    elif args.image_name:
        success = tool.smart_pull(args.image_name, max_retries=args.max_retries, timeout=args.timeout, force_mirror=args.force_mirror)
        sys.exit(0 if success else 1)
    
    else:
        parser.print_help()
        sys.exit(1)


# 导出main函数，使其可以通过命令行调用
__all__ = ['main']

if __name__ == "__main__":
    main()