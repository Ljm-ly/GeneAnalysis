# -*- coding: utf-8 -*-
"""
基因表达调控分析与预测平台 - Python启动脚本

功能：
1. 设置Streamlit配置目录到项目目录下
2. 避免Windows权限问题
3. 启动Streamlit应用
"""

import os
import sys
import subprocess

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 设置Streamlit配置目录到项目目录下
streamlit_config_dir = os.path.join(current_dir, '.streamlit')

# 创建配置目录（如果不存在）
os.makedirs(streamlit_config_dir, exist_ok=True)
os.makedirs(os.path.join(streamlit_config_dir, 'cache'), exist_ok=True)

# 设置环境变量
os.environ['STREAMLIT_CONFIG_HOME'] = streamlit_config_dir
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
os.environ['STREAMLIT_SERVER_PORT'] = '8501'

print("=" * 50)
print("  基因表达调控分析与预测平台 - 启动脚本")
print("=" * 50)
print(f"配置目录: {streamlit_config_dir}")
print("正在启动应用...")
print("请在浏览器中访问: http://localhost:8501")
print("按 Ctrl+C 停止应用")
print("=" * 50)
print()

# 使用Python模块方式启动Streamlit
# 配置文件已经在C:\Users\LJM\.streamlit\config.toml，Streamlit会自动读取
cmd = [
    sys.executable,
    '-m', 'streamlit',
    'run', 'app.py',
    '--server.headless', 'true',
    '--server.port', '8501'
]

print(f"执行命令: {' '.join(cmd)}")
print()

# 执行命令
try:
    subprocess.run(cmd, cwd=current_dir)
except KeyboardInterrupt:
    print("\n应用已停止")
except Exception as e:
    print(f"\n启动失败: {e}")
