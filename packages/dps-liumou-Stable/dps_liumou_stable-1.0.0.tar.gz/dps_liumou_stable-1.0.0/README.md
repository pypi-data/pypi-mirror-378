# DockerPull 智能镜像拉取工具

## 🚀 介绍

DockerPull 是一个智能的 Docker 镜像拉取工具，能够自动检测并使用最优的镜像加速源，解决 Docker 镜像拉取慢或失败的问题。

### ✨ 主要特性

- **智能镜像源选择**: 自动检测 20+ 个可用镜像加速源，选择最优源进行拉取
- **实时进度显示**: 显示镜像拉取的实时进度（Downloading/Extracting/Pulling）
- **调试模式**: 支持 `-d` 参数输出实际执行的完整命令，便于调试
- **耗时统计**: 自动统计并显示整个拉取过程的总耗时
- **容错机制**: 支持重试机制，单个镜像源失败自动切换到下一个
- **命令行友好**: 使用 argparse 标准库，支持完整的命令行参数和帮助

## 📦 安装

### 系统要求

- Python 3.6+
- Docker 已安装

### 快速安装

```bash
# 克隆仓库
git clone https://gitee.com/your-repo/docker-pull.git
cd docker-pull

# 安装依赖（如果有的话）
pip install -r requirements.txt
```

## 🎯 使用方法

### 基本用法

```bash
# 拉取镜像（自动选择最优镜像源）
python docker_pull_smart.py nginx:latest

# 拉取指定版本
python docker_pull_smart.py python:3.9

# 列出所有可用镜像源
python docker_pull_smart.py --list-mirrors

# 列出本地镜像
python docker_pull_smart.py --local-images
```

### 高级用法

```bash
# 调试模式 - 显示实际执行的完整命令
python docker_pull_smart.py nginx:latest -d

# 设置超时时间（秒）
python docker_pull_smart.py nginx:latest --timeout 600

# 设置最大重试次数
python docker_pull_smart.py nginx:latest --max-retries 5

# 组合使用
python docker_pull_smart.py nginx:latest -d --timeout 600 --max-retries 5
```

### 命令行参数

```
positional arguments:
  image_name            要拉取的镜像名称，如 nginx:latest

options:
  -h, --help            显示帮助信息
  --list-mirrors        列出所有可用的镜像源
  --local-images        列出本地Docker镜像
  --timeout TIMEOUT     Docker命令超时时间（秒），默认300秒
  --max-retries MAX_RETRIES
                        每个镜像源的最大重试次数，默认3次
  -d, --debug           调试模式，输出实际执行的完整命令
```

## 🎨 输出示例

### 正常拉取模式

```
🎯 开始智能拉取镜像: nginx:latest
==================================================
📋 找到 22 个可用镜像源
  1. 阿里云镜像仓库 - https://registry.cn-hangzhou.aliyuncs.com
  2. 网易云镜像仓库 - https://hub-mirror.c.163.com
  ...

🔄 尝试镜像源 1/22: 阿里云镜像仓库
🔗 URL: https://registry.cn-hangzhou.aliyuncs.com
📥 Downloading  6e7cb3f1d8a5:  45.67MB/123.45MB
📥 Extracting  6e7cb3f1d8a5:  100%
✅ 成功拉取镜像: nginx:latest
==================================================
🎉 镜像拉取成功: nginx:latest
📍 使用的镜像源: 阿里云镜像仓库
⏱️  总耗时: 15.3秒
```

### 调试模式

```
🎯 开始智能拉取镜像: nginx:latest
==================================================
🔍 执行命令: docker pull https://registry.cn-hangzhou.aliyuncs.com/nginx:latest
📥 Downloading  6e7cb3f1d8a5:  45.67MB/123.45MB
📋 latest: Pulling from library/nginx
📋 Digest: sha256:1234567890abcdef...
✅ 命令执行成功: docker pull https://registry.cn-hangzhou.aliyuncs.com/nginx:latest (耗时: 12.5秒)
✅ 成功拉取镜像: https://registry.cn-hangzhou.aliyuncs.com/nginx:latest
🏷️  设置镜像标签: https://registry.cn-hangzhou.aliyuncs.com/nginx:latest -> nginx:latest
✅ 成功设置镜像标签: nginx:latest
🗑️  删除镜像: https://registry.cn-hangzhou.aliyuncs.com/nginx:latest
==================================================
🎉 镜像拉取成功: nginx:latest
📍 使用的镜像源: 阿里云镜像仓库
⏱️  总耗时: 15.3秒
```

## 🔧 技术特性

- **智能镜像源管理**: 实时检测镜像源可用性，自动过滤失效源
- **实时输出**: 使用 subprocess.Popen 实现实时进度显示
- **错误处理**: 完善的异常处理和重试机制
- **跨平台**: 支持 Windows、Linux、macOS
- **标准库**: 使用 argparse 标准库，无需额外依赖

## 🤝 参与贡献

1. Fork 本仓库
2. 新建 Feat_xxx 分支
3. 提交代码
4. 新建 Pull Request

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

#### 相关链接

- [Gitee 官方博客](https://blog.gitee.com)
- [Gitee 优秀开源项目](https://gitee.com/explore)
- [GVP 最有价值开源项目](https://gitee.com/gvp)
- [Gitee 使用手册](https://gitee.com/help)
