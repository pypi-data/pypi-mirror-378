# dps_liumou_Stable

智能Docker镜像拉取工具 - 自动选择最优镜像源

## 安装

```bash
pip install dps_liumou_Stable
```

## 使用

安装后，可以通过 `dps` 命令使用：

```bash
# 拉取镜像
dps nginx:latest

# 列出可用镜像源
dps --list-mirrors

# 调试模式
dps nginx:latest -d

# 设置超时时间
dps nginx:latest --timeout 600
```

## 功能特性

- 🚀 智能镜像源选择：自动检测 20+ 个可用镜像加速源
- 📊 实时进度显示：显示镜像拉取的实时进度
- 🔍 调试模式：支持 `-d` 参数输出实际执行的完整命令
- ⏱️ 耗时统计：自动统计并显示整个拉取过程的总耗时
- 🔄 容错机制：支持重试机制，单个镜像源失败自动切换到下一个
- 📋 命令行友好：使用 argparse 标准库，支持完整的命令行参数和帮助

## 项目结构

```
dps_liumou_Stable/
├── src/
│   ├── dps_liumou_Stable/     # 主包
│   │   ├── __init__.py         # 主程序代码
│   │   └── __main__.py         # 包入口点
│   └── dps/                    # dps命令入口
│       ├── __init__.py
│       └── __main__.py
├── setup.py                    # 包配置（兼容旧版）
├── pyproject.toml             # 现代包配置
├── requirements.txt           # 依赖
├── README.md                  # 项目说明
├── LICENSE                    # 许可证
└── MANIFEST.in               # 包文件清单
```

## 开发

```bash
# 克隆项目
git clone https://gitee.com/liumou/dps_liumou_Stable.git
cd dps_liumou_Stable

# 开发模式安装
pip install -e .

# 构建包
python build.py

# 发布到PyPI（需要配置twine）
python -m twine upload dist/*
```

## 许可证

MIT License