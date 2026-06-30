# -*- coding: utf-8 -*-
"""
模拟数据生成器 - 生成1000条基因的模拟数据

生成内容：
    1. FASTA序列文件（1000条基因序列）
    2. 基因表达矩阵（1000基因 × 6样本）

数据特点：
    - 序列长度：500-2000 bp（模拟真实基因长度分布）
    - GC含量：40%-60%（符合哺乳动物基因组特征）
    - 表达量：符合对数正态分布（真实表达数据的特征）
    - 差异基因：约30%的基因在处理组有显著变化
    - 上调/下调比例：约各占一半

使用方法：
    python generate_simulated_data.py
    生成的数据会保存在 data/ 目录下
"""

import os
import random
import numpy as np
import pandas as pd


# ================================================================
# 配置参数
# ================================================================

# 随机种子，保证每次运行生成相同的数据（可复现）
RANDOM_SEED = 42

# 基因数量
N_GENES = 1000

# 样本数量
N_CONTROL = 3       # 对照组样本数
N_TREATMENT = 3     # 处理组样本数

# 序列长度范围（碱基对 bp）
MIN_SEQ_LENGTH = 500
MAX_SEQ_LENGTH = 2000

# GC含量范围（百分比）
MIN_GC_CONTENT = 40
MAX_GC_CONTENT = 60

# 差异基因比例（约30%的基因有差异表达）
DEG_PROPORTION = 0.3

# 上调基因占差异基因的比例（约一半上调，一半下调）
UPREGULATED_PROPORTION = 0.5

# 差异倍数范围（log2尺度）
# 2-8倍变化 = log2FC 1-3
MIN_LOG2FC = 1.0
MAX_LOG2FC = 3.0

# 基础表达量范围（原始计数）
# 真实RNA-seq数据中，基因表达量差异很大
MIN_BASE_EXPRESSION = 10
MAX_BASE_EXPRESSION = 5000

# 生物学重复的变异系数（CV = 标准差/均值）
# 真实实验中，重复样本之间有一定差异
CV_CONTROL = 0.15      # 对照组变异系数
CV_TREATMENT = 0.15    # 处理组变异系数


# ================================================================
# 1. 生成FASTA序列
# ================================================================

def generate_gene_sequence(gc_content: float, length: int) -> str:
    """
    生成一条指定GC含量和长度的DNA序列

    原理：
        - 先根据GC含量确定G/C和A/T的比例
        - 随机选择碱基，使得整体GC含量接近目标值

    Args:
        gc_content: 目标GC含量（百分比，如50表示50%）
        length: 序列长度（碱基对）

    Returns:
        str: DNA序列字符串
    """
    # GC比例（0-1之间）
    gc_ratio = gc_content / 100.0
    # AT比例
    at_ratio = 1 - gc_ratio

    # 每个位置随机选择碱基
    # G和C各占 gc_ratio/2，A和T各占 at_ratio/2
    bases = []
    for _ in range(length):
        r = random.random()  # 0到1之间的随机数
        if r < at_ratio / 2:
            bases.append('A')
        elif r < at_ratio:
            bases.append('T')
        elif r < at_ratio + gc_ratio / 2:
            bases.append('G')
        else:
            bases.append('C')

    return ''.join(bases)


def generate_fasta_file(output_path: str, n_genes: int):
    """
    生成FASTA格式的序列文件

    Args:
        output_path: 输出文件路径
        n_genes: 生成基因的数量
    """
    print(f"🔬 正在生成 {n_genes} 条基因序列...")

    with open(output_path, 'w', encoding='utf-8') as f:
        for i in range(n_genes):
            # 基因ID：gene_0001, gene_0002, ...
            gene_id = f"gene_{i+1:04d}"

            # 随机生成序列长度
            seq_length = random.randint(MIN_SEQ_LENGTH, MAX_SEQ_LENGTH)

            # 随机生成GC含量
            gc_content = random.uniform(MIN_GC_CONTENT, MAX_GC_CONTENT)

            # 生成序列
            sequence = generate_gene_sequence(gc_content, seq_length)

            # 基因描述（模拟真实FASTA的描述行）
            # 包含一些假的基因功能注释
            descriptions = [
                "protein coding gene",
                "transcription factor",
                "receptor protein",
                "enzyme",
                "signaling molecule",
                "structural protein",
                "transport protein",
                "cell cycle regulator"
            ]
            desc = random.choice(descriptions)

            # 写入FASTA格式
            f.write(f">{gene_id} {desc}\n")

            # 序列每60个字符换一行（标准FASTA格式）
            for j in range(0, len(sequence), 60):
                f.write(sequence[j:j+60] + '\n')

    print(f"✅ FASTA文件已生成: {output_path}")
    print(f"   基因数量: {n_genes}")
    print(f"   序列长度范围: {MIN_SEQ_LENGTH}-{MAX_SEQ_LENGTH} bp")
    print(f"   GC含量范围: {MIN_GC_CONTENT}-{MAX_GC_CONTENT}%")


# ================================================================
# 2. 生成基因表达矩阵
# ================================================================

def generate_expression_matrix(
    output_path: str,
    n_genes: int,
    n_control: int,
    n_treatment: int
):
    """
    生成基因表达矩阵

    模拟真实RNA-seq数据的特征：
        1. 表达量服从对数正态分布（大部分基因低表达，少数高表达）
        2. 生物学重复之间有一定变异
        3. 部分基因在处理组有显著变化（差异表达）

    Args:
        output_path: 输出CSV文件路径
        n_genes: 基因数量
        n_control: 对照组样本数
        n_treatment: 处理组样本数
    """
    print(f"\n📊 正在生成 {n_genes} 个基因的表达矩阵...")

    # 生成基因名列表
    gene_names = [f"gene_{i+1:04d}" for i in range(n_genes)]

    # 生成样本名列表
    control_samples = [f"control_{i}" for i in range(n_control)]
    treatment_samples = [f"treatment_{i}" for i in range(n_treatment)]
    all_samples = control_samples + treatment_samples

    # ==================================================
    # 第一步：生成每个基因的基础表达量
    # ==================================================
    # 使用对数正态分布模拟真实表达量分布
    # （真实数据中，大部分基因表达量低，少数很高）

    # log-normal分布参数
    # 均值在对数空间
    log_mu = np.log(100)   # 中位表达量约100
    log_sigma = 1.5        # 分布的离散程度

    base_expressions = np.random.lognormal(
        mean=log_mu,
        sigma=log_sigma,
        size=n_genes
    )

    # 限制表达量在合理范围内
    base_expressions = np.clip(
        base_expressions,
        MIN_BASE_EXPRESSION,
        MAX_BASE_EXPRESSION
    )

    # ==================================================
    # 第二步：确定哪些基因是差异表达基因
    # ==================================================

    # 随机选择DEG_PROPORTION比例的基因作为差异基因
    n_deg = int(n_genes * DEG_PROPORTION)
    deg_indices = np.random.choice(n_genes, size=n_deg, replace=False)
    deg_indices = set(deg_indices)  # 转成集合，查找更快

    # 其中一半上调，一半下调
    n_up = int(n_deg * UPREGULATED_PROPORTION)
    n_down = n_deg - n_up

    # 打乱顺序，随机分配上调和下调
    deg_list = list(deg_indices)
    np.random.shuffle(deg_list)
    up_indices = set(deg_list[:n_up])
    down_indices = set(deg_list[n_up:])

    # ==================================================
    # 第三步：为每个基因生成倍数变化
    # ==================================================

    log2_fold_changes = np.zeros(n_genes)

    for i in range(n_genes):
        if i in up_indices:
            # 上调基因：log2FC为正
            log2_fold_changes[i] = np.random.uniform(MIN_LOG2FC, MAX_LOG2FC)
        elif i in down_indices:
            # 下调基因：log2FC为负
            log2_fold_changes[i] = -np.random.uniform(MIN_LOG2FC, MAX_LOG2FC)
        else:
            # 非差异基因：log2FC接近0，但有微小波动
            log2_fold_changes[i] = np.random.normal(0, 0.2)

    # ==================================================
    # 第四步：生成表达矩阵
    # ==================================================

    # 创建空的DataFrame
    expression_data = pd.DataFrame(
        index=gene_names,
        columns=all_samples,
        dtype=float
    )

    for i, gene in enumerate(gene_names):
        base_exp = base_expressions[i]
        log2fc = log2_fold_changes[i]

        # 处理组的均值 = 对照组均值 × 2^log2FC
        treatment_mean = base_exp * (2 ** log2fc)

        # 生成对照组样本（有生物学变异）
        for j, sample in enumerate(control_samples):
            # 用正态分布加噪声
            # 标准差 = 均值 × CV
            std = base_exp * CV_CONTROL
            value = np.random.normal(base_exp, std)
            # 确保表达量为正
            value = max(1, value)
            expression_data.loc[gene, sample] = round(value, 1)

        # 生成处理组样本
        for j, sample in enumerate(treatment_samples):
            std = treatment_mean * CV_TREATMENT
            value = np.random.normal(treatment_mean, std)
            value = max(1, value)
            expression_data.loc[gene, sample] = round(value, 1)

    # ==================================================
    # 第五步：保存到CSV文件
    # ==================================================

    # 保存为CSV，第一列是基因名
    expression_data.to_csv(output_path, index_label='gene')

    print(f"✅ 表达矩阵已生成: {output_path}")
    print(f"   基因数量: {n_genes}")
    print(f"   样本数量: {n_control + n_treatment} (对照:{n_control}, 处理:{n_treatment})")
    print(f"   差异基因: {n_deg} 个 ({DEG_PROPORTION*100:.0f}%)")
    print(f"     上调: {n_up} 个")
    print(f"     下调: {n_down} 个")
    print(f"   表达量范围: {MIN_BASE_EXPRESSION}-{MAX_BASE_EXPRESSION}")

    # ==================================================
    # 第六步：快速统计验证
    # ==================================================

    # 简单验证一下差异是否存在
    control_mean = expression_data[control_samples].mean(axis=1)
    treatment_mean = expression_data[treatment_samples].mean(axis=1)
    actual_log2fc = np.log2(treatment_mean / control_mean)

    print(f"\n📈 数据质量检查:")
    print(f"   对照组整体均值: {control_mean.mean():.1f}")
    print(f"   处理组整体均值: {treatment_mean.mean():.1f}")
    print(f"   实际log2FC范围: {actual_log2fc.min():.2f} ~ {actual_log2fc.max():.2f}")


# ================================================================
# 主函数
# ================================================================

def main():
    """主函数：依次生成FASTA文件和表达矩阵"""

    print("=" * 60)
    print("🧬 模拟基因数据生成器")
    print("=" * 60)

    # 设置随机种子，保证可复现
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    # 确保data目录存在
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)

    # 输出文件路径
    fasta_path = os.path.join(data_dir, "simulated_genes.fasta")
    expression_path = os.path.join(data_dir, "simulated_expression.csv")

    # 生成FASTA文件
    generate_fasta_file(fasta_path, N_GENES)

    # 生成表达矩阵
    generate_expression_matrix(
        expression_path,
        N_GENES,
        N_CONTROL,
        N_TREATMENT
    )

    print("\n" + "=" * 60)
    print("🎉 所有模拟数据生成完成！")
    print("=" * 60)
    print(f"📁 FASTA文件: {fasta_path}")
    print(f"📁 表达矩阵: {expression_path}")
    print("\n💡 使用方法：")
    print("   修改 config.py 中的文件路径，然后运行 python main.py")
    print(f"   fasta_file = '{fasta_path}'")
    print(f"   expression_file = '{expression_path}'")


if __name__ == "__main__":
    main()
