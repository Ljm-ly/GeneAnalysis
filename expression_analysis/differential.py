# -*- coding: utf-8 -*-
"""
差异表达分析模块
使用统计方法识别在不同实验条件下表达水平显著差异的基因

这是RNA-seq数据分析中最核心的步骤。

背景知识：
- 差异表达基因（DEG）：在处理组和对照组之间表达量有显著变化的基因
- 上调基因（Up-regulated）：处理后表达量增加
- 下调基因（Down-regulated）：处理后表达量减少
- P值：原假设为"两组无差异"，P值表示观察到这么极端结果的概率
- Fold Change：倍数变化，反映变化的幅度

常用软件：DESeq2、edgeR、limma（R语言），这里是Python实现的简化版本
"""
import pandas as pd                             # Pandas库，数据处理和分析
import numpy as np                              # NumPy库，数值计算
from scipy import stats                         # SciPy统计模块，提供t检验等统计方法
from typing import Dict, List, Optional, Tuple  # 类型提示
import logging                                  # 日志模块


class DiffExpAnalyzer:
    """
    差异表达分析器类
    
    对基因表达数据进行差异分析，识别显著变化的基因。
    
    分析流程：
    1. 读取表达矩阵（基因 × 样本）
    2. 过滤低表达基因（减少假阳性）
    3. 对每个基因执行t检验（比较两组均值）
    4. 计算log2倍数变化
    5. 多重检验校正（控制假发现率）
    6. 标记显著基因
    """
    
    def __init__(self, expression_file: str):
        """
        初始化分析器
        
        Args:
            expression_file: 表达数据文件路径（CSV格式）
                行：基因
                列：样本（包含对照组和处理组）
        """
        # 获取日志记录器
        self.logger = logging.getLogger(__name__)
        
        # 尝试读取表达数据文件
        try:
            # 使用pandas读取CSV文件
            # index_col=0：第一列作为行索引（基因名）
            self.data = pd.read_csv(expression_file, index_col=0)
            # 记录成功读取的信息
            self.logger.info(f"成功读取表达数据: {self.data.shape}")
        except Exception as e:
            self.logger.error(f"读取表达数据失败: {e}")
            raise
        
        # 初始化分析结果为空
        self.results = None
    
    def _remove_low_expression(self, data: pd.DataFrame,
                                min_count: int = 10) -> pd.DataFrame:
        """
        去除低表达基因（内部方法）
        
        为什么需要过滤？
        1. 生物学意义：极低表达可能只是噪声
        2. 统计原因：低表达基因的变异通常很大，t检验不可靠
        3. 计算效率：减少检测的基因数量，加快分析
        
        阈值选择：
        - min_count=10 是常用默认值
        - 可根据测序深度调整（测序深度高可以降低阈值）
        
        Args:
            data: 表达数据框
            min_count: 最小表达计数阈值，默认10
            
        Returns:
            pd.DataFrame: 过滤后的数据
        """
        # 计算每个基因在所有样本中的平均表达量
        # axis=1：对每一行操作（每个基因）
        mean_expression = data.mean(axis=1)
        
        # 保留平均表达量大于阈值的基因
        # 布尔索引：只保留True对应的行
        filtered_data = data[mean_expression > min_count]
        
        # 计算被去除的基因数量
        removed = len(data) - len(filtered_data)
        self.logger.info(f"去除低表达基因: {removed} 个")
        
        return filtered_data
    
    def _perform_ttest(self, group1: pd.Series,
                       group2: pd.Series) -> Tuple[float, float]:
        """
        执行独立样本t检验（内部方法）
        
        t检验是比较两组均值差异的经典统计方法。
        
        原理：
        1. 原假设(H0)：两组均值相等（无差异）
        2. 备择假设(H1)：两组均值不相等
        3. 计算t统计量：反映组间差异相对于组内变异的大小
        4. 根据t统计量和自由度，计算p值
        
        解读p值：
        - p < 0.05：拒绝原假设，认为差异显著（5%概率是假阳性）
        - p < 0.01：更显著的差异（1%概率是假阳性）
        - p > 0.05：不能拒绝原假设，差异不显著
        
        注意：
        - equal_var=True 假设两组方差相等（Student's t-test）
        - equal_var=False 不假设方差相等（Welch's t-test，更稳健）
        
        Args:
            group1: 第一组（通常是对照组）的表达值序列
            group2: 第二组（通常的处理组）的表达值序列
            
        Returns:
            Tuple[float, float]: (t统计量, p值)
                t统计量：正值表示group2均值更大
                p值：越小表示差异越显著
        """
        # 使用scipy的ttest_ind函数进行双尾独立样本t检验
        # equal_var=True：假设两组方差相等
        t_stat, p_value = stats.ttest_ind(group1, group2, equal_var=True)
        
        # 返回t统计量和p值
        return t_stat, p_value
    
    def _calculate_fold_change(self, group1: pd.Series,
                                group2: pd.Series) -> float:
        """
        计算两组间的倍数变化（内部方法）
        
        Fold Change = 处理组均值 / 对照组均值
        
        为什么用log2？
        1. 对称性：2倍上调=log2(2)=1，2倍下调=log2(0.5)=-1
        2. 接近正态分布：log2变化量更接近正态分布
        3. 方便设定阈值：|log2FC| > 1 表示超过2倍变化
        
        处理零值：
        - 如果两组都为0，无法计算倍数变化，返回0
        - 如果其中一组为0，加伪计数避免无穷大
        
        Args:
            group1: 对照组表达值序列
            group2: 处理组表达值序列
            
        Returns:
            float: log2倍数变化值
                正数：上调
                负数：下调
                接近0：无变化
        """
        # 计算两组的均值
        mean1 = group1.mean()  # 对照组均值
        mean2 = group2.mean()  # 处理组均值
        
        # 使用伪计数（pseudocount）处理零值
        pseudocount = 0.01
        
        if mean1 == 0 and mean2 == 0:
            # 两组均为0，无法计算倍数变化
            return 0.0
        else:
            # 都加上伪计数，保持计算对称性
            return np.log2((mean2 + pseudocount) / (mean1 + pseudocount))
    
    def analyze(self,
                group1_cols: List[str],
                group2_cols: List[str],
                p_threshold: float = 0.05,
                log2fc_threshold: float = 1.0,
                multiple_testing: str = 'fdr_bh') -> pd.DataFrame:
        """
        执行差异表达分析（核心方法）
        
        对每个基因执行以下步骤：
        1. 提取两组数据
        2. 过滤低表达基因
        3. t检验，计算p值
        4. 计算log2倍数变化
        5. 多重检验校正（Benjamini-Hochberg FDR）
        6. 标记显著性
        
        Args:
            group1_cols: 对照组样本的列名列表
                例如：['control_0', 'control_1', 'control_2']
            group2_cols: 处理组样本的列名列表
                例如：['treatment_0', 'treatment_1', 'treatment_2']
            p_threshold: 校正后P值阈值，默认0.05
                通常0.05是行业标准，表示5%的假阳性率
            log2fc_threshold: log2倍数变化阈值，默认1.0
                1.0对应2倍变化，2.0对应4倍变化
            multiple_testing: 多重检验校正方法
                - 'fdr_bh': Benjamini-Hochberg FDR校正（推荐）
                - 'bonferroni': Bonferroni校正（最保守）
                - 其他值：不校正
            
        Returns:
            pd.DataFrame: 差异表达分析结果
                包含每个基因的：
                - gene: 基因名
                - log2_fold_change: log2倍数变化
                - p_value: 原始p值
                - corrected_p_value: 校正后p值
                - is_significant: 是否显著
                - regulation: 调控方向（up/down/no_change）
        """
        # ====== 第一步：提取两组数据 ======
        # 从表达数据中选择指定的列
        group1 = self.data[group1_cols]
        group2 = self.data[group2_cols]
        
        # ====== 第二步：去除低表达基因 ======
        # 合并两组数据
        combined = pd.concat([group1, group2], axis=1)
        # 过滤低表达基因
        filtered = self._remove_low_expression(combined)
        # 重新分离两组数据
        group1_filtered = filtered[group1_cols]
        group2_filtered = filtered[group2_cols]
        
        # ====== 第三步：对每个基因进行统计计算 ======
        results_list = []
        genes = filtered.index  # 获取基因名列表
        
        # 遍历每个基因
        for gene in genes:
            # 获取该基因在两组中的表达值
            exp1 = group1_filtered.loc[gene]  # 对照组
            exp2 = group2_filtered.loc[gene]  # 处理组
            
            # 执行t检验
            t_stat, p_value = self._perform_ttest(exp1, exp2)
            
            # 计算log2倍数变化
            log2_fc = self._calculate_fold_change(exp1, exp2)
            
            # 保存结果
            results_list.append({
                'gene': gene,                          # 基因名
                'log2_fold_change': log2_fc,           # log2倍数变化
                'p_value': p_value,                    # 原始p值
                't_statistic': t_stat,                 # t统计量
                'mean_control': exp1.mean(),           # 对照组均值
                'mean_treatment': exp2.mean()          # 处理组均值
            })
        
        # 转为DataFrame
        results_df = pd.DataFrame(results_list)
        
        # ====== 第四步：多重检验校正 ======
        # 为什么要校正？
        # 同时检验10000个基因，即使全部无差异，p<0.05的也会有约500个！
        # 多重检验校正的目的是控制假阳性数量
        
        if multiple_testing == 'fdr_bh':
            # Benjamini-Hochberg FDR校正（最常用）
            # FDR（False Discovery Rate）：假发现率
            # BH校正控制期望FDR < alpha（如0.05）
            
            n = len(results_df)
            # 获取按p值排序的索引
            sorted_p_values = results_df['p_value'].values
            sorted_indices = np.argsort(sorted_p_values)
            
            # 计算初始校正值: p × n / rank
            corrected = np.zeros(n)
            for i, idx in enumerate(sorted_indices):
                rank = i + 1  # 排名从1开始
                corrected[i] = sorted_p_values[idx] * n / rank
            
            # 保证单调性：从后往前取累积最小值
            # 这是BH校正的关键步骤
            for i in range(n - 2, -1, -1):
                corrected[i] = min(corrected[i], corrected[i + 1])
            
            # 限制最大值不超过1.0
            results_df['corrected_p_value'] = 1.0
            for i, idx in enumerate(sorted_indices):
                results_df.iloc[idx, results_df.columns.get_loc('corrected_p_value')] = min(corrected[i], 1.0)
        
        elif multiple_testing == 'bonferroni':
            # Bonferroni校正（最保守）
            # 将每个p值乘以检验总数
            n = len(results_df)
            results_df['corrected_p_value'] = results_df['p_value'] * n
            # 限制最大值为1.0
            results_df['corrected_p_value'] = results_df['corrected_p_value'].clip(upper=1.0)
        
        else:
            # 不进行校正
            results_df['corrected_p_value'] = results_df['p_value']
        
        # ====== 第五步：标记显著性 ======
        # 同时满足两个条件才算显著：
        # 1. 统计显著：校正p值 < 阈值
        # 2. 生物学显著：|log2FC| > 阈值
        results_df['is_significant'] = (
            (results_df['corrected_p_value'] < p_threshold) &
            (abs(results_df['log2_fold_change']) > log2fc_threshold)
        )
        
        # 标记调控方向
        results_df['regulation'] = 'no_change'  # 默认无变化
        # log2FC > 阈值 → 上调
        results_df.loc[results_df['log2_fold_change'] > log2fc_threshold, 'regulation'] = 'up'
        # log2FC < -阈值 → 下调
        results_df.loc[results_df['log2_fold_change'] < -log2fc_threshold, 'regulation'] = 'down'
        
        # ====== 第六步：排序 ======
        # 按校正后p值从小到大排序（最显著的排在前面）
        results_df = results_df.sort_values('corrected_p_value')
        
        # 保存到实例变量
        self.results = results_df
        
        # 统计结果
        sig_count = results_df['is_significant'].sum()
        up_count = len(results_df[results_df['regulation'] == 'up'])
        down_count = len(results_df[results_df['regulation'] == 'down'])
        
        self.logger.info(f"分析完成: {sig_count} 个显著基因")
        self.logger.info(f"  上调: {up_count}, 下调: {down_count}")
        
        return results_df
    
    def get_significant_genes(self, direction: Optional[str] = None) -> List[str]:
        """
        获取显著差异表达基因列表
        
        Args:
            direction: 表达方向筛选
                - 'up': 只返回上调基因
                - 'down': 只返回下调基因
                - None: 返回所有显著基因
                
        Returns:
            List[str]: 基因名列表
        """
        # 检查是否已执行分析
        if self.results is None:
            raise ValueError("请先执行analyze()方法")
        
        # 筛选显著基因
        significant = self.results[self.results['is_significant']]
        
        # 根据方向参数返回不同结果
        if direction == 'up':
            return significant[significant['regulation'] == 'up']['gene'].tolist()
        elif direction == 'down':
            return significant[significant['regulation'] == 'down']['gene'].tolist()
        else:
            return significant['gene'].tolist()
    
    def export_results(self, output_file: str) -> None:
        """
        导出分析结果到CSV文件
        
        Args:
            output_file: 输出文件路径
        """
        if self.results is not None:
            # 保存为CSV，index=False不保存行索引
            self.results.to_csv(output_file, index=False)
            self.logger.info(f"结果已导出到: {output_file}")
        else:
            self.logger.warning("没有可导出的结果")
