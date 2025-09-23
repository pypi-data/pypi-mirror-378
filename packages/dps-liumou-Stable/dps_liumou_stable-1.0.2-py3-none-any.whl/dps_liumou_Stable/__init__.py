#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Docker镜像拉取智能工具
自动检测可用镜像加速轮询拉取镜像
"""

import subprocess
import requests
import sys
import time
import argparse
from typing import List, Dict


class DockerPullSmart:
    """Docker镜像拉取智能工具"""
    
    def __init__(self, debug: bool = False):
        """初始化Docker拉取智能工具"""
        self.mirror_sources = []  # 不再加载本地配置文件，完全依赖接口数据
        self.debug = debug  # 调试模式  
    def fetch_online_mirrors(self) -> List[Dict]:
        """从API获取在线镜像源"""
        url = "https://status.anye.xyz/status.json"
        
        try:
            print("🌐 正在获取镜像源信息...")
            
            headers = {
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                'cache-control': 'no-cache',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'referer': 'https://status.anye.xyz/',
                'sec-ch-ua': '"Microsoft Edge";v="137", "Chromium";v="137", "Not=A?Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            all_mirrors = response.json()
            online_mirrors = [mirror for mirror in all_mirrors if mirror.get('status') == 'online']
            
            print(f"✅ 成功获取 {len(online_mirrors)} 个在线镜像源")
            return online_mirrors
            
        except Exception as e:
            print(f"⚠️  获取镜像源失败: {e}")
            print("💡 建议检查网络连接或稍后重试")
            return []
    
    def get_available_mirrors(self) -> List[Dict]:
        """获取可用的镜像源列表"""
        online_mirrors = self.fetch_online_mirrors()
        if not online_mirrors:
            print("⚠️  没有可用的镜像源，请检查网络连接或稍后重试")
            return []
        
        # 按最后检查时间排序，最新的优先
        online_mirrors.sort(key=lambda x: x.get('lastCheck', ''), reverse=True)
        return online_mirrors
    
    def run_docker_command(self, command: List[str], timeout: int = None) -> bool:
        """运行Docker命令"""
        if timeout is None:
            timeout = 300  # 默认超时时间
        
        # 调试模式下输出完整命令
        if self.debug:
            print(f"🔍 执行命令: {' '.join(command)}")
        
        try:
            # 使用实时输出模式运行命令
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                bufsize=1,  # 行缓冲
                universal_newlines=True
            )
            
            # 实时输出命令执行结果
            output_lines = []
            start_time = time.time()
            
            for line in iter(process.stdout.readline, ''):
                if line:
                    line = line.strip()
                    output_lines.append(line)
                    # 实时输出进度信息
                    if 'Downloading' in line or 'Extracting' in line or 'Pulling' in line:
                        print(f"📥 {line}")
                    elif self.debug:  # 调试模式下输出所有信息
                        print(f"📋 {line}")
            
            # 等待进程完成
            process.wait()
            end_time = time.time()
            
            if process.returncode == 0:
                if self.debug:
                    print(f"✅ 命令执行成功: {' '.join(command)} (耗时: {end_time - start_time:.1f}秒)")
                return True
            else:
                if self.debug:
                    print(f"❌ 命令执行失败: {' '.join(command)}")
                # 输出错误信息
                for line in output_lines[-5:]:  # 显示最后5行错误信息
                    if line and ('error' in line.lower() or 'failed' in line.lower()):
                        print(f"❌ {line}")
                return False
                
        except subprocess.TimeoutExpired:
            process.kill()
            print(f"⏰ 命令超时: {' '.join(command)}")
            return False
        except Exception as e:
            print(f"❌ 运行命令失败: {e}")
            return False
    
    def pull_image_with_mirror(self, image_name: str, mirror_url: str) -> bool:
        """使用镜像源拉取镜像"""
        # 移除协议前缀，构建镜像源地址
        clean_mirror_url = mirror_url.replace('https://', '').replace('http://', '')
        mirror_image = f"{clean_mirror_url}/{image_name}"
        print(f"🔄 尝试从镜像源拉取: {mirror_image}")
        
        # 拉取镜像
        pull_command = ["docker", "pull", mirror_image]
        if self.run_docker_command(pull_command):
            print(f"✅ 成功拉取镜像: {mirror_image}")
            return True
        else:
            print(f"❌ 从镜像源拉取失败: {mirror_image}")
            return False
    
    def tag_image(self, source_image: str, target_image: str) -> bool:
        """为镜像打标签"""
        print(f"🏷️  设置镜像标签: {source_image} -> {target_image}")
        tag_command = ["docker", "tag", source_image, target_image]
        return self.run_docker_command(tag_command)
    
    def remove_image(self, image_name: str) -> bool:
        """删除镜像"""
        print(f"🗑️  删除镜像: {image_name}")
        remove_command = ["docker", "rmi", image_name]
        return self.run_docker_command(remove_command)
    
    def is_docker_hub_image(self, image_name: str) -> bool:
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
    
    def pull_image_directly(self, image_name: str) -> bool:
        """直接使用默认docker pull命令拉取镜像"""
        print(f"🔄 将使用默认命令尝试拉取...")
        command = ['docker', 'pull', image_name]
        
        # 调试模式下输出完整命令
        if self.debug:
            print(f"🔍 执行默认拉取命令: {' '.join(command)}")
        
        success = self.run_docker_command(command)
        
        if success:
            print(f"✅ 镜像拉取成功: {image_name}")
        else:
            print(f"❌ 镜像拉取失败: {image_name}")
        
        return success
    
    def smart_pull(self, image_name: str, max_retries: int = 3, timeout: int = 300, force_mirror: bool = False) -> bool:
        """智能拉取镜像
        
        Args:
            image_name: 镜像名称
            max_retries: 最大重试次数
            timeout: 超时时间
            force_mirror: 是否强制使用镜像站（即使非Docker Hub镜像）
        """
        print(f"🎯 开始智能拉取镜像: {image_name}")
        print("=" * 50)
        
        # 记录开始时间
        start_time = time.time()
        
        # 判断是否为Docker Hub镜像
        is_docker_hub = self.is_docker_hub_image(image_name)
        
        if not is_docker_hub:
            print(f"📦 检测到非Docker Hub镜像: {image_name}")
            if not force_mirror:
                print("🔄 非Docker Hub镜像默认不使用镜像站加速")
                success = self.pull_image_directly(image_name)
                # 输出总耗时
                total_time = time.time() - start_time
                print(f"⏱️  总耗时: {total_time:.1f}秒")
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
            print(f"⏱️  总耗时: {total_time:.1f}秒")
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
                # 拉取成功，设置标签（使用清理后的URL）
                clean_mirror_url = mirror_url.replace('https://', '').replace('http://', '')
                mirror_image = f"{clean_mirror_url}/{image_name}"
                if self.tag_image(mirror_image, image_name):
                    print(f"✅ 成功设置镜像标签: {image_name}")
                    
                    # 删除带镜像前缀的镜像
                    self.remove_image(mirror_image)
                    
                    print("=" * 50)
                    print(f"🎉 镜像拉取成功: {image_name}")
                    print(f"📍 使用的镜像源: {mirror_name}")
                    # 输出总耗时
                    total_time = time.time() - start_time
                    print(f"⏱️  总耗时: {total_time:.1f}秒")
                    return True
                else:
                    print(f"⚠️  设置标签失败，继续尝试其他镜像源")
            
            print(f"❌ 镜像源 {mirror_name} 失败，尝试下一个...")
            print("-" * 30)
            time.sleep(1)  # 短暂延迟避免过快请求
        
        print("❌ 所有镜像源都失败了")
        print("🔄 将使用默认命令尝试拉取...")
        success = self.pull_image_directly(image_name)
        
        # 输出总耗时
        total_time = time.time() - start_time
        print(f"⏱️  总耗时: {total_time:.1f}秒")
        
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