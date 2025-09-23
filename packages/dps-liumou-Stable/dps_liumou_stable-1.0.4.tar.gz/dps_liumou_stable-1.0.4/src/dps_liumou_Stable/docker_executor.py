#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Docker命令执行器模块
负责执行Docker相关命令并处理输出
"""

import subprocess
import time
from typing import List


class DockerCommandExecutor:
    """Docker命令执行器"""
    
    def __init__(self, debug: bool = False):
        """初始化Docker命令执行器"""
        self.debug = debug
    
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
    
    def list_local_images(self):
        """列出本地镜像"""
        print("📦 本地镜像列表:")
        command = ["docker", "images", "--format", "table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}"]
        self.run_docker_command(command)