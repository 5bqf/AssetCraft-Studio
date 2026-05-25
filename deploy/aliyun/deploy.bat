@echo off
REM PixelForge AI — Windows 端上传部署脚本
REM 用法: deploy.bat <ECS公网IP>

if "%1"=="" (
    echo 用法: deploy.bat <ECS公网IP>
    echo 示例: deploy.bat 47.96.123.456
    exit /b 1
)

set ECS_IP=%1

echo === 上传 pixelforge-ai 到阿里云 ECS ===

REM 上传代码 (排除缓存和虚拟环境)
scp -r ^
    --exclude="__pycache__" ^
    --exclude="*.pyc" ^
    --exclude=".pytest_cache" ^
    --exclude="static/cache" ^
    --exclude="static/exports" ^
    --exclude="static/outputs" ^
    --exclude="venv" ^
    c:\Users\b2020\Desktop\AssetCraft-Studio\pixelforge-ai ^
    root@%ECS_IP%:/opt/

REM 上传 .env (如需要)
scp c:\Users\b2020\Desktop\AssetCraft-Studio\pixelforge-ai\.env root@%ECS_IP%:/opt/pixelforge-ai/

echo === 执行远程部署脚本 ===
ssh root@%ECS_IP% "cd /opt/pixelforge-ai && bash deploy/aliyun/setup.sh"

echo === 完成 ===
echo 访问: http://%ECS_IP%
