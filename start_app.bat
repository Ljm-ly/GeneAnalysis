@echo off
chcp 65001 >nul

echo ========================================
echo   基因表达调控分析与预测平台 - 启动脚本
echo ========================================
echo.

setlocal

set STREAMLIT_CONFIG_HOME=%~dp0\.streamlit

if not exist "%STREAMLIT_CONFIG_HOME%" mkdir "%STREAMLIT_CONFIG_HOME%"
if not exist "%STREAMLIT_CONFIG_HOME%\cache" mkdir "%STREAMLIT_CONFIG_HOME%\cache"

echo [INFO] 配置目录: %STREAMLIT_CONFIG_HOME%
echo.

echo [INFO] 正在启动应用...
echo [INFO] 请在浏览器中访问: http://localhost:8501
echo.
echo [INFO] 按 Ctrl+C 停止应用
echo ========================================
echo.

streamlit run app.py --server.headless true --server.port 8501

endlocal
