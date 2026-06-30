# -*- coding: utf-8 -*-
"""
机器学习模块 - 基因表达分类器

本模块使用机器学习算法对基因进行分类预测。

为什么用机器学习？
    传统的差异表达分析是"单基因视角"——分别检验每个基因是否显著。
    但基因之间不是孤立的，它们相互作用、相互调控。
    机器学习可以：
        1. 综合多个特征（表达量、变化幅度、统计显著性等）
        2. 发现更复杂的模式
        3. 预测新基因的功能类别

我们使用的算法：随机森林 (Random Forest)
    什么是随机森林？
        - 一种"集成学习"方法，由很多棵"决策树"组成
        - 每棵树独立学习，最后投票决定最终结果
        - 就像专家委员会，集体智慧

    为什么选随机森林？
        - 优点：
            - 抗过拟合能力强（多个树投票，避免单个树的错误被抵消）
            - 不需要复杂的调参（默认参数就很好）
            - 能处理高维数据（很多特征多也不怕）
            - 能给出"特征重要性"（哪些特征对分类最重要）
            - 对异常值不敏感
        - 缺点：
            - 模型比较大，解释性差（不如单棵决策树直观）
            - 训练比线性模型慢一点（但通常可以接受）

    决策树是什么？
        像一棵倒着的树：
        - 每个"根节点：所有数据
        |
        根节点：根据某个特征的阈值，把数据分成两部分
        |       /     \
        是左子树   右子树
        （满足条件  不满足条件
        |
        叶节点：最终的分类结果

        例如：
        "|log2FC| > 1？
            /     \
          是       否
          |         |
    p值 < 0.05?  非显著
        /   \
       是     否
       |       |
    显著基因  非显著
"""

# ==================== 标准库导入 ====================
import warnings                       # 警告模块，用于控制警告信息
import logging                       # 日志模块

# ==================== 第三方库导入 ====================
import numpy as np                  # NumPy：数值计算
import pandas as pd                 # Pandas：数据处理

# ==================== scikit-learn 导入 ====================
# train_test_split：将数据集分割成训练集和测试集
from sklearn.model_selection import train_test_split
# StandardScaler：数据标准化（均值为0，标准差为1）
# LabelEncoder：标签编码（把文字标签转成数字）
from sklearn.preprocessing import StandardScaler, LabelEncoder
# RandomForestClassifier：随机森林分类器
from sklearn.ensemble import RandomForestClassifier
# 评估指标：
# accuracy_score（准确率）、precision_score（精确率）、
# recall_score（召回率）、f1_score（F1分数）
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

# 忽略scikit-learn的一些警告信息
# （版本更新时可能有一些弃用警告，不影响功能
warnings.filterwarnings('ignore')


class GeneClassifier:
    """
    基因分类器类

    功能：
        1. 准备数据（清洗、特征提取、标签生成）
        2. 训练随机森林模型
        3. 对新基因进行预测
        4. 输出特征重要性分析

    使用流程：
        1. 创建分类器实例: clf = GeneClassifier()
        2. 准备数据: X, y = clf.prepare_data(deg_results, expression_data)
        3. 训练模型: results = clf.train(X, y)
        4. 预测: predictions = clf.predict(X_new)
    """

    def __init__(self, model_type: str = 'random_forest', random_state: int = 42, n_estimators: int = 100):
        """
        初始化基因分类器

        Args:
            model_type: 模型类型
                目前只支持 'random_forest'（随机森林）
                预留接口，以后可以扩展支持SVM、逻辑回归等
            random_state: 随机种子
                固定随机种子，保证每次运行结果相同
                便于调试和结果复现
            n_estimators: 随机森林中决策树的数量
                树越多，结果越稳定，但计算越慢
                默认100棵
        """
        # 保存模型类型（目前只有random_forest
        self.model_type = model_type

        # 保存随机种子
        self.random_state = random_state
        
        # 保存决策树数量
        self.n_estimators = n_estimators

        # 训练好的模型对象
        # 初始为None，调用train()后才会有值
        self.model = None

        # 数据标准化器
        # StandardScaler的作用：
        #   把每个特征都变成均值为0，标准差为1
        # 为什么要标准化？
        #   不同特征的数值范围可能差异很大
        #   （比如p值是0-1，而mean_control可能是几千）
        #   不标准化的话，数值大的特征会"话语权更大
        #   标准化后所有特征在同一尺度上，公平比较
        #
        # fit_transform() 和 transform() 的区别：
        #   fit_transform()：先计算均值和标准差（fit），再转换（transform）
        #   只在训练集上用
        #   transform()：用之前fit好的参数直接转换
        #   用在测试集和新数据上（保证用同一套标准）
        self.scaler = StandardScaler()

        # 标签编码器
        # 作用：把文字标签（如"上调/下调/无变化"）转成数字（0/1/2）
        # 因为机器学习模型只能处理数字
        # 目前我们的标签已经是0和1了，这个主要是为了扩展性
        self.label_encoder = LabelEncoder()

        # 特征列名列表
        # 记录训练时用了哪些特征
        # 预测时需要和训练时的特征顺序要一致
        self.feature_columns = []

        # 获取日志记录器
        # __name__ 会是 "machine_learning.classifier
        self.logger = logging.getLogger(__name__)

    def prepare_data(self, deg_results: pd.DataFrame,
                     expression_data: pd.DataFrame = None,
                     gene_names: list = None):
        """
        准备训练数据

        做了哪些事情：
            1. 选择特征列（哪些数据作为"输入"
            2. 处理缺失值和无穷值（机器学习算法不接受NaN和Inf）
            3. 生成标签（哪些是"显著基因"，哪些是"非显著基因"）

        Args:
            deg_results: 差异表达分析结果DataFrame
                包含每个基因的统计结果
            expression_data: 表达数据（可选，目前未使用
                以后可以加入表达谱作为额外特征
            gene_names: 基因名列表（可选，目前未使用

        Returns:
            tuple: (X, y)
                X: 特征矩阵（DataFrame，行=基因，列=特征）
                y: 标签数组（一维数组，0或1
                如果数据有问题返回 (None, None)
        """
        self.logger.info("🔧 准备机器学习训练数据...")

        # ---------- 检查1：输入数据是否为空 ----------
        if deg_results is None or deg_results.empty:
            self.logger.error("❌ 差异表达结果为空，无法准备数据")
            return None, None

        # ---------- 第一步：选择特征列 ----------
        # 我们从差异分析结果中选择有用的特征
        # 这些特征从不同角度描述基因的差异表达情况
        feature_cols = [
            'log2_fold_change',   # 变化幅度（生物学意义大小）
            'p_value',              # 原始p值（统计显著性）
            'corrected_p_value',   # 校正后p值（更严格的显著性）
            'mean_control',         # 对照组平均表达量
            'mean_treatment',     # 处理组平均表达量
            't_statistic'          # t统计量（组间差异/组内变异
        ]

        # 过滤：只保留数据中实际存在的列
        # （不同的差异分析结果可能列名不同）
        self.feature_columns = [
            col for col in feature_cols if col in deg_results.columns
        ]

        # 如果预设的特征一个都没有，退而求其次：
        # 自动选择所有数值类型的列
        if not self.feature_columns:
            self.logger.warning("⚠️  未找到预设特征列，将使用所有数值列")
            # select_dtypes选择指定类型的列
            # include=[np.number] 选择所有数值型（int, float等）
            self.feature_columns = deg_results.select_dtypes(
                include=[np.number]
            ).columns.tolist()
            # 排除明显是标签的列
            exclude_cols = ['is_significant', 'significant', 'label']
            self.feature_columns = [
                c for c in self.feature_columns if c not in exclude_cols
            ]

        # 再次检查：如果还是没有特征，报错
        if not self.feature_columns:
            self.logger.error("❌ 没有可用的特征列")
            return None, None

        self.logger.info(f"   使用特征: {self.feature_columns}")

        # ---------- 第二步：提取特征矩阵 X ----------
        # .copy() 创建副本，避免修改原始数据
        X = deg_results[self.feature_columns].copy()

        # ---------- 第三步：数据清洗 ----------
        # 机器学习算法要求输入不能有NaN（缺失值）和Inf（无穷大）
        # 所以需要处理这些"脏数据

        # 1. 把无穷大替换成NaN
        # np.inf 正无穷，-np.inf 负无穷
        X = X.replace([np.inf, -np.inf], np.nan)

        # 2. 用每列的均值填充NaN
        # 为什么用均值？
        #   - 简单常用的方法
        #   - 不会改变列的均值
        #   - 对大部分情况够用
        # 更高级的方法：KNN填充、MICE填充等
        X = X.fillna(X.mean())

        # ---------- 第四步：创建标签 y ----------
        # 标签：1 = 显著差异基因，0 = 无显著变化
        #
        # 这里我们根据log2倍数变化来定义标签：
        #   变化幅度最大的前40%的基因为"差异基因"
        #
        # 为什么用这种方式而不是直接用is_significant列？
        #   - 确保正负样本比例不会太失衡
        #   - 让模型有足够的"正样本"可以学习
        #
        # 实际应用中，可以根据需要调整标签定义方式

        # 获取log2倍数变化的值
        log2fc = deg_results['log2_fold_change'].values

        # 初始化标签数组，全是0
        labels = np.zeros(len(deg_results), dtype=int)

        # 计算log2FC绝对值的第60百分位数
        # 即：60%的基因变化幅度小于这个值
        # 前40%变化最大的作为"差异基因"
        fc_abs = np.abs(log2fc)
        threshold = np.percentile(fc_abs, 60)

        # |log2FC| 大于阈值的标记为1（差异基因）
        # 包括上调和下调的都算
        labels[log2fc > threshold] = 1    # 上调基因
        labels[log2fc < -threshold] = 1   # 下调基因
        y = labels

        # ---------- 第五步：输出统计信息 ----------
        n_total = len(y)
        n_positive = np.sum(y == 1)  # 正样本（差异基因）数量
        n_negative = np.sum(y == 0)  # 负样本（无变化）数量
        self.logger.info(
            f"✅ 数据准备完成: "
            f"X={X.shape}, "
            f"差异基因={n_positive}, "
            f"无变化={n_negative}"
        )

        return X, y

    def train(self, X, y, test_size: float = 0.2):
        """
        训练随机森林分类模型

        完整的训练流程：
            1. 数据标准化
            2. 分割训练集和测试集
            3. 创建随机森林模型
            4. 在训练集上训练
            5. 在测试集上预测
            6. 评估模型表现

        Args:
            X: 特征矩阵（DataFrame或二维数组）
            y: 标签数组（一维数组）
            test_size: 测试集比例，默认0.2（20%的数据用于测试）

        Returns:
            dict: 训练结果字典
                包含评估指标、特征重要性等信息
                如果出错，包含 'error' 键
        """
        # ---------- 输入验证 ----------
        if X is None or y is None:
            self.logger.error("❌ 训练数据为空")
            return {'error': 'Empty training data'}

        # 检查样本数量是否足够
        # 太少的话，模型学不到什么规律
        if len(X) < 10:
            self.logger.error(f"❌ 训练样本太少: {len(X)}，至少需要10个")
            return {'error': 'Too few samples'}

        self.logger.info(f"🤖 开始训练分类模型: {self.model_type}")

        try:
            # ==================================================
            # 第一步：数据标准化
            # ==================================================
            # fit_transform() 做两件事：
            #   1. fit: 计算每列的均值和标准差
            #   2. transform: 用计算出的参数进行转换
            #
            # 公式：z = (x - μ) / σ
            #   μ是均值，σ是标准差
            #   转换后：均值为0，标准差为1
            X_scaled = self.scaler.fit_transform(X)

            # ==================================================
            # 第二步：分割数据集
            # ==================================================
            # train_test_split() 随机打乱数据并分割
            #
            # 参数说明：
            #   X_scaled: 特征矩阵
            #   y: 标签数组
            #   test_size: 测试集比例
            #   random_state: 随机种子
            #
            # stratify参数说明：
            #   - 按标签分层抽样，保证训练测试集比例一致
            #   - 但当某个类别样本数太少（<2）时，不能分层抽样
            #     此时需要去掉stratify参数，否则会报错
            #
            # 返回四个值：
            #   X_train: 训练集特征
            #   X_test:  测试集特征
            #   y_train: 训练集标签
            #   y_test:  测试集标签

            # 检查每个类别的样本数
            unique, counts = np.unique(y, return_counts=True)
            min_class_count = counts.min()

            # 如果每个类别至少有2个样本，才使用分层抽样
            if min_class_count >= 2:
                X_train, X_test, y_train, y_test = train_test_split(
                    X_scaled, y,
                    test_size=test_size,
                    random_state=self.random_state,
                    stratify=y  # 按标签分层抽样
                )
                self.logger.info(f"   使用分层抽样（每类至少{min_class_count}个样本）")
            else:
                # 样本太少，不能分层抽样
                X_train, X_test, y_train, y_test = train_test_split(
                    X_scaled, y,
                    test_size=test_size,
                    random_state=self.random_state
                    # 不使用 stratify 参数
                )
                self.logger.warning(
                    f"⚠️  样本类别不平衡（最小类只有{min_class_count}个样本），"
                    f"不使用分层抽样"
                )

            self.logger.info(
                f"   训练集: {X_train.shape[0]} 样本, "
                f"测试集: {X_test.shape[0]} 样本"
            )

            # ==================================================
            # 第三步：创建随机森林分类器
            # ==================================================
            # 随机森林的主要参数：
            #
            # n_estimators : 决策树的数量
            #   越多越稳定，但计算也越慢
            #   默认100，通常够了
            #
            # max_depth : 每棵树的最大深度
            #   限制深度可以防止过拟合
            #   这里设为 min(10, 样本数//2)
            #   树太深会"死记硬背"训练数据
            #
            # random_state : 随机种子
            #   保证每次运行结果相同
            #
            # class_weight : 类别权重
            #   - 'balanced': 自动平衡类别权重
            #     如果正负样本数量差异很大，
            #     给少的那类更高的权重，避免模型偏向多数类
            #   - 但当样本数极少时，这个参数反而可能导致问题
            #     此时使用 None

            # 当样本数足够时使用 balanced，否则不用
            if min_class_count >= 2 and len(X_train) >= 10:
                class_weight = 'balanced'
            else:
                class_weight = None
                self.logger.warning(
                    f"⚠️  样本数太少（训练集仅{len(X_train)}个），"
                    f"不使用类别平衡"
                )

            self.model = RandomForestClassifier(
                n_estimators=self.n_estimators,
                max_depth=min(10, len(X_train) // 2),
                random_state=self.random_state,
                class_weight=class_weight
            )

            # ==================================================
            # 第四步：训练模型
            # ==================================================
            # fit() 是scikit-learn的标准训练方法
            # 传入训练数据和标签
            # 模型会自动学习特征和标签之间的关系
            self.model.fit(X_train, y_train)

            # ==================================================
            # 第五步：在测试集上预测
            # ==================================================
            # predict() 用训练好的模型预测
            # 返回预测的标签数组
            y_pred = self.model.predict(X_test)

            # ==================================================
            # 第六步：评估模型性能
            # ==================================================
            # 四个常用评估指标，从不同角度衡量模型好坏：
            #
            # 1. 准确率 (Accuracy)
            #    = 预测正确的 / 总数
            #    整体正确率，最简单直观
            #    但类别不平衡时会有误导性
            #
            # 2. 精确率 (Precision)
            #    = 真阳性 / (真阳性 + 假阳性)
            #    预测为正的里面，真正是正的比例
            #    "宁缺毋滥"型：精确率高表示预测为正的可信度高
            #
            # 3. 召回率 (Recall)
            #    = 真阳性 / (真阳性 + 假阴性)
            #    真正的正例中，被找出来的比例
            #    "宁可错杀"型：召回率高表示漏网之鱼少
            #
            # 4. F1分数 (F1-Score)
            #    = 2 × 精确率 × 召回率 / (精确率 + 召回率)
            #    精确率和召回率的调和平均
            #    综合指标，两者的平衡
            #
            # average='weighted' : 按各类别样本数加权平均
            #   适合多分类或类别不平衡的情况
            # zero_division=0 : 分母为0时返回0，避免报错
            results = {
                'model_type': 'random_forest',
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(
                    y_test, y_pred,
                    average='weighted',
                    zero_division=0
                ),
                'recall': recall_score(
                    y_test, y_pred,
                    average='weighted',
                    zero_division=0
                ),
                'f1_score': f1_score(
                    y_test, y_pred,
                    average='weighted',
                    zero_division=0
                ),
                'feature_importance': self._get_feature_importance_safe()
            }

            # 记录训练结果
            self.logger.info(
                f"✅ 训练完成: "
                f"准确率={results['accuracy']:.3f}, "
                f"F1={results['f1_score']:.3f}"
            )

            return results

        except Exception as e:
            self.logger.error(f"❌ 训练失败: {e}")
            return {'error': str(e)}

    def predict(self, X):
        """
        对新样本进行预测

        用训练好的模型预测基因是否是"差异基因"

        注意：
            - 必须先调用 train() 训练模型
            - 输入特征的列顺序必须和训练时一致
            - 内部会自动用训练时的参数标准化

        Args:
            X: 特征矩阵（DataFrame或二维数组）
               列顺序必须和训练时相同

        Returns:
            array: 预测标签数组
                0 = 无变化基因
                1 = 差异基因

        Raises:
            ValueError: 如果模型还没训练
        """
        # 检查模型是否已经训练
        if self.model is None:
            raise ValueError("模型未训练，请先调用 train() 方法训练模型")

        # 用训练时的标准化参数转换输入数据
        # 注意：这里用 transform()，不是 fit_transform()
        # 因为我们要用训练集的均值和标准差
        # 不能用测试集自己的（否则数据泄露！
        X_scaled = self.scaler.transform(X)

        # 返回预测结果
        return self.model.predict(X_scaled)

    def predict_proba(self, X):
        """
        预测每个类别的概率

        和 predict() 的区别：
            predict() 返回"最可能的类别（0或1）
            predict_proba() 返回每个类别的概率

        例如：
            predict()    → [0, 1, 1, 0]
            predict_proba() → [[0.9, 0.1],
                              [0.2, 0.8],
                              [0.3, 0.7],
                              [0.95, 0.05]]

        概率的好处：
            - 可以看到模型的"信心"
            - 可以调整阈值（比如概率>0.7才算正）
            - 可以画ROC曲线等

        Args:
            X: 特征矩阵

        Returns:
            array: 概率矩阵，形状为 (样本数, 类别数)
                第0列：类别0的概率
                第1列：类别1的概率
        """
        if self.model is None:
            raise ValueError("模型未训练，请先调用 train() 方法训练模型")

        # 标准化输入
        X_scaled = self.scaler.transform(X)

        # 返回预测概率
        return self.model.predict_proba(X_scaled)

    def _get_feature_importance_safe(self) -> dict:
        """
        安全地获取特征重要性

        为什么要"安全"？
            因为模型可能没训练、可能没有feature_importances_属性
            直接访问可能报错，所以做多层检查

        特征重要性是什么？
            随机森林中，每个特征对分类结果的"贡献度"
            值越大，说明这个特征越重要
            加起来等于1（归一化后）

        怎么计算的？
            主要基于"基尼不纯度减少量"或"均方误差减少量"
            简单说：这个特征帮我们把数据分得多"干净"

        Returns:
            dict: 特征名 → 重要性值的字典
                失败时返回 None
        """
        # 检查1：模型是否存在
        if self.model is None:
            return None

        # 检查2：模型是否有 feature_importances_ 属性
        if not hasattr(self.model, 'feature_importances_'):
            return None

        # 检查3：特征重要性值本身是否为None
        importance = self.model.feature_importances_
        if importance is None:
            return None

        # 检查4：特征列名列表是否为空
        if not self.feature_columns:
            return None

        # 检查5：特征数量是否匹配
        if len(self.feature_columns) != len(importance):
            return None

        # 所有检查通过，返回字典
        # zip() 把两个列表按位置配对
        # dict() 把配对的键值转成字典
        return dict(zip(self.feature_columns, importance))
