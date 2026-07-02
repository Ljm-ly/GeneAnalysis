# 更新日志

本项目所有重要的变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
并遵循 [语义化版本](https://semver.org/lang/zh-CN/spec/v2.0.0.html) 规范。

---

## [1.0.0] - 2026-07-02

### ✨ 新增

- **软件使用说明书（Word格式）**：新增《基因表达调控分析与预测平台（V1.0）软件使用说明书.docx》，包含完整的六章内容：
  - 第一章：前言（编写目的、项目背景、适用对象）
  - 第二章：系统架构设计（功能架构、数据结构设计）
  - 第三章：平台系统操作描述（仪表板、数据配置、运行分析、结果展示、下载结果、侧边栏导航、命令行模式）
  - 第四章：系统测试（功能测试、性能测试）
  - 第五章：常见问题与解决方案（数据上传、分析参数、可视化图表、结果下载、命令行模式、Web应用）
  - 第六章：附录（示例数据格式、参数调整建议、技术支持与联系方式）
- **GitHub 仓库地址**：项目开源发布至 GitHub，仓库地址为 https://github.com/Ljm-ly/GeneAnalysis
- **Streamlit 在线应用**：平台已部署至 Streamlit Community Cloud，可直接访问 https://geneanalysis-app.streamlit.app/ 使用
- **快速部署指南**：提供基于 GitHub 仓库一键部署至 Streamlit Cloud 的完整操作步骤
- **Code Wiki 文档**：新增 CODE_WIKI.md，包含项目架构、模块说明、API 文档与开发指南
- **Markdown 版使用说明书**：同步提供 MD 格式的软件使用说明书，便于版本管理与在线阅读

### 📚 文档

- 更新 `README.md`，在首页显著位置展示 GitHub 仓库地址、在线应用链接与使用说明书下载入口
- 新增 `CODE_WIKI.md`，提供面向开发者的技术文档与架构说明
- 新增 `基因表达调控分析与预测平台（V1.0）软件使用说明书.md`，Markdown 格式使用说明书
- 新增 `基因表达调控分析与预测平台（V1.0）软件使用说明书.docx`，Word 格式使用说明书

### 🔧 配置

- 新增 `.streamlit/config.toml`，Streamlit 应用配置文件
- 新增 `config.ini` 与 `config.toml`，多格式配置支持
- 新增 `.devcontainer/devcontainer.json`，VS Code 开发容器配置
- 新增 `requirements_web.txt`，Web 部署专用依赖清单

---

## [0.1.0] - 初始版本

### ✨ 核心功能

- 🔬 **序列分析模块**：FASTA 文件读取、GC 含量计算、核苷酸频率统计、序列长度分布
- 📊 **差异表达分析模块**：t 检验统计、BH-FDR 多重检验校正、上调/下调基因识别
- 📈 **可视化模块**：火山图、表达热图、PCA 主成分分析图、GC 含量分布图
- 🤖 **机器学习模块**：随机森林分类、特征重要性分析、模型性能评估
- 🖥️ **Web 界面**：基于 Streamlit 的交互式 Web 应用，支持数据上传、参数配置、实时分析与结果下载
- 💻 **命令行模式**：支持 `main.py` 脚本批处理运行，适用于服务器环境与自动化流程

---

**Made with ❤️ by GeneAnalysis Team**
