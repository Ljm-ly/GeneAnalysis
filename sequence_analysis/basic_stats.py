# -*- coding: utf-8 -*-
"""
序列基础统计模块
提供计算DNA序列各种统计指标的方法，如GC含量、核苷酸频率等

这些是序列分析中最基础、最常用的统计量。
GC含量和核苷酸频率反映了DNA的化学特性和进化压力。
"""
import numpy as np                    # NumPy库，高效的数值计算
from typing import List, Dict         # 类型提示
from collections import Counter       # 计数器类，高效统计元素出现次数
import logging                        # 日志模块


class SequenceStats:
    """
    序列统计类
    
    对一组DNA序列进行各种统计分析。
    主要关注GC含量（DNA稳定性的指标）和核苷酸频率（碱基组成）。
    """
    
    def __init__(self, sequences: List[Dict]):
        """
        初始化统计对象
        
        Args:
            sequences: 序列字典列表，每个字典包含：
                - 'id': 序列标识符
                - 'sequence': 碱基序列字符串
                - 'length': 序列长度（可选）
        """
        # 保存序列数据到实例变量
        self.sequences = sequences
        
        # 获取日志记录器
        self.logger = logging.getLogger(__name__)
        
        # 记录初始化信息
        self.logger.info(f"初始化序列统计，共 {len(sequences)} 条序列")
    
    def calculate_gc_content(self) -> List[float]:
        """
        计算每条序列的GC含量
        
        GC含量 = (G数量 + C数量) / 总碱基数 × 100%
        
        为什么GC含量重要？
        1. DNA热稳定性：GC碱基对有3个氢键，AT只有2个
           GC含量高的生物通常生活在高温环境（如嗜热菌）
        2. 基因组特性：不同物种的GC含量差异很大
           - 人类基因组：约41% GC
           - 拟南芥：约36% GC
           - 稻瘟病菌：约52% GC
        3. 基因密度：GC含量高的区域通常基因更密集
        4. 密码子偏好：不同GC含量影响同义密码子的选择
        
        Returns:
            List[float]: 每条序列的GC含量百分比列表
                例如：[45.2, 52.1, 38.7, ...]
        """
        # 初始化结果列表
        gc_contents = []
        
        # 遍历所有序列
        for seq_dict in self.sequences:
            # 获取序列字符串
            # .upper() 转成大写，因为序列可能包含小写字符
            sequence = seq_dict['sequence'].upper()
            
            # 统计G（鸟嘌呤）和C（胞嘧啶）的数量
            # str.count() 统计子串出现次数
            g_count = sequence.count('G')  # 统计G碱基个数
            c_count = sequence.count('C')  # 统计C碱基个数
            
            # 计算GC含量百分比
            if len(sequence) > 0:
                # 公式：(G数 + C数) / 总长度 × 100
                gc_percent = (g_count + c_count) / len(sequence) * 100
            else:
                # 空序列时返回0.0，避免除以零错误
                gc_percent = 0.0
            
            # 将当前序列的GC含量添加到结果列表
            gc_contents.append(gc_percent)
            
            # 记录调试信息
            self.logger.debug(f"序列 {seq_dict['id']} 的GC含量: {gc_percent:.2f}%")
        
        # 如果有GC含量数据，计算并记录平均值
        if gc_contents:
            # np.mean 是NumPy的均值函数，比Python内置sum()/len()更快
            avg_gc = np.mean(gc_contents)
            self.logger.info(f"平均GC含量: {avg_gc:.2f}%")
        
        # 返回所有序列的GC含量列表
        return gc_contents
    
    def calculate_nucleotide_frequencies(self) -> Dict[str, float]:
        """
        计算所有序列中每种核苷酸的总体频率
        
        核苷酸频率反映了基因组的碱基组成偏好。
        正常生物的A和T、C和G频率通常接近（Chargaff规则）。
        如果频率明显偏离，可能暗示：
        - 测序错误
        - 物种特异性（如某些噬菌体AT含量极高）
        - 选择压力
        
        N表示不确定碱基（测序质量差或无法判读的位置）。
        
        Returns:
            Dict[str, float]: 各核苷酸的频率字典
                例如：{'A': 0.30, 'T': 0.30, 'G': 0.20, 'C': 0.20, 'N': 0.00}
                频率范围是 [0.0, 1.0]，所有频率之和应接近1.0
        """
        # 使用Counter统计各碱基出现次数
        # Counter会自动统计可迭代对象中每个元素的出现次数
        total_counts = Counter()
        
        # 总长度
        total_length = 0
        
        # 遍历所有序列
        for seq_dict in self.sequences:
            # 获取序列字符串并转为大写
            sequence = seq_dict['sequence'].upper()
            
            # update() 累加计数
            # Counter会自动把序列中每个字符的出现次数加起来
            total_counts.update(sequence)
            
            # 累加当前序列的长度到总长度
            total_length += len(sequence)
        
        # 如果总长度为0（所有序列都为空），返回空字典
        if total_length == 0:
            return {}
        
        # 初始化频率字典
        frequencies = {}
        
        # 遍历五种核苷酸
        for nucleotide in ['A', 'T', 'G', 'C', 'N']:
            # 计算该核苷酸的频率
            # .get(nucleotide, 0)：如果该碱基存在返回其数量，否则返回0
            # 这样可以处理序列中不包含某些碱基的情况
            count = total_counts.get(nucleotide, 0)
            freq = count / total_length
            frequencies[nucleotide] = freq
        
        # 记录计算完成信息
        self.logger.info(f"核苷酸频率计算完成: {frequencies}")
        
        # 返回频率字典
        return frequencies
    
    def calculate_gc_skew(self, window_size: int = 100) -> List[List[float]]:
        """
        计算每条序列的GC偏斜（GC skew）
        
        GC偏斜 = (G - C) / (G + C)
        
        取值范围：[-1, 1]
        - 正偏斜（G > C）：前导链特征，可能指示复制方向
        - 负偏斜（C > G）：滞后链特征
        - 零偏斜（G = C）：无偏向
        
        应用场景：
        1. 细菌基因组：GC偏斜的转折点通常对应复制起始位点（oriC）
        2. 真核生物：帮助识别复制起始区
        3. 线粒体：帮助识别复制起点
        
        滑动窗口策略：
        - 使用窗口可以捕捉局部特征
        - 步长=窗口大小的一半，使相邻窗口有50%重叠
        - 窗口太小容易受随机波动影响，窗口太大可能掩盖局部特征
        
        Args:
            window_size: 滑动窗口大小，默认100个碱基对
            
        Returns:
            List[List[float]]: 每条序列的GC偏斜值列表
                外层列表：每条序列
                内层列表：该序列每个窗口的偏斜值
        """
        # 初始化所有序列的偏斜结果列表
        all_skews = []
        
        # 遍历所有序列
        for seq_dict in self.sequences:
            # 获取序列字符串并转为大写
            sequence = seq_dict['sequence'].upper()
            
            # 初始化当前序列的偏斜值列表
            skews = []
            
            # 使用滑动窗口计算GC偏斜
            # range(起始, 结束, 步长)
            # 步长设为窗口大小的一半，实现50%重叠
            step = window_size // 2
            for i in range(0, len(sequence) - window_size + 1, step):
                # 取窗口内的子序列
                window = sequence[i:i + window_size]
                
                # 统计窗口内G和C的数量
                g_count = window.count('G')
                c_count = window.count('C')
                
                # 计算GC偏斜
                if g_count + c_count > 0:
                    # 公式：(G - C) / (G + C)
                    # 结果范围：[-1, 1]
                    skew = (g_count - c_count) / (g_count + c_count)
                else:
                    # 窗口内没有G和C（如全是AT），偏斜设为0
                    skew = 0.0
                
                # 将当前窗口的偏斜值添加到列表
                skews.append(skew)
            
            # 将当前序列的偏斜列表添加到总结果
            all_skews.append(skews)
        
        # 返回所有序列的GC偏斜列表
        return all_skews
    
    def get_summary_statistics(self) -> Dict:
        """
        获取汇总统计信息
        
        一次计算返回多个常用的统计指标，便于快速了解数据特征。
        
        Returns:
            Dict: 包含多种统计指标的字典
                - 'total_sequences': 序列总数
                - 'total_bases': 所有序列的碱基总数
                - 'gc_content_mean': GC含量平均值
                - 'gc_content_std': GC含量标准差（反映GC含量的变异程度）
                - 'length_mean': 序列长度平均值
                - 'length_min': 最短序列的长度
                - 'length_max': 最长序列的长度
                - 'length_std': 序列长度的标准差
        """
        # 获取所有序列的GC含量
        gc_contents = self.calculate_gc_content()
        
        # 提取所有序列的长度
        lengths = [seq['length'] for seq in self.sequences]
        
        # 构建汇总统计字典
        summary = {
            'total_sequences': len(self.sequences),      # 序列总数
            'total_bases': sum(lengths),                  # 所有序列的碱基总数
            'gc_content_mean': np.mean(gc_contents),      # GC含量的平均值
            'gc_content_std': np.std(gc_contents),        # GC含量的标准差
            'length_mean': np.mean(lengths),               # 序列长度的平均值
            'length_min': min(lengths),                   # 最短序列的长度
            'length_max': max(lengths),                   # 最长序列的长度
            'length_std': np.std(lengths)                 # 序列长度的标准差
        }
        
        # 返回汇总统计字典
        return summary
