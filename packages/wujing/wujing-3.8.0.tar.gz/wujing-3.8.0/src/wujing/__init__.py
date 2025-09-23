"""Wujing - Python 工具包

一个包含数据处理、机器学习、LLM调用、RAG和可视化等功能的Python工具包。
"""

# 导入各个子模块
from . import core
from . import data  
from . import llm
from . import ml
from . import rag
from . import text
from . import viz

__version__ = "3.7.1"

__all__ = [
    "core",
    "data", 
    "llm",
    "ml", 
    "rag",
    "text",
    "viz",
]