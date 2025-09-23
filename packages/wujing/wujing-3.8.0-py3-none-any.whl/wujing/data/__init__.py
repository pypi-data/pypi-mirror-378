"""数据处理和分析模块

本模块包含数据加载、查询、处理和转换的相关功能。
"""

from .ir import IR
from .load_data import load_excel
from .deduplicate import deduplicate
from .split import split_dataset, analyze_label_distribution

__all__ = [
    "IR",
    "load_excel",
    "deduplicate",
    "split_dataset",
    "analyze_label_distribution",
]