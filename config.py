# -*- coding: utf-8 -*-
"""
配置管理模块 - 集中管理所有分析参数

为什么需要配置管理？
    在生物信息学分析中，参数往往很多且经常需要调整：
    - 文件路径：数据放在哪、结果存在哪
    - 分析阈值：P值多少算显著、几倍变化算重要
    - 模型参数：随机森林用多少棵树
    - 可视化选项：图表尺寸、颜色方案

    把所有参数集中放在一处有以下好处：
    1. 易于修改：不用在代码中到处找参数
    2. 版本控制：可以把配置文件存入Git，记录每次分析用了什么参数
    3. 实验可复现：保存配置，别人可以完全复现你的分析结果
    4. 批量运行：不同实验用不同的配置文件

本模块使用 Python 的 @dataclass 装饰器，
它能自动生成 __init__、__repr__、__eq__ 等方法，
让配置类的定义简洁优雅。
"""

# ==================== 标准库导入 ====================
import os                            # 操作系统接口，用于文件和路径操作
from dataclasses import dataclass, asdict  # 数据类装饰器和转换函数


@dataclass
class AnalysisConfig:
    """
    分析配置类 - 基因表达分析的所有参数都在这里

    使用 dataclass 的好处：
        - 自动生成 __init__ 方法，不需要手动写
        - 自动生成 __repr__ 方法，打印更友好
        - 自动生成 __eq__ 方法，可以比较两个配置是否相同
        - 类型提示清晰，每个参数是什么类型一目了然

    参数分为以下几类：
        1. 文件路径配置：输入输出位置
        2. 分析参数配置：统计检验的阈值
        3. 机器学习参数：模型超参数
        4. 可视化参数：图表样式
    """

    # ==================================================
    # 第一部分：文件路径配置
    # ==================================================

    # FASTA序列文件路径
    # FASTA格式是生物信息学的标准序列格式
    # 包含基因ID、描述和碱基序列
    fasta_file: str = "data/simulated_genes.fasta"

    # 基因表达数据文件路径（CSV格式）
    # 表达矩阵：行=基因，列=样本，值=表达量
    expression_file: str = "data/simulated_expression.csv"

    # 分析结果输出目录
    # 所有生成的图表、结果表格都存在这里
    # 程序会自动创建这个目录（如果不存在）
    output_dir: str = "results"

    # ==================================================
    # 第二部分：分析参数配置
    # ==================================================

    # GC含量分析的滑动窗口大小（单位：碱基对 bp）
    #
    # 什么是滑动窗口？
    #   把序列分成一段段的窗口，窗口沿着序列滑动，
    #   每个窗口单独计算GC含量。
    #
    # 窗口大小的选择：
    #   - 窗口小：分辨率高（看局部细节），但波动大（噪声多）
    #   - 窗口大：分辨率低（看整体趋势），但平滑稳定
    #   - 常用范围：50-500 bp
    #
    # 应用场景：
    #   - 寻找CpG岛（GC含量高的区域，通常在基因启动子附近）
    #   - 寻找复制起始位点（GC偏斜的变化点）
    #   - 分析染色体的区域差异
    gc_window_size: int = 100

    # 差异表达分析的P值阈值（显著性水平）
    #
    # P值是什么？
    #   假设"基因在两组间没有差异"（原假设），
    #   P值表示：如果原假设为真，观察到这么极端结果的概率。
    #
    # P值越小，越有把握认为差异是真实的，不是随机波动。
    #
    # 常用阈值：
    #   - 0.05：最常用的标准（5%的假阳性率）
    #   - 0.01：更严格的标准（1%的假阳性率）
    #   - 0.001：非常严格（探索性研究可用）
    #
    # 注意：这里是"校正后"的P值阈值，
    # 因为同时检验很多基因需要多重检验校正。
    p_value_threshold: float = 0.05

    # 差异倍数阈值（log2尺度）
    #
    # 为什么同时需要P值和倍数变化？
    #   - P值告诉你"变化是否可信"（统计显著性）
    #   - 倍数变化告诉你"变化有多大"（生物学意义）
    #   两个都满足才算"显著差异基因"
    #
    # 为什么用log2尺度？
    #   - 对称性：2倍上调 = log2(2) = 1
    #             2倍下调 = log2(0.5) = -1
    #   - 直观：值的绝对值越大，变化越大
    #
    # 常用阈值对应的原始倍数：
    #   log2FC = 0.5  →  约 1.4 倍变化
    #   log2FC = 1.0  →  2 倍变化（最常用）
    #   log2FC = 1.5  →  约 2.8 倍变化
    #   log2FC = 2.0  →  4 倍变化
    log2_fold_change_threshold: float = 1.0

    # ==================================================
    # 第三部分：机器学习参数
    # ==================================================

    # 测试集占总数据的比例
    #
    # 为什么要分训练集和测试集？
    #   - 训练集：用来训练模型（学习规律）
    #   - 测试集：用来评估模型表现（检验学得好不好）
    #   - 分开的目的：避免模型"过拟合"（死记硬背训练数据）
    #
    # 常用比例：
    #   - 80%训练 + 20%测试：数据量充足时（>1000样本）
    #   - 70%训练 + 30%测试：数据量中等时
    #   - 60%训练 + 40%测试：数据量很少时
    #
    # 注意：还有更严格的验证方法，如交叉验证（Cross-Validation）
    test_size: float = 0.2

    # 随机种子（随机数生成器的初始状态）
    #
    # 为什么要固定随机种子？
    #   很多算法都有随机性（如数据分割、模型初始化），
    #   每次运行结果可能略有不同。
    #   固定随机种子可以保证：
    #     - 结果可复现：别人用同样的代码和数据得到完全一样的结果
    #     - 调试方便：改代码时可以确认是改了什么导致结果变化
    #
    # 选什么值？
    #   - 随便选一个整数就行（0、42、2024...都可以）
    #   - 42是程序员之间的一个梗（出自《银河系漫游指南》）
    random_state: int = 42

    # 随机森林中决策树的数量
    #
    # 随机森林是什么？
    #   由很多棵决策树组成，每棵树"投票"决定最终分类结果。
    #   树越多，结果越稳定，但计算量也越大。
    #
    # 如何选择？
    #   - 太少（<10）：结果不稳定，方差大
    #   - 适中（100-500）：大多数情况足够好
    #   - 太多（>1000）：收益递减，计算变慢
    #
    # 经验法则：
    #   从100开始，如果模型表现不稳定再增加。
    n_estimators: int = 100

    # ==================================================
    # 第四部分：可视化参数
    # ==================================================

    # 图表的默认尺寸（宽度, 高度），单位是英寸
    #
    # 为什么是英寸而不是像素？
    #   matplotlib使用物理尺寸（英寸），
    #   实际像素数 = 英寸数 × DPI（每英寸像素数）
    #   这样可以保证打印出来的大小一致。
    #
    # 常用尺寸参考（保存时300 DPI）：
    #   - (8, 6)  →  2400 × 1800 像素（一般图表）
    #   - (10, 8) →  3000 × 2400 像素（较复杂图表）
    #   - (12, 6) →  3600 × 1800 像素（宽图，如时间序列）
    #
    # 注意：论文图表通常有特定的尺寸要求，
    #   如单栏图约 3.5 英寸宽，双栏图约 7 英寸宽。
    figure_size: tuple = (10, 8)

    # seaborn的颜色方案（调色板名称）
    #
    # 常用调色板：
    #   - "Set2"：柔和的分类色，区分度好，适合类别变量
    #   - "Set1"：鲜艳的分类色，对比强烈
    #   - "Paired"：成对的颜色，适合展示对照组vs处理组
    #   - "viridis"：从黄到蓝的渐变色，色盲友好
    #   - "RdBu_r"：红蓝发散色，适合热图（红高蓝低）
    #   - "coolwarm"：冷暖色，适合表达量的高低对比
    #
    # 选择原则：
    #   - 类别数据用离散调色板（Set1, Set2, Paired）
    #   - 连续数据用连续调色板（viridis, magma）
    #   - 有正有负用发散调色板（RdBu, coolwarm）
    #   - 考虑色盲友好（viridis, plasma, inferno）
    color_palette: str = "Set2"

    # ==================================================
    # 方法定义
    # ==================================================

    def validate(self) -> bool:
        """
        验证配置是否有效

        检查内容：
            1. 必需的输入文件是否存在
            2. 参数是否在合理范围内
            3. 输出目录是否存在（不存在则自动创建）

        为什么要验证？
            - 早发现问题：在分析开始前就发现配置错误
            - 友好提示：告诉用户哪里错了，怎么改
            - 避免浪费时间：不会跑了半小时才发现文件路径错了

        Returns:
            bool: True表示配置有效，可以继续分析
                  False表示配置有问题，需要修正
        """
        # -------------------- 检查1：FASTA文件 --------------------
        # os.path.exists() 检查路径是否存在
        if not os.path.exists(self.fasta_file):
            print(f"⚠️  警告: FASTA文件不存在: {self.fasta_file}")
            print(f"   请检查文件路径是否正确，或者在 config 中修改 fasta_file")
            return False

        # -------------------- 检查2：P值阈值范围 --------------------
        # P值必须在 (0, 1] 之间
        # 不能等于0（概率不可能为0），也不能大于1
        if self.p_value_threshold <= 0 or self.p_value_threshold > 1:
            print(f"❌ 错误: P值阈值 {self.p_value_threshold} 超出范围")
            print(f"   P值阈值应该在 0 和 1 之间，推荐 0.05 或 0.01")
            return False

        # -------------------- 检查3：倍数变化阈值 --------------------
        # log2倍数变化应该 >= 0（因为我们取绝对值判断）
        if self.log2_fold_change_threshold < 0:
            print(f"❌ 错误: 倍数变化阈值 {self.log2_fold_change_threshold} 不能为负数")
            print(f"   推荐值：1.0（对应2倍变化）")
            return False

        # -------------------- 检查4：输出目录 --------------------
        # 如果目录不存在，自动创建
        # exist_ok=True：目录已存在时不报错
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
            print(f"📁 已创建输出目录: {self.output_dir}")

        # -------------------- 所有检查通过 --------------------
        return True

    def save_to_file(self, filepath: str) -> None:
        """
        将当前配置保存到文本文件

        为什么要保存配置？
            - 实验记录：记下这次分析用了什么参数
            - 结果复现：以后可以用同样的配置重新运行
            - 分享给他人：别人看了配置就知道你怎么做的

        保存格式：简单的键值对文本
            每行一个参数，格式为 "参数名: 参数值"

        Args:
            filepath: 保存的文件路径，如 "results/config.txt"
        """
        # 确保文件所在的目录存在
        # os.path.dirname() 获取路径中的目录部分
        # 例如 "results/config.txt" → "results"
        dir_name = os.path.dirname(filepath)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

        # 以写入模式打开文件
        # encoding='utf-8' 确保中文能正确保存
        with open(filepath, 'w', encoding='utf-8') as f:
            # 写入标题
            f.write("# 基因表达分析配置文件\n")
            f.write("# 自动生成，可手动修改\n")
            f.write("\n")

            # self.__dict__ 是对象的属性字典
            # {属性名: 属性值, ...}
            # 遍历所有属性，按 "键: 值" 格式写入
            for key, value in self.__dict__.items():
                f.write(f"{key}: {value}\n")

        print(f"✅ 配置已保存到: {filepath}")

    @classmethod
    def load_from_file(cls, filepath: str) -> 'AnalysisConfig':
        """
        从配置文件加载设置（类方法）

        类方法是什么？
            - 用 @classmethod 装饰，第一个参数是 cls（类本身）
            - 调用方式：AnalysisConfig.load_from_file("config.txt")
            - 可以创建并返回类的新实例

        支持的参数类型自动转换：
            - int：整数（如 100, 42）
            - float：浮点数（如 0.05, 1.0）
            - bool：布尔值（true/false，不区分大小写）
            - tuple：元组（如 (10, 8)）
            - str：字符串（其他情况都当作字符串）

        Args:
            filepath: 配置文件路径

        Returns:
            AnalysisConfig: 加载了配置的新实例
        """
        # 先用默认值创建一个配置实例
        # cls() 等价于 AnalysisConfig()
        config = cls()

        # 以读取模式打开文件
        with open(filepath, 'r', encoding='utf-8') as f:
            # 逐行读取
            for line_num, line in enumerate(f, 1):
                # 去掉两端空白（空格、换行符、制表符等）
                line = line.strip()

                # 跳过空行和注释行（以#开头的行）
                if not line or line.startswith('#'):
                    continue

                # 跳过不包含冒号的行（格式不对）
                if ':' not in line:
                    print(f"⚠️  第 {line_num} 行格式不正确，已跳过: {line}")
                    continue

                # 按第一个冒号分割，分成键和值
                # maxsplit=1 表示只分割一次
                # （防止值里面也包含冒号时被错误分割）
                key, value = line.split(':', 1)

                # 去掉键和值两端的空格
                key = key.strip()
                value = value.strip()

                # 检查配置对象是否有这个属性
                # hasattr(obj, name) 检查对象是否有名为name的属性
                if not hasattr(config, key):
                    print(f"⚠️  未知的配置项: {key}，已忽略")
                    continue

                # 获取该属性的原始类型
                # getattr(config, key) 获取属性值
                # type() 获取值的类型
                original_type = type(getattr(config, key))

                try:
                    # 根据原始类型进行转换

                    if original_type == bool:
                        # 布尔类型：字符串 "true" / "false"（不区分大小写）
                        setattr(config, key, value.lower() == 'true')

                    elif original_type == int:
                        # 整数类型：字符串转整数
                        setattr(config, key, int(value))

                    elif original_type == float:
                        # 浮点数类型：字符串转浮点数
                        setattr(config, key, float(value))

                    elif original_type == tuple:
                        # 元组类型：解析形如 "(10, 8)" 的字符串
                        # 步骤：
                        #   1. 去掉两端的括号和空格
                        #   2. 按逗号分割成多个元素
                        #   3. 每个元素尝试转int，失败则转float
                        #   4. 转成tuple
                        inner = value.strip('() ')  # 去掉括号和空格
                        if inner:
                            items = [item.strip() for item in inner.split(',')]
                            converted = []
                            for item in items:
                                try:
                                    converted.append(int(item))
                                except ValueError:
                                    converted.append(float(item))
                            setattr(config, key, tuple(converted))

                    else:
                        # 其他类型（如str）：直接赋值
                        setattr(config, key, value)

                except (ValueError, TypeError):
                    # 类型转换失败时打印警告
                    print(f"⚠️  配置项 {key} 的值 {value} 无法转换为 {original_type.__name__}，已跳过")

        print(f"✅ 配置已从 {filepath} 加载")
        return config

    def to_dict(self) -> dict:
        """
        将配置转换为字典格式

        用途：
            - 方便序列化（如保存为JSON）
            - 方便遍历所有配置项
            - 方便传递给其他函数

        Returns:
            dict: 包含所有配置项的字典
        """
        # asdict() 是 dataclasses 模块提供的函数
        # 可以把 dataclass 实例转换成普通字典
        return asdict(self)
