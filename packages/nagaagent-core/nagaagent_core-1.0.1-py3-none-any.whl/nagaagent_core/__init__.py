#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NagaAgent Core Package
核心依赖包，包含核心功能和API服务器相关依赖
"""

__version__ = "1.0.1"
__author__ = "NagaAgent Team"
__email__ = "nagaagent@example.com"

# 导入核心功能模块
from .core import *
from .api import *

__all__ = [
    "__version__",
    "__author__", 
    "__email__",
]
