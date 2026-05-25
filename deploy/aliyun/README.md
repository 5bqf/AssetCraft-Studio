# PixelForge AI — 阿里云 ECS + baiqingfeng.xyz 部署指南

## 前提

- 阿里云 ECS 实例 (Ubuntu 22.04，已绑定公网 IP)
- 域名 `baiqingfeng.xyz` DNS 解析在阿里云
- 安全组放行: 22 (SSH) + 80 (HTTP) + 443 (HTTPS 可选)

## 步骤一：DNS 解析

在阿里云 DNS 控制台添加 A 记录:

| 主机记录 | 记录类型 | 记录值 |
|---------|---------|--------|
| `pixelforge` (或用 @) | A | `<ECS公网IP>` |

生效后 `pixelforge.baiqingfeng.xyz` 或 `baiqingfeng.xyz` 指向 ECS。

## 步骤二：上传代码 (Windows 本机)

```bash
# 上传 pixelforge-ai 到 ECS
scp -r c:/Users/b2020/Desktop/AssetCraft-Studio/pixelforge-ai root@<ECS_IP>:/opt/
scp c:/Users/b2020/Desktop/AssetCraft-Studio/pixelforge-ai/.env root@<ECS_IP>:/opt/pixelforge-ai/
```

## 步骤三：SSH 到 ECS 执行安装

```bash
ssh root@<ECS_IP>
bash /opt/pixelforge-ai/deploy/aliyun/setup.sh
```

脚本自动完成:
- Python 环境 + 依赖安装
- systemd 服务 (开机自启、崩溃重启)
- Nginx 反向代理 (80 → 7860)
- 域名绑定

## 步骤四：验证

```bash
# ECS 上检查
systemctl status pixelforge
journalctl -u pixelforge -f

# 浏览器访问
http://<ECS公网IP>
http://baiqingfeng.xyz
```

## 更新部署

```bash
# 本地更新代码后
scp -r c:/Users/b2020/Desktop/AssetCraft-Studio/pixelforge-ai/*.py root@<ECS_IP>:/opt/pixelforge-ai/
scp -r c:/Users/b2020/Desktop/AssetCraft-Studio/pixelforge-ai/core root@<ECS_IP>:/opt/pixelforge-ai/

# 重启服务
ssh root@<ECS_IP> "systemctl restart pixelforge"
```

## 查看日志

```bash
ssh root@<ECS_IP> "journalctl -u pixelforge -n 30"
```
