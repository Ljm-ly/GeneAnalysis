# -*- coding: utf-8 -*-
"""
主程序入口文件 - 基因表达调控分析与预测平台

本文件是整个项目的"总指挥"，负责按照预设流程依次调用各个功能模块，
完成从原始数据读取到最终结果输出的完整分析流水线。

分析流程概览：
    1. 系统初始化（配置加载、日志设置）
    2. 数据读取（FASTA序列、表达矩阵）
    3. 序列分析（GC含量、核苷酸频率）
    4. 差异表达分析（统计检验、多重校正）
    5. 可视化图表生成（4种图表）
    6. 机器学习分类（随机森林）
    7. 结果输出与保存

使用方法：
    在项目根目录下运行：python main.py
"""

# ==================== 标准库导入 ====================
# sys模块：提供与Python解释器交互的功能，如程序退出、命令行参数
import sys
# os模块：提供操作系统接口，用于文件路径操作、目录创建
import os
# logging模块：Python内置的日志系统，用于记录程序运行过程中的信息
import logging

# ==================== 第三方库导入 ====================
# pandas：数据分析的核心库，提供DataFrame数据结构，类似Excel表格
import pandas as pd
# numpy：数值计算基础库，提供高效的数组运算和数学函数
import numpy as np
# matplotlib：Python最流行的绘图库，pyplot是其命令式接口
import matplotlib.pyplot as plt

# 设置matplotlib显示中文字体
# 问题：matplotlib默认字体不支持中文，会显示为方框（豆腐块）
# 解决：指定中文字体，优先使用SimHei（黑体）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
# 解决负号"-"显示为方块的问题
plt.rcParams['axes.unicode_minus'] = False

# ==================== 项目自定义模块导入 ====================
# 配置管理类：集中管理所有参数设置
from config import AnalysisConfig
# FASTA文件读取器：专门负责解析FASTA格式的序列文件
from data_processing.fasta_reader import FASTAReader
# 序列统计分析：计算GC含量、核苷酸频率等序列特征
from sequence_analysis.basic_stats import SequenceStats
# 差异表达分析器：执行统计学检验，识别显著变化的基因
from expression_analysis.differential import DiffExpAnalyzer
# 机器学习分类器：使用随机森林算法对基因进行分类
from machine_learning.classifier import GeneClassifier
# 图表生成器：统一管理各种可视化图表的绘制
from visualization.plots import PlotGenerator


def setup_logging(log_level: int = logging.INFO) -> logging.Logger:
    """
    配置并初始化日志系统

    日志系统的作用：
        - 记录程序运行的关键节点，便于排查问题
        - 区分不同级别的信息（调试、信息、警告、错误）
        - 可以同时输出到控制台和文件

    日志级别（从低到高）：
        DEBUG    - 调试信息，最详细，开发时使用
        INFO     - 一般信息，记录正常运行状态
        WARNING  - 警告信息，可能有问题但不影响运行
        ERROR    - 错误信息，某个功能失败了
        CRITICAL - 严重错误，程序可能无法继续

    Args:
        log_level: 日志级别，默认INFO（只显示INFO及以上级别）

    Returns:
        logging.Logger: 配置好的日志记录器对象
    """
    # 创建（或获取）名为 'GeneAnalysis' 的日志记录器
    # 同一个名字的logger在程序中只有一个实例（单例模式）
    logger = logging.getLogger('GeneAnalysis')

    # 设置日志记录级别
    # 低于这个级别的日志会被忽略，不会输出
    logger.setLevel(log_level)

    # 防止重复添加处理器（如果被多次调用）
    # 检查logger是否已经有handler了
    if not logger.handlers:
        # ==================== 创建控制台输出处理器 ====================
        # StreamHandler将日志输出到终端（控制台）
        console_handler = logging.StreamHandler()
        # 处理器也有自己的级别，可以和logger不同
        console_handler.setLevel(log_level)

        # ==================== 定义日志输出格式 ====================
        # 格式字符串中可以使用的占位符：
        #   %(asctime)s      - 时间戳
        #   %(name)s         - 日志记录器名称
        #   %(levelname)s    - 日志级别名称
        #   %(message)s      - 日志消息内容
        #   %(filename)s     - 文件名
        #   %(lineno)d       - 行号
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'  # 时间格式
        )
        # 将格式器绑定到处理器
        console_handler.setFormatter(formatter)

        # 将处理器添加到日志记录器
        logger.addHandler(console_handler)

    # 返回配置好的日志记录器
    return logger


def load_configuration(logger: logging.Logger) -> AnalysisConfig:
    """
    加载并验证配置

    配置系统的设计原则：
        - 集中管理：所有参数放在一处，便于修改和维护
        - 默认配置：提供合理的默认值，开箱即用
        - 可定制化：支持从文件加载，实现不同实验的配置切换
        - 有效性验证：自动检查参数是否合理、文件是否存在

    Args:
        logger: 日志记录器对象

    Returns:
        AnalysisConfig: 验证通过的配置对象

    Raises:
        SystemExit: 配置验证失败时退出程序
    """
    logger.info("=" * 60)
    logger.info("第一步：加载配置")
    logger.info("=" * 60)

    # 使用默认配置创建配置对象
    # dataclass会自动生成__init__方法，不需要手动传参
    config = AnalysisConfig()

    # 验证配置的有效性
    # 验证内容包括：文件是否存在、参数范围是否合理
    if config.validate():
        logger.info("✅ 配置验证通过")
        logger.info(f"   FASTA文件: {config.fasta_file}")
        logger.info(f"   表达数据: {config.expression_file}")
        logger.info(f"   输出目录: {config.output_dir}")
    else:
        # 配置无效，记录错误并退出程序
        # sys.exit(1) 的1表示非零退出码，代表程序异常结束
        logger.error("❌ 配置验证失败，程序退出")
        sys.exit(1)

    return config


def load_fasta_sequences(config: AnalysisConfig, logger: logging.Logger) -> list:
    """
    读取FASTA序列文件

    FASTA格式是生物信息学的标准序列格式：
        - 以 ">" 开头的行是序列的标题/描述
        - 紧接着的行是序列本身（DNA/RNA/蛋白质）
        - 一个文件可以包含多条序列

    示例：
        >gene_001 TP53 肿瘤蛋白p53
        ATGAGCCACCCTGAGCCGGCTCCTGATTCCTT...
        >gene_002 BRCA1 乳腺癌1基因
        ATGCGATCGATCG...

    Args:
        config: 配置对象
        logger: 日志记录器

    Returns:
        list: 序列字典列表，每个字典包含id、description、sequence、length

    Raises:
        SystemExit: 读取失败时退出程序
    """
    logger.info("=" * 60)
    logger.info("第二步：读取FASTA序列数据")
    logger.info("=" * 60)

    try:
        # 创建FASTA读取器实例
        # 参数：FASTA文件的路径
        reader = FASTAReader(config.fasta_file)

        # 读取文件中所有序列
        # 返回值是一个列表，每个元素是一个字典
        sequences = reader.read_all()

        logger.info(f"✅ 成功读取 {len(sequences)} 条序列")

        # 打印前3条序列的基本信息（如果有的话）
        for i, seq in enumerate(sequences[:3]):
            logger.info(f"   序列{i+1}: {seq['id']} (长度: {seq['length']} bp)")
        if len(sequences) > 3:
            logger.info(f"   ... 还有 {len(sequences)-3} 条序列")

        return sequences

    except Exception as e:
        # 捕获所有异常，记录错误信息并退出
        logger.error(f"❌ 读取FASTA文件失败: {e}")
        sys.exit(1)


def load_expression_data(config: AnalysisConfig, logger: logging.Logger) -> pd.DataFrame:
    """
    读取基因表达数据

    表达矩阵格式说明（CSV文件）：
        - 每一行：一个基因
        - 每一列：一个样本
        - 单元格：该基因在该样本中的表达量（通常是标准化后的计数）

    示例：
        gene,control_0,control_1,control_2,treatment_0,treatment_1,treatment_2
        gene_001,100,120,110,50,60,55
        gene_002,50,55,48,200,210,195
        ...

    Args:
        config: 配置对象
        logger: 日志记录器

    Returns:
        pd.DataFrame: 表达数据矩阵（行=基因，列=样本）
                     如果文件不存在或读取失败，返回None
    """
    logger.info("=" * 60)
    logger.info("第三步：读取基因表达数据")
    logger.info("=" * 60)

    # 检查文件是否存在
    if not os.path.exists(config.expression_file):
        logger.warning(f"⚠️  表达数据文件不存在: {config.expression_file}")
        logger.warning("   跳过需要表达数据的分析步骤")
        return None

    try:
        # 使用pandas读取CSV文件
        # index_col=0：指定第一列作为行索引（基因名）
        # 这样DataFrame的行索引就是基因名，方便按基因名查找
        expression_data = pd.read_csv(config.expression_file, index_col=0)

        # shape属性返回一个元组：(行数, 列数)
        # 行数 = 基因数量，列数 = 样本数量
        n_genes, n_samples = expression_data.shape
        logger.info(f"✅ 成功读取表达数据")
        logger.info(f"   基因数量: {n_genes} 个")
        logger.info(f"   样本数量: {n_samples} 个")
        logger.info(f"   样本名称: {', '.join(expression_data.columns.tolist())}")

        return expression_data

    except Exception as e:
        # 读取失败时记录警告，不退出程序
        # 因为表达数据是可选的，没有它也可以做序列分析
        logger.warning(f"⚠️  读取表达数据失败: {e}")
        return None


def run_sequence_analysis(sequences: list, config: AnalysisConfig, logger: logging.Logger) -> dict:
    """
    执行序列基础统计分析

    序列分析是生物信息学的基础，主要关注：
        1. GC含量：DNA中鸟嘌呤(G)和胞嘧啶(C)的比例
           - 影响DNA的稳定性（GC之间有3个氢键，AT只有2个）
           - 不同物种的GC含量特征不同
        2. 核苷酸频率：A/T/G/C各占多少比例
           - 正常生物符合Chargaff规则：A≈T，G≈C
        3. GC偏斜(GC Skew)：(G-C)/(G+C)
           - 可用于预测细菌复制起始位点

    Args:
        sequences: 序列字典列表
        config: 配置对象
        logger: 日志记录器

    Returns:
        dict: 包含分析结果的字典
            - 'gc_contents': 每条序列的GC含量列表
            - 'nucleotide_freq': 核苷酸频率字典
            - 'avg_gc': 平均GC含量
    """
    logger.info("=" * 60)
    logger.info("第四步：序列基础统计分析")
    logger.info("=" * 60)

    try:
        # 创建序列统计分析器实例
        # 参数：序列数据列表
        stats = SequenceStats(sequences)

        # 计算每条序列的GC含量
        # 返回一个列表，每个元素是对应序列的GC百分比
        gc_contents = stats.calculate_gc_content()

        # 计算所有序列的总体核苷酸频率
        # 返回一个字典：{'A': 0.3, 'T': 0.3, 'G': 0.2, 'C': 0.2, 'N': 0.0}
        nucleotide_freq = stats.calculate_nucleotide_frequencies()

        # 计算平均GC含量
        # 三目运算符：条件为真时取前面的值，为假时取后面的值
        # 防止gc_contents为空时除以零
        avg_gc = sum(gc_contents) / len(gc_contents) if gc_contents else 0

        logger.info(f"✅ 序列统计分析完成")
        logger.info(f"   平均GC含量: {avg_gc:.2f}%")

        # 打印各核苷酸频率
        logger.info(f"   核苷酸频率:")
        for base, freq in nucleotide_freq.items():
            # 只打印A/T/G/C四种主要碱基，N（不确定碱基）单独处理
            if base in ['A', 'T', 'G', 'C']:
                logger.info(f"     {base}: {freq*100:.2f}%")
        if 'N' in nucleotide_freq and nucleotide_freq['N'] > 0:
            logger.info(f"     N (不确定): {nucleotide_freq['N']*100:.2f}%")

        # 将结果打包成字典返回
        # 这样调用者可以通过键名访问，不需要记住返回顺序
        return {
            'gc_contents': gc_contents,
            'nucleotide_freq': nucleotide_freq,
            'avg_gc': avg_gc
        }

    except Exception as e:
        logger.error(f"❌ 序列统计分析失败: {e}")
        # 导入traceback打印详细的错误堆栈，方便调试
        import traceback
        traceback.print_exc()
        return None


def run_differential_analysis(config: AnalysisConfig, logger: logging.Logger) -> pd.DataFrame:
    """
    执行差异表达分析

    差异表达分析的核心问题：
        "这个基因在处理组和对照组之间的表达变化是真实的，还是随机波动？"

    分析流程：
        1. 数据过滤：去除表达量太低的基因（减少假阳性）
        2. 统计检验：对每个基因做t检验，计算p值
        3. 多重校正：同时检验几千个基因，需要校正假阳性率
        4. 结果筛选：同时满足统计显著和生物学显著

    两个关键阈值：
        - P值阈值：衡量统计显著性（变化是否可靠）
        - 倍数变化阈值：衡量生物学显著性（变化幅度是否够大）

    Args:
        config: 配置对象
        logger: 日志记录器

    Returns:
        pd.DataFrame: 差异表达分析结果
                     包含每个基因的log2FC、p值、校正p值、显著性标记等
    """
    logger.info("=" * 60)
    logger.info("第五步：差异表达分析")
    logger.info("=" * 60)

    # 检查表达数据文件是否存在
    if not os.path.exists(config.expression_file):
        logger.warning("⚠️  未找到表达数据文件，跳过差异分析")
        return None

    try:
        # 创建差异表达分析器实例
        analyzer = DiffExpAnalyzer(config.expression_file)

        # 定义两组样本的列名
        # 这里假设数据中有3个对照样本和3个处理样本
        # 实际项目中，这些样本名应该从配置文件或元数据读取
        group_control = ['control_0', 'control_1', 'control_2']      # 对照组（3个生物学重复）
        group_treatment = ['treatment_0', 'treatment_1', 'treatment_2']  # 处理组（3个生物学重复）

        logger.info(f"   对照组样本: {group_control}")
        logger.info(f"   处理组样本: {group_treatment}")
        logger.info(f"   P值阈值: {config.p_value_threshold}")
        logger.info(f"   倍数变化阈值: {config.log2_fold_change_threshold} (log2尺度)")

        # 执行差异表达分析
        # 这是最核心的分析步骤，内部会：
        #   - 过滤低表达基因
        #   - 对每个基因做t检验
        #   - 计算log2倍数变化
        #   - BH-FDR多重检验校正
        #   - 标记显著性
        deg_results = analyzer.analyze(
            group1_cols=group_control,
            group2_cols=group_treatment,
            p_threshold=config.p_value_threshold,
            log2fc_threshold=config.log2_fold_change_threshold
        )

        # 统计结果
        # is_significant列是布尔值，sum()可以统计True的数量
        n_significant = deg_results['is_significant'].sum()
        n_up = len(deg_results[deg_results['regulation'] == 'up'])
        n_down = len(deg_results[deg_results['regulation'] == 'down'])

        logger.info(f"✅ 差异表达分析完成")
        logger.info(f"   总基因数: {len(deg_results)}")
        logger.info(f"   显著差异基因: {n_significant} 个")
        logger.info(f"     上调基因: {n_up} 个")
        logger.info(f"     下调基因: {n_down} 个")

        # 保存结果到CSV文件
        result_path = os.path.join(config.output_dir, "deg_results.csv")
        analyzer.export_results(result_path)
        logger.info(f"   结果已保存: {result_path}")

        return deg_results

    except Exception as e:
        logger.error(f"❌ 差异表达分析失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_visualizations(
    seq_results: dict,
    deg_results: pd.DataFrame,
    expression_data: pd.DataFrame,
    config: AnalysisConfig,
    logger: logging.Logger
) -> None:
    """
    生成所有可视化图表

    "一图胜千言" - 可视化是生物信息学分析的关键环节
    我们生成4种常用图表：

    1. GC含量分布图 - 直方图
       展示所有序列的GC含量分布，了解序列碱基组成特征

    2. 差异表达火山图 - 散点图
       X轴：log2倍数变化（变化幅度）
       Y轴：-log10(p值)（统计显著性）
       形状像火山喷发，因此得名

    3. 差异基因热图 - 热图
       展示显著差异基因在各样本中的表达模式
       红色=高表达，蓝色=低表达

    4. 样本PCA图 - 散点图
       主成分分析降维，观察样本间的相似性
       相似的样本会聚在一起

    Args:
        seq_results: 序列分析结果字典
        deg_results: 差异表达分析结果DataFrame
        expression_data: 表达数据矩阵
        config: 配置对象
        logger: 日志记录器
    """
    logger.info("=" * 60)
    logger.info("第六步：生成可视化图表")
    logger.info("=" * 60)

    # 创建图表生成器实例
    plotter = PlotGenerator()

    # 计数器：记录成功生成的图表数量
    plot_count = 0

    # ---------- 图表1：GC含量分布直方图 ----------
    # 前提：有GC含量数据
    if seq_results is not None and seq_results.get('gc_contents'):
        try:
            gc_contents = seq_results['gc_contents']
            output_path = os.path.join(config.output_dir, "gc_distribution.png")

            plotter.plot_gc_distribution(
                gc_contents,
                title="序列GC含量分布",
                output_file=output_path
            )
            logger.info(f"✅ GC含量分布图已保存")
            plot_count += 1
        except Exception as e:
            logger.warning(f"⚠️  绘制GC含量分布图失败: {e}")

    # ---------- 图表2：差异表达火山图 ----------
    # 前提：有差异表达结果
    if deg_results is not None and len(deg_results) > 0:
        try:
            output_path = os.path.join(config.output_dir, "volcano_plot.png")

            plotter.plot_volcano(
                deg_results,
                p_threshold=config.p_value_threshold,
                log2fc_threshold=config.log2_fold_change_threshold,
                title="差异表达火山图",
                output_file=output_path
            )
            logger.info(f"✅ 火山图已保存")
            plot_count += 1
        except Exception as e:
            logger.warning(f"⚠️  绘制火山图失败: {e}")

    # ---------- 图表3：基因表达热图（全部基因） ----------
    # 前提：同时有表达数据和差异分析结果
    if expression_data is not None and deg_results is not None:
        try:
            # 获取全部基因列表
            if 'gene' in deg_results.columns:
                all_genes = deg_results['gene'].tolist()
            else:
                all_genes = deg_results.index.tolist()

            # 过滤：只保留在表达数据中实际存在的基因
            available_genes = [g for g in all_genes if g in expression_data.index]

            if len(available_genes) >= 2:
                # 从表达矩阵中提取这些基因的表达数据
                heatmap_data = expression_data.loc[available_genes]

                # 根据基因数量决定是否显示行标签
                # 基因太多时，标签会重叠看不清，所以自动隐藏
                n_genes = len(available_genes)
                if n_genes > 50:
                    show_row_labels = False  # 基因太多，不显示行名
                    logger.info(f"   基因数量 ({n_genes}) 较多，热图不显示行标签")
                else:
                    show_row_labels = True   # 基因少，显示行名

                # 根据基因数量动态调整图表高度
                # 基因越多，图越高
                # 基准：20个基因用8英寸高度，按比例缩放
                fig_height = max(8, min(30, n_genes * 0.15))
                fig_width = 10

                output_path = os.path.join(config.output_dir, "expression_heatmap.png")
                plotter.plot_heatmap(
                    heatmap_data,
                    title=f"基因表达热图（共{n_genes}个基因）",
                    show_labels=show_row_labels,
                    output_file=output_path,
                    figsize=(fig_width, fig_height)
                )
                logger.info(f"✅ 热图已保存 ({n_genes} 个基因)")
                plot_count += 1
            else:
                logger.warning("⚠️  可用基因不足，无法绘制热图")

        except Exception as e:
            logger.warning(f"⚠️  绘制热图失败: {e}")
            import traceback
            traceback.print_exc()

    # ---------- 图表4：样本PCA图 ----------
    # 前提：有表达数据
    if expression_data is not None:
        try:
            output_path = os.path.join(config.output_dir, "pca_plot.png")

            # 注意：PCA需要的格式是"样本×基因"（行是样本，列是基因）
            # 但我们的表达矩阵是"基因×样本"
            # 所以需要转置：.T 就是转置操作
            plotter.plot_pca(
                expression_data.T,  # 转置后：行=样本，列=基因
                title="样本PCA主成分分析",
                output_file=output_path
            )
            logger.info(f"✅ PCA图已保存")
            plot_count += 1
        except Exception as e:
            logger.warning(f"⚠️  绘制PCA图失败: {e}")

    logger.info(f"   共生成 {plot_count} 个图表")


def run_machine_learning(
    deg_results: pd.DataFrame,
    config: AnalysisConfig,
    logger: logging.Logger
) -> pd.DataFrame:
    """
    执行机器学习基因分类

    为什么用机器学习？
        传统差异分析只看单个基因的统计显著性，
        机器学习可以综合多个特征，发现更复杂的模式。

    使用的算法：随机森林 (Random Forest)
        - 一种集成学习方法，由多棵决策树组成
        - 优点：抗过拟合、无需复杂调参、能给出特征重要性
        - 应用场景：分类、回归、特征选择

    特征（输入数据）：
        - log2_fold_change: 倍数变化
        - p_value: 原始p值
        - corrected_p_value: 校正后p值
        - mean_control: 对照组均值
        - mean_treatment: 处理组均值
        - t_statistic: t检验统计量

    标签（预测目标）：
        - 1: 显著差异基因
        - 0: 无显著变化

    Args:
        deg_results: 差异表达分析结果
        config: 配置对象
        logger: 日志记录器

    Returns:
        pd.DataFrame: 添加了预测结果的DataFrame
    """
    logger.info("=" * 60)
    logger.info("第七步：机器学习基因分类")
    logger.info("=" * 60)

    # 检查是否有数据
    if deg_results is None or len(deg_results) == 0:
        logger.warning("⚠️  无差异表达数据，跳过机器学习")
        return deg_results

    try:
        # 创建基因分类器实例
        # model_type='random_forest'：使用随机森林算法
        classifier = GeneClassifier(model_type='random_forest')

        # 定义用于分类的特征列名
        # 这些特征从不同角度描述了基因的差异表达情况
        feature_columns = [
            'log2_fold_change',      # 变化幅度（生物学意义）
            'p_value',               # 原始显著性（统计检验结果）
            'corrected_p_value',     # 校正后显著性（更严格）
            'mean_control',          # 对照组基础表达水平
            'mean_treatment',        # 处理组基础表达水平
            't_statistic'            # t统计量（组间差异/组内变异）
        ]

        # 过滤：只保留数据中实际存在的特征列
        # （有些特征可能因为数据格式不同而不存在）
        available_features = [col for col in feature_columns if col in deg_results.columns]

        if not available_features:
            logger.warning("⚠️  没有可用的特征列，跳过机器学习")
            return deg_results

        logger.info(f"   使用特征: {available_features}")

        # 提取特征矩阵 X
        # .copy() 创建副本，避免修改原始数据
        X = deg_results[available_features].copy()

        # 创建标签 y：1=显著基因，0=非显著基因
        if 'is_significant' in deg_results.columns:
            # 直接使用is_significant列，布尔值转整数
            y = deg_results['is_significant'].astype(int).values
        else:
            # 没有该列时，根据校正p值和倍数变化自己判断
            y = (
                (deg_results['corrected_p_value'] < config.p_value_threshold) &
                (abs(deg_results['log2_fold_change']) > config.log2_fold_change_threshold)
            ).astype(int).values

        logger.info(f"   样本数量: {len(y)}")
        logger.info(f"   显著基因(1): {sum(y == 1)} 个")
        logger.info(f"   非显著基因(0): {sum(y == 0)} 个")

        # 训练模型
        # test_size=0.2：20%的数据作为测试集，80%作为训练集
        # random_state：固定随机种子，保证每次运行结果相同
        train_results = classifier.train(X, y, test_size=config.test_size)

        # 检查训练是否成功
        if 'error' in train_results:
            logger.error(f"❌ 模型训练失败: {train_results['error']}")
            return deg_results

        # 打印模型评估指标
        logger.info(f"✅ 模型训练完成")
        if 'accuracy' in train_results:
            logger.info(f"   准确率 (Accuracy): {train_results['accuracy']:.4f}")
        if 'precision' in train_results:
            logger.info(f"   精确率 (Precision): {train_results['precision']:.4f}")
        if 'recall' in train_results:
            logger.info(f"   召回率 (Recall): {train_results['recall']:.4f}")
        if 'f1_score' in train_results:
            logger.info(f"   F1分数: {train_results['f1_score']:.4f}")

        # 打印特征重要性（哪些特征对分类最重要）
        if 'feature_importance' in train_results and train_results['feature_importance']:
            logger.info(f"   特征重要性排序:")
            # 按重要性从高到低排序
            sorted_features = sorted(
                train_results['feature_importance'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            for feat, imp in sorted_features:
                logger.info(f"     {feat}: {imp:.4f}")

        # 使用训练好的模型对所有基因进行预测
        predictions = classifier.predict(X)

        # 验证预测结果长度是否匹配
        if len(predictions) != len(deg_results):
            logger.warning(f"⚠️  预测结果长度不匹配")
        else:
            # 将预测结果添加到DataFrame中
            deg_results['prediction'] = predictions

        # 统计预测结果
        n_sig = sum(predictions == 1)
        n_nonsig = sum(predictions == 0)
        logger.info(f"   预测结果: 显著基因 {n_sig} 个, 非显著基因 {n_nonsig} 个")

        # 保存包含分类结果的文件
        output_path = os.path.join(
            config.output_dir,
            "deg_results_with_classification.csv"
        )
        # index=False：不保存行索引（避免多出一列Unnamed）
        deg_results.to_csv(output_path, index=False)
        logger.info(f"   分类结果已保存: {output_path}")

        return deg_results

    except Exception as e:
        logger.error(f"❌ 机器学习分类失败: {e}")
        import traceback
        traceback.print_exc()
        return deg_results


def main():
    """
    主函数 - 整个分析流程的总指挥

    按照预设顺序依次执行各个分析步骤，
    每个步骤的输出作为后续步骤的输入。

    流程设计考虑了容错性：
        - 某个步骤失败不会导致整个程序崩溃
        - 缺少某些数据时会自动跳过相关分析
        - 每个步骤都有独立的错误处理和日志记录
    """
    # ==================== 初始化 ====================
    # 设置日志系统
    logger = setup_logging()

    # 打印欢迎信息
    logger.info("🚀 基因表达调控分析与预测平台启动")
    logger.info("=" * 60)

    try:
        # ==================== 步骤1-2：配置与数据读取 ====================
        config = load_configuration(logger)
        sequences = load_fasta_sequences(config, logger)
        expression_data = load_expression_data(config, logger)

        # ==================== 步骤3：序列分析 ====================
        seq_results = run_sequence_analysis(sequences, config, logger)

        # ==================== 步骤4：差异表达分析 ====================
        deg_results = run_differential_analysis(config, logger)

        # ==================== 步骤5：可视化 ====================
        generate_visualizations(seq_results, deg_results, expression_data, config, logger)

        # ==================== 步骤6：机器学习 ====================
        run_machine_learning(deg_results, config, logger)

        # ==================== 完成 ====================
        logger.info("=" * 60)
        logger.info("🎉 所有分析流程完成！")
        logger.info(f"📂 结果保存在: {os.path.abspath(config.output_dir)}")
        logger.info("=" * 60)

    except KeyboardInterrupt:
        # 用户按下Ctrl+C中断程序
        logger.warning("\n⚠️  用户中断程序")
        sys.exit(0)
    except Exception as e:
        # 捕获所有未处理的异常，打印错误信息
        logger.error(f"\n❌ 程序运行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


# ==================== 程序入口判断 ====================
# 这是Python的惯用写法，作用是：
#
# 1. 当直接运行此文件时（python main.py）：
#    __name__ == "__main__" 为 True，执行 main() 函数
#
# 2. 当被其他文件导入时（import main）：
#    __name__ == "main" 为 True，不执行 main() 函数
#    只是加载函数和类的定义，供其他模块使用
#
# 这样设计的好处是同一个文件既可以独立运行，也可以被导入复用
if __name__ == "__main__":
    main()
