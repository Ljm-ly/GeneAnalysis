# -*- coding: utf-8 -*-
"""
单元测试模块 - 测试数据处理功能

什么是单元测试？
    单元测试是自动化的代码测试，用来验证每个"单元"（函数/类）
    是否按照预期工作。

为什么需要单元测试？
    1. 保证代码质量：确保修改代码后不会引入新bug（回归测试）
    2. 快速定位问题：出错时能快速知道是哪里坏了
    3. 文档作用：测试用例本身就是一种"使用示例"
    4. 重构信心：有测试保护，改代码时更有底气

Python的单元测试框架：unittest
    - Python内置，不需要额外安装
    - 测试类继承 unittest.TestCase
    - 测试方法以 test_ 开头
    - 用 assert... 系列方法做断言

常用断言方法：
    - assertEqual(a, b)     : a == b
    - assertNotEqual(a, b)  : a != b
    - assertTrue(x)         : bool(x) is True
    - assertFalse(x)        : bool(x) is False
    - assertIsNone(x)       : x is None
    - assertIsNotNone(x)    : x is not None
    - assertAlmostEqual(a, b): 约等于（处理浮点精度问题）
    - assertIn(item, list)  : item在list中

运行方式：
    python -m unittest tests.test_data -v
    或直接运行本文件
"""

# ==================== 标准库导入 ====================
import unittest                  # Python内置单元测试框架
import tempfile                  # 临时文件模块，创建测试用的临时文件
import os                        # 操作系统接口，文件路径操作
import sys                       # 系统模块，修改Python搜索路径

# ==================== 路径设置 ====================
# 把项目根目录添加到Python搜索路径中
# 这样测试文件就能导入项目的各个模块了
#
# 解释一下这一串dirname：
#   __file__                  : 当前文件路径 → tests/test_data.py
#   os.path.abspath(__file__) : 绝对路径
#   第1次 dirname             : 去掉文件名 → tests/
#   第2次 dirname             : 去掉tests/ → 项目根目录
# sys.path.insert(0, ...)       : 插到最前面，优先查找
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ==================== 导入待测模块 ====================
# FASTA读取器：测试序列文件读取功能
from data_processing.fasta_reader import FASTAReader
# 序列统计：测试GC含量、核苷酸频率等计算
from sequence_analysis.basic_stats import SequenceStats


# ================================================================
# 测试类1：FASTA读取器测试
# ================================================================
class TestFASTAReader(unittest.TestCase):
    """
    FASTA读取器功能测试类

    测试目标：
        1. 能否正确读取FASTA文件中的序列
        2. 能否按ID查找特定序列
        3. 遇到不存在的ID时是否返回None

    setUp/tearDown：
        setUp    - 每个测试方法执行前自动运行（准备测试环境）
        tearDown - 每个测试方法执行后自动运行（清理测试环境）
        这样每个测试都有独立、干净的环境，互不影响
    """

    def setUp(self):
        """
        测试前的准备工作 - 创建临时FASTA文件

        为什么用临时文件？
            - 测试不应该依赖真实的数据文件
            - 临时文件用完就删，不污染环境
            - 可以精确控制测试数据的内容

        NamedTemporaryFile 参数说明：
            - mode='w'      : 以写入模式打开
            - suffix='.fasta' : 文件名后缀（让FASTAReader认识格式）
            - delete=False  : 不自动删除（我们在tearDown中手动删）
            - encoding='utf-8' : 字符编码
        """
        # 创建临时文件对象
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.fasta',
            delete=False,
            encoding='utf-8'
        )

        # 写入测试数据：两条简单的DNA序列
        # FASTA格式：
        #   >序列ID
        #   序列内容
        self.temp_file.write(">test_seq_1\n")          # 第1条序列的ID
        self.temp_file.write("ATCGATCGATCG\n")          # 第1条序列（12个碱基，GC含量50%）
        self.temp_file.write(">test_seq_2\n")          # 第2条序列的ID
        self.temp_file.write("GCTAGCTAGCTA\n")          # 第2条序列（12个碱基，GC含量50%）

        # 关闭文件，确保内容写入磁盘
        # （不关闭的话，后面读取可能读不到完整内容）
        self.temp_file.close()

    def tearDown(self):
        """
        测试后的清理工作 - 删除临时文件

        为什么要清理？
            - 不留下垃圾文件
            - 下次测试从零开始
            - 避免临时文件堆积占用磁盘空间

        os.unlink() = os.remove()，都是删除文件
        """
        os.unlink(self.temp_file.name)

    def test_read_all_sequences(self):
        """
        测试1：读取所有序列

        验证内容：
            - 读取的序列数量是否正确（2条）
            - 第1条序列的ID是否正确（test_seq_1）
            - 第1条序列的长度是否正确（12个碱基）
        """
        # 步骤1：创建读取器实例，传入临时文件路径
        reader = FASTAReader(self.temp_file.name)

        # 步骤2：读取所有序列
        sequences = reader.read_all()

        # 步骤3：验证结果
        # 断言1：序列数量应该是2
        self.assertEqual(len(sequences), 2, "应该读取到2条序列")

        # 断言2：第1条序列的ID应该是 test_seq_1
        # sequences是列表，用[0]取第一个元素（字典）
        self.assertEqual(sequences[0]['id'], 'test_seq_1', "第1条序列ID错误")

        # 断言3：第1条序列的长度应该是12
        self.assertEqual(sequences[0]['length'], 12, "第1条序列长度错误")

    def test_read_by_id(self):
        """
        测试2：按ID查找序列

        验证内容：
            - 存在的ID能找到对应的序列
            - 不存在的ID返回None
        """
        # 步骤1：先读取所有序列（read_by_id依赖缓存）
        reader = FASTAReader(self.temp_file.name)
        reader.read_all()

        # 步骤2：查找存在的ID
        seq = reader.read_by_id('test_seq_1')

        # 断言1：找到的序列不应该是None
        self.assertIsNotNone(seq, "应该找到test_seq_1")

        # 断言2：序列ID应该匹配
        self.assertEqual(seq['id'], 'test_seq_1', "找到的序列ID错误")

        # 步骤3：查找不存在的ID
        not_found = reader.read_by_id('non_existent_gene')

        # 断言3：应该返回None
        self.assertIsNone(not_found, "不存在的ID应该返回None")


# ================================================================
# 测试类2：序列统计功能测试
# ================================================================
class TestSequenceStats(unittest.TestCase):
    """
    序列统计功能测试类

    测试目标：
        1. GC含量计算是否正确
        2. 核苷酸频率计算是否正确
        3. 空序列等边界情况是否正常处理
    """

    def test_gc_content(self):
        """
        测试1：GC含量计算

        用已知序列"ATCG"验证：
            A=1, T=1, C=1, G=1
            G + C = 2
            总长度 = 4
            GC含量 = 2/4 × 100% = 50.0%

        为什么用 assertAlmostEqual 而不是 assertEqual？
            浮点数计算可能有精度问题，
            比如 0.1 + 0.2 在Python中等于 0.30000000000000004
            assertAlmostEqual 会判断两个值是否"足够接近"
        """
        # 准备测试数据：一条简单的序列
        test_sequences = [
            {'id': 'seq1', 'sequence': 'ATCG', 'length': 4}
        ]

        # 创建统计对象并计算GC含量
        stats = SequenceStats(test_sequences)
        gc_contents = stats.calculate_gc_content()

        # 断言：GC含量应该约等于50.0（精确到7位小数）
        self.assertAlmostEqual(gc_contents[0], 50.0, places=6)

    def test_nucleotide_frequencies(self):
        """
        测试2：核苷酸频率计算

        用已知序列"AACCGGTT"验证：
            A=2, C=2, G=2, T=2
            总长度 = 8
            每种碱基的频率 = 2/8 = 0.25
        """
        # 准备测试数据：四个碱基各出现两次
        test_sequences = [
            {'id': 'seq1', 'sequence': 'AACCGGTT', 'length': 8}
        ]

        # 创建统计对象并计算频率
        stats = SequenceStats(test_sequences)
        freqs = stats.calculate_nucleotide_frequencies()

        # 断言：每种标准碱基的频率都应该是0.25
        self.assertAlmostEqual(freqs['A'], 0.25, places=6)
        self.assertAlmostEqual(freqs['C'], 0.25, places=6)
        self.assertAlmostEqual(freqs['G'], 0.25, places=6)
        self.assertAlmostEqual(freqs['T'], 0.25, places=6)

    def test_empty_sequence(self):
        """
        测试3：空序列的边界情况

        测试目标：验证程序在遇到空序列时不会崩溃
        （这是一种"边界测试"，测试极端/异常输入）

        预期行为：
            - GC含量应该返回 0.0（而不是除以零报错）
            - 核苷酸频率应该是空字典（没有碱基就没有频率）
        """
        # 准备测试数据：空序列
        test_sequences = [
            {'id': 'seq1', 'sequence': '', 'length': 0}
        ]

        # 创建统计对象
        stats = SequenceStats(test_sequences)

        # 测试GC含量：空序列应该返回0.0
        gc_contents = stats.calculate_gc_content()
        self.assertEqual(gc_contents[0], 0.0, "空序列GC含量应为0")

        # 测试核苷酸频率：空序列应该返回空字典
        freqs = stats.calculate_nucleotide_frequencies()
        self.assertEqual(freqs, {}, "空序列核苷酸频率应为空字典")

    def test_gc_content_multiple_sequences(self):
        """
        测试4：多条序列的GC含量

        验证：多条序列时，返回的列表长度和每条的GC含量都正确
        """
        # 准备测试数据：三条不同GC含量的序列
        test_sequences = [
            {'id': 'seq1', 'sequence': 'AAAA', 'length': 4},    # 0% GC
            {'id': 'seq2', 'sequence': 'GGCC', 'length': 4},    # 100% GC
            {'id': 'seq3', 'sequence': 'ATCG', 'length': 4},    # 50% GC
        ]

        # 计算GC含量
        stats = SequenceStats(test_sequences)
        gc_contents = stats.calculate_gc_content()

        # 断言1：返回3个值
        self.assertEqual(len(gc_contents), 3)

        # 断言2：每条序列的GC含量正确
        self.assertAlmostEqual(gc_contents[0], 0.0)     # 全A = 0%
        self.assertAlmostEqual(gc_contents[1], 100.0)   # 全GC = 100%
        self.assertAlmostEqual(gc_contents[2], 50.0)    # 各一半 = 50%


# ================================================================
# 程序入口
# ================================================================
if __name__ == '__main__':
    """
    当直接运行这个文件时，执行所有测试

    unittest.main() 会：
        1. 自动发现所有继承 unittest.TestCase 的类
        2. 自动运行所有以 test_ 开头的方法
        3. 输出测试结果（通过/失败的数量）

    命令行参数：
        -v : 详细模式，显示每个测试的名字和结果
    """
    unittest.main(verbosity=2)  # verbosity=2 显示更详细的输出
