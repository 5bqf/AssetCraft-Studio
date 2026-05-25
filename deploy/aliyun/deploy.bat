@echo off
REM PixelForge AI — 部署到 baiqingfeng.xyz (阿里云 ECS)
REM 用法: deploy.bat <ECS公网IP>

if "%1"=="" (
    echo 用法: deploy.bat <ECS公网IP>
    echo 示例: deploy.bat 47.96.123.456
    exit /b 1
)

set ECS_IP=%1

echo === 1/3 上传代码到 ECS ===
scp -r app.py config.py requirements.txt .env.example core exporters static root@%ECS_IP%:/opt/pixelforge-ai/
scp -r core root@%ECS_IP%:/opt/pixelforge-ai/
scp .env root@%ECS_IP%:/opt/pixelforge-ai/

echo === 2/3 执行远程安装 ===
ssh root@%ECS_IP% "bash /opt/pixelforge-ai/deploy/aliyun/setup.sh"

echo === 3/3 完成 ===
echo.
echo 浏览器打开: http://baiqingfeng.xyz
echo 或: http://%ECS_IP%
echo.
echo 查看状态: ssh root@%ECS_IP% "systemctl status pixelforge"
