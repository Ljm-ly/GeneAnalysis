# -*- coding: utf-8 -*-
"""
辅助工具模块
提供通用的工具函数，供其他模块调用

这些函数是通用的，不依赖特定的生物学分析逻辑，
可以在任何Python项目中复用。
"""
import os                     # 操作系统接口，用于文件和目录操作
import json                   # JSON数据处理，用于配置和元数据存储
import hashlib                # 哈希计算，用于文件完整性校验
from typing import Any, Dict  # 类型提示
from datetime import datetime  # 日期时间处理


def ensure_directory(directory: str) -> str:
    """
    确保目录存在，如果不存在则创建
    
    在保存分析结果时，通常需要先创建输出目录。
    这个函数可以自动处理目录创建，避免手动操作。
    
    Args:
        directory: 目录路径，如 "results/plots"
        
    Returns:
        str: 规范化后的目录路径
        
    示例:
        >>> ensure_directory("results/plots")
        'results/plots'
    """
    # os.makedirs创建目录，exist_ok=True表示目录已存在时不报错
    # 这比手动检查os.path.exists再创建更简洁
    os.makedirs(directory, exist_ok=True)
    
    # 返回规范化路径：处理多余的分隔符、相对路径等
    # 例如 "results//plots/." 会被规范化为 "results/plots"
    return os.path.normpath(directory)


def calculate_file_hash(filepath: str, algorithm: str = 'sha256') -> str:
    """
    计算文件的哈希值（摘要）
    
    哈希就像文件的"数字指纹"：
    - 内容相同的文件，哈希值一定相同
    - 内容不同的文件，哈希值几乎一定不同
    
    在生物信息学中的用途：
    1. 验证测序数据是否完整下载（下载前后的哈希应该一致）
    2. 检查大文件在传输过程中是否损坏
    3. 识别内容重复的文件（比对哈希而非内容，速度更快）
    
    常用算法对比：
    - SHA256：安全，速度中等，128位十六进制输出（64个字符）
    - MD5：速度快，但存在碰撞风险，适合大文件快速校验
    - SHA1：速度中等，安全性已不够好，不推荐使用
    
    Args:
        filepath: 文件的绝对或相对路径
        algorithm: 哈希算法，'sha256'（默认）或 'md5'
        
    Returns:
        str: 十六进制哈希字符串，如 'e3b0c44298fc1...'
        
    示例:
        >>> calculate_file_hash("data/sample.fasta")
        'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    """
    # hashlib.new()创建哈希对象，参数是算法名
    hash_obj = hashlib.new(algorithm)
    
    # 分块读取文件，避免大文件（如FASTQ可能几十GB）占用过多内存
    # 每次读取64KB（65536字节），处理完再读下一块
    with open(filepath, 'rb') as f:  # 'rb' = read binary（二进制模式）
        # iter(lambda: f.read(65536), b'') 创建一个迭代器
        # 每次调用lambda读取64KB，直到文件末尾返回b''终止迭代
        for chunk in iter(lambda: f.read(65536), b''):
            # update()是累积的：每次读到的块都会参与哈希计算
            hash_obj.update(chunk)
    
    # hexdigest()返回十六进制字符串（每字节转为2个十六进制字符）
    return hash_obj.hexdigest()


def format_timestamp(timestamp: float, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    将Unix时间戳转换为可读的日期时间字符串
    
    时间戳是从1970年1月1日00:00:00（UTC）开始计算的秒数。
    这是计算机存储时间的标准方式，便于计算和存储。
    
    Args:
        timestamp: Unix时间戳（秒），如 1609459200
        format_str: 输出格式，使用strftime语法
            - %Y: 4位年份（如 2024）
            - %m: 2位月份（01-12）
            - %d: 2位日期（01-31）
            - %H: 24小时制小时（00-23）
            - %M: 分钟（00-59）
            - %S: 秒（00-59）
        
    Returns:
        str: 格式化后的时间字符串
        
    示例:
        >>> format_timestamp(1609459200)
        '2021-01-01 08:00:00'
    """
    # datetime.fromtimestamp()将时间戳转为datetime对象
    # 注意：这是本地时间，不是UTC
    dt = datetime.fromtimestamp(timestamp)
    
    # strftime()按照格式字符串输出
    return dt.strftime(format_str)


def validate_file_extension(filepath: str, allowed_extensions: list) -> bool:
    """
    验证文件扩展名是否在允许列表中
    
    这是一个简单的安全检查：
    - 确保用户没有输入错误路径
    - 防止意外处理错误格式的文件
    
    Args:
        filepath: 文件路径，如 "data/expression.csv"
        allowed_extensions: 允许的扩展名列表
            注意：应该包含点号，且是小写
            如 ['.fasta', '.fa', '.fna']
            
    Returns:
        bool: True表示扩展名有效，False表示无效
        
    示例:
        >>> validate_file_extension("sample.fasta", ['.fasta', '.fa'])
        True
        >>> validate_file_extension("sample.txt", ['.fasta', '.fa'])
        False
    """
    # os.path.splitext()分割文件名和扩展名
    # 返回元组：(路径部分, 扩展名)
    # 例如 "data/sample.fasta" -> ("data/sample", ".fasta")
    _, ext = os.path.splitext(filepath)
    
    # 转为小写，实现不区分大小写的比较
    # Windows用户可能输入 "Sample.FASTA"
    ext = ext.lower()
    
    # 检查扩展名是否在允许列表中
    return ext in allowed_extensions


def save_json(data: Dict[str, Any], filepath: str) -> None:
    """
    将Python字典保存为JSON文件
    
    JSON（JavaScript Object Notation）是一种轻量级数据格式：
    - 人类可读：可以直接打开查看
    - 跨平台：任何语言都能解析
    - 结构清晰：支持嵌套的键值对
    
    常用于：
    - 保存配置参数
    - 保存分析元数据（分析时间、参数、版本等）
    - 保存结果摘要（避免每次都重新计算）
    
    Args:
        data: 要保存的Python字典
        filepath: 保存路径，如 "results/analysis_summary.json"
    """
    # 确保目标目录存在
    # os.path.dirname()获取文件所在目录的路径
    # 如果目录不存在，先创建它
    ensure_directory(os.path.dirname(filepath))
    
    # 打开文件进行写入
    # encoding='utf-8' 确保能正确保存中文等非ASCII字符
    with open(filepath, 'w', encoding='utf-8') as f:
        # json.dump()将Python对象序列化为JSON字符串并写入文件
        # indent=2: 使用2个空格缩进，使JSON更易读
        # ensure_ascii=False: 允许非ASCII字符（如中文）原样保存
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # 打印保存成功信息
    print(f"数据已保存到: {filepath}")


def load_json(filepath: str) -> Dict[str, Any]:
    """
    从JSON文件加载数据为Python字典
    
    Args:
        filepath: JSON文件路径
        
    Returns:
        Dict: 解析后的Python字典
        
    示例:
        >>> config = load_json("config.json")
        >>> print(config['p_value_threshold'])
        0.05
    """
    # 打开文件进行读取
    with open(filepath, 'r', encoding='utf-8') as f:
        # json.load()从文件读取JSON字符串并反序列化为Python对象
        data = json.load(f)
    return data


def chunk_list(data_list: list, chunk_size: int) -> list:
    """
    将列表分割成指定大小的块
    
    在处理大数据时，分块处理可以：
    - 避免内存溢出（不需要一次性加载所有数据）
    - 便于并行处理（每个块可以交给不同的CPU核心）
    - 实现增量处理（如分批训练神经网络）
    
    Args:
        data_list: 原始列表
        chunk_size: 每块的大小
        
    Returns:
        list: 分块后的列表，每个元素是一个子列表
        
    示例:
        >>> chunk_list([1,2,3,4,5], 2)
        [[1, 2], [3, 4], [5]]
        >>> # 常用于分批读取大文件
        >>> for batch in chunk_list(large_gene_list, batch_size=100):
        ...     process(batch)  # 处理每批基因
    """
    # range(0, len(data_list), chunk_size) 生成起始索引
    # 0, chunk_size, 2*chunk_size, ...
    # data_list[i:i+chunk_size] 切片截取当前块
    return [data_list[i:i + chunk_size]
            for i in range(0, len(data_list), chunk_size)]
