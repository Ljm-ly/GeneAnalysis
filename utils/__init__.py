# -*- coding: utf-8 -*-
"""
工具函数模块 (utils)

本模块提供各种通用的辅助工具函数，
不依赖具体的生物学分析逻辑，可以在任何项目中复用。

包含的功能：
    1. 文件与目录操作 (helpers)
       - ensure_directory: 确保目录存在，不存在则创建
       - validate_file_extension: 验证文件扩展名
       - calculate_file_hash: 计算文件哈希值

    2. 数据格式转换
       - save_json: 保存字典为JSON文件
       - load_json: 从JSON文件加载数据

    3. 其他工具
       - format_timestamp: 格式化时间戳
       - chunk_list: 将列表分块

使用方式：
    from utils import ensure_directory, save_json, load_json

    ensure_directory("results/")
    save_json(data, "results/output.json")
    config = load_json("config.json")
"""

from .helpers import (
    ensure_directory,
    format_timestamp,
    validate_file_extension,
    save_json,
    load_json,
    chunk_list,
    calculate_file_hash
)

__all__ = [
    'ensure_directory',
    'format_timestamp',
    'validate_file_extension',
    'save_json',
    'load_json',
    'chunk_list',
    'calculate_file_hash'
]
