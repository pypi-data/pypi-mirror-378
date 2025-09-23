#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NagaAgent Core Package Setup
核心依赖包，包含核心功能和API服务器相关依赖
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nagaagent-core",
    version="1.0.2",
    author="NagaAgent Team",
    author_email="nagaagent@example.com",
    description="NagaAgent核心依赖包，包含核心功能和API服务器相关依赖",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nagaagent/nagaagent-core",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        # 核心依赖
        "mcp>=1.6.0",
        "openai>=1.76.0", 
        "python-dotenv>=1.1.0",
        "requests>=2.32.3",
        "aiohttp>=3.11.18",
        
        # API服务器相关依赖
        "flask>=3.1.0",
        "gevent>=25.5.1",
        "fastapi>=0.115.0",
        "uvicorn[standard]>=0.34.0",

        # GUI/桌面相关依赖
        "PyQt5==5.15.11",  # 桌面UI #
        "playwright>=1.52.0",  # 浏览器自动化 #
        "pygame>=2.6.0",  # 音频/多媒体 #
        "html2text>=2020.1.16",  # HTML转纯文本 #
        "Pillow>=10.0.0",  # 图像处理 #

        # 系统控制相关依赖（Windows）
        "screen-brightness-control",  # 屏幕亮度控制 #
        "pycaw",  # 系统音量控制 #
        "comtypes",  # COM接口依赖 #

        # AI/ML 相关依赖（项目已实际使用）
        "numpy>=1.24.0,<2.0.0",  # 多处VAD/音频与算法使用 #
        "pandas>=2.0.0,<3.0.0",  # jmcomic 插件统计/处理 #
        "scipy>=1.15.2",  # VAD与信号处理 #
        "transformers>=4.51.3",  # 模型推理 #
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0",
            "flake8>=4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "nagaagent-core=nagaagent_core.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
