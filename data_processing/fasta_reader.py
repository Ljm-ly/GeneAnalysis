# -*- coding: utf-8 -*-
"""
FASTA文件读取模块
负责从FASTA格式文件中读取基因序列数据

FASTA格式是生物信息学中最常见的序列存储格式：
- 以">"开头的行是序列标题/描述（包含ID和注释信息）
- 后续行是该序列的碱基/氨基酸序列
- 序列可以换行，但">"表示新序列的开始

示例：
>gene_001 Homo sapiens TP53 tumor protein p53
ATGAGCCACCCTGAGCCGGCTCCTGATT CCTTT...
>gene_002 Homo sapiens BRCA1 breast cancer 1
ATGCGATCGATCG...
"""
from Bio import SeqIO           # Biopython的序列输入输出模块，自动解析FASTA/FASTQ等格式
from typing import List, Dict, Optional  # 类型提示，提高代码可读性
import logging                  # 日志模块，记录处理过程


class FASTAReader:
    """
    FASTA文件读取器类
    
    封装了读取和解析FASTA文件的方法。
    使用Biopython的SeqIO模块，该模块能自动处理：
    - 多行序列（序列可以分成多行书写）
    - 空格和特殊字符
    - 不同的标题行格式
    """
    
    def __init__(self, filepath: str):
        """
        初始化读取器
        
        Args:
            filepath: FASTA文件的路径，可以是绝对路径或相对路径
        """
        # 保存文件路径到实例变量
        # self.xxx 表示这是实例属性，整个类的所有方法都可以访问
        self.filepath = filepath
        
        # 获取日志记录器
        # __name__ 在模块级别会自动是 "fasta_reader"
        # 这样可以区分不同模块的日志
        self.logger = logging.getLogger(__name__)
        
        # 初始化序列缓存列表
        # read_all() 会填充这个列表，read_by_id() 等方法会使用缓存
        self.sequences = []
    
    def read_all(self) -> List[Dict]:
        """
        读取FASTA文件中的所有序列
        
        使用Biopython的SeqIO.parse解析器，该方法：
        - 自动处理多行序列
        - 自动识别序列ID（标题行第一个空格前的内容）
        - 内存高效（使用生成器，不会一次性加载所有序列到内存）
        
        Returns:
            List[Dict]: 序列字典列表，每个字典包含：
                - 'id': 序列ID（标题行第一个空格前的内容）
                    例如 ">NP_009225.1 protein TP53" -> id = "NP_009225.1"
                - 'description': 完整描述（整个标题行，不含">"）
                - 'sequence': 序列字符串（ATCG...）
                - 'length': 序列长度（碱基或氨基酸个数）
        """
        # 初始化结果列表，用于存储所有读取的序列
        sequences = []
        
        try:
            # 使用with语句打开文件，确保文件使用后自动关闭
            # 这是Python的最佳实践，避免文件句柄泄漏
            with open(self.filepath, 'r') as handle:
                # SeqIO.parse 是迭代器，每次返回一个SeqRecord对象
                # 参数1：文件句柄
                # 参数2：文件格式，"fasta" 表示FASTA格式
                for record in SeqIO.parse(handle, "fasta"):
                    # record.id: 序列ID（Biopython自动从标题行提取）
                    # record.description: 完整描述（Biopython自动设置）
                    # record.seq: Seq对象，需要转str
                    # len(record.seq): 计算序列长度
                    
                    # 构建字典保存序列信息
                    seq_dict = {
                        'id': record.id,                    # 序列唯一标识符
                        'description': record.description,  # 完整的描述信息
                        'sequence': str(record.seq),        # 转为Python字符串
                        'length': len(record.seq)           # 序列长度
                    }
                    
                    # 将字典添加到结果列表
                    sequences.append(seq_dict)
                    
                    # 记录调试信息
                    # debug级别的日志默认不显示，需要调整日志级别
                    self.logger.debug(f"读取序列: {record.id}, 长度: {len(record.seq)}")
            
            # 将结果缓存到实例变量
            # 方便后续方法（read_by_id等）直接使用，而不需要重新读取文件
            self.sequences = sequences
            
            # 记录成功信息
            self.logger.info(f"成功读取 {len(sequences)} 条序列")
            
        except FileNotFoundError:
            # 文件未找到（如路径错误、文件名拼写错误）
            self.logger.error(f"文件未找到: {self.filepath}")
            raise  # 重新抛出异常，让调用者知道发生了什么
        except Exception as e:
            # 其他异常（如文件格式错误、编码问题）
            self.logger.error(f"读取FASTA文件时出错: {e}")
            raise
        
        # 返回读取的序列列表
        return sequences
    
    def read_by_id(self, seq_id: str) -> Optional[Dict]:
        """
        根据序列ID查找特定的序列
        
        适用于需要检索特定基因的场景，如：
        - 获取某个癌症相关基因的序列
        - 查找参考序列进行比对
        
        Args:
            seq_id: 要查找的序列ID（必须与FASTA文件中的ID完全匹配）
            
        Returns:
            Optional[Dict]: 找到则返回序列字典，否则返回None
        """
        # 遍历缓存的序列列表
        # 注意：这个方法依赖 read_all() 先被调用过
        for seq in self.sequences:
            # 检查序列ID是否匹配
            if seq['id'] == seq_id:
                # 找到匹配的序列，返回该序列字典
                return seq
        
        # 未找到匹配的序列，返回None
        # 调用者可以通过检查返回值是否为None来判断是否找到
        return None
    
    def get_statistics(self) -> Dict:
        """
        获取序列的统计信息
        
        快速了解FASTA文件中序列的基本特征：
        - 总数
        - 长度范围（最短和最长）
        - 平均长度
        - 总碱基数
        
        Returns:
            Dict: 包含统计信息的字典
        """
        # 检查是否已读取序列数据
        if not self.sequences:
            # 缓存为空，说明还没有调用 read_all()
            return {'count': 0}
        
        # 列表推导式提取所有序列的长度
        # [seq['length'] for seq in self.sequences]
        # 等价于：
        # lengths = []
        # for seq in self.sequences:
        #     lengths.append(seq['length'])
        lengths = [seq['length'] for seq in self.sequences]
        
        # 构建统计字典
        stats = {
            'count': len(self.sequences),               # 序列总数
            'min_length': min(lengths),                 # 最短序列长度
            'max_length': max(lengths),                  # 最长序列长度
            'avg_length': sum(lengths) / len(lengths),   # 平均长度（总长度/个数）
            'total_bases': sum(lengths)                 # 碱基总数（所有序列长度之和）
        }
        
        return stats
