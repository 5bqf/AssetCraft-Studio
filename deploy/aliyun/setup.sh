#!/bin/bash
# PixelForge AI — 阿里云 ECS 一键部署脚本
# 在 ECS 实例上以 root 执行: bash setup.sh

set -e

echo "=== PixelForge AI 阿里云部署 ==="

# 1. 安装系统依赖
echo "[1/5] 安装系统依赖..."
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv nginx git

# 2. 创建应用目录
echo "[2/5] 创建应用目录..."
mkdir -p /opt/pixelforge-ai
cd /opt/pixelforge-ai

# 3. 克隆代码 (或手动上传)
echo "[3/5] 部署代码..."
# 方案A: 从 GitHub 拉取
if [ -n "$GIT_REPO" ]; then
    git clone "$GIT_REPO" .
    cd pixelforge-ai
else
    echo "请将 pixelforge-ai/ 目录上传至 /opt/pixelforge-ai/"
    echo "或设置环境变量 GIT_REPO 后重新运行"
    exit 1
fi

# 4. Python 虚拟环境
echo "[4/5] 配置 Python 环境..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

# 5. 创建 systemd 服务
echo "[5/5] 创建 systemd 服务..."
cat > /etc/systemd/system/pixelforge.service << 'SERVICE'
[Unit]
Description=PixelForge AI
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/pixelforge-ai/pixelforge-ai
Environment="PORT=7860"
EnvironmentFile=/opt/pixelforge-ai/pixelforge-ai/.env
ExecStart=/opt/pixelforge-ai/pixelforge-ai/venv/bin/python app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICE

# Nginx 反向代理
cat > /etc/nginx/sites-available/pixelforge << 'NGINX'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:7860;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
}
NGINX

ln -sf /etc/nginx/sites-available/pixelforge /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 启动服务
systemctl daemon-reload
systemctl enable pixelforge
systemctl start pixelforge
systemctl restart nginx

echo ""
echo "=== 部署完成 ==="
echo "访问: http://<ECS公网IP>"
echo "查看状态: systemctl status pixelforge"
echo "查看日志: journalctl -u pixelforge -f"
