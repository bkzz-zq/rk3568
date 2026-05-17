# FRP 内网穿透部署指南

## 架构

```
App/手机 → 云服务器(你的域名:8000) → FRP隧道 → RK3568(192.168.0.100:8000)
            3Mbps 带宽
```

## 1. 云服务器（服务端）

### 下载 FRP

```bash
# 下载最新版 FRP（Linux amd64）
wget https://github.com/fatedier/frp/releases/download/v0.61.1/frp_0.61.1_linux_amd64.tar.gz
tar -xzf frp_0.61.1_linux_amd64.tar.gz
cd frp_0.61.1_linux_amd64

# 或使用国内镜像
# wget https://mirrors.huaweicloud.com/frp/0.61.1/frp_0.61.1_linux_amd64.tar.gz
```

### 配置

```bash
# 复制服务端配置
cp frps.toml /etc/frp/frps.toml
```

### 启动

```bash
# 前台测试
./frps -c /etc/frp/frps.toml

# 后台运行
nohup ./frps -c /etc/frp/frps.toml &

# 设为 systemd 服务（开机自启）
cat > /etc/systemd/system/frps.service << 'EOF'
[Unit]
Description=FRP Server
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/frps -c /etc/frp/frps.toml
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 安装
cp frps /usr/local/bin/
systemctl daemon-reload
systemctl enable frps
systemctl start frps
systemctl status frps
```

### 防火墙放行

```bash
# 放行 FRP 端口
firewall-cmd --permanent --add-port=7000/tcp   # FRP 通信
firewall-cmd --permanent --add-port=8000/tcp   # API + 视频流
firewall-cmd --permanent --add-port=8765/tcp   # WebSocket
firewall-cmd --permanent --add-port=7500/tcp   # 管理面板（可选）
firewall-cmd --reload

# 或阿里云/腾讯云安全组中放行以上端口
```

### 域名解析

在域名 DNS 管理中添加 A 记录：

```
类型:  A
名称:  smart（或你想要的子域名）
值:    云服务器公网 IP
```

## 2. RK3568（客户端）

### 下载 FRP

```bash
# 下载 ARM64 版本
wget https://github.com/fatedier/frp/releases/download/v0.61.1/frp_0.61.1_linux_arm64.tar.gz
tar -xzf frp_0.61.1_linux_arm64.tar.gz
cd frp_0.61.1_linux_arm64

# 或使用国内镜像
# wget https://mirrors.huaweicloud.com/frp/0.61.1/frp_0.61.1_linux_arm64.tar.gz
```

### 配置

```bash
# 编辑客户端配置
vi frpc.toml

# 修改 serverAddr 为你的云服务器公网 IP
# serverAddr = "123.45.67.89"
```

### 启动

```bash
# 前台测试
./frpc -c frpc.toml

# 设为 systemd 服务
cat > /etc/systemd/system/frpc.service << 'EOF'
[Unit]
Description=FRP Client
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/frpc -c /opt/frp/frpc.toml
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 安装
cp frpc /usr/local/bin/
mkdir -p /opt/frp
cp frpc.toml /opt/frp/
systemctl daemon-reload
systemctl enable frpc
systemctl start frpc
systemctl status frpc
```

## 3. 验证

```bash
# 在任意网络环境下测试
curl http://smart.example.com:8000/health
# 应返回: {"status":"ok",...}

# 视频流（局域网画质）
http://smart.example.com:8000/video/stream

# 低带宽视频流（外网推荐）
http://smart.example.com:8000/video/stream_low?quality=30&fps=15

# 极省带宽模式
http://smart.example.com:8000/video/stream_low?quality=20&fps=5&scale=0.5
```

## 4. 带宽参考（3Mbps 云服务器）

| 端点 | 画质 | 帧率 | 带宽占用 |
|------|------|------|---------|
| `/video/stream_low` (默认) | 480×270 Q30 | 15fps | ~180KB/s |
| `/video/stream_low?fps=10` | 480×270 Q30 | 10fps | ~120KB/s |
| `/video/stream_low?scale=0.5&fps=10` | 320×180 Q30 | 10fps | ~40KB/s |
| `/video/stream` | 640×360 Q60 | ~25fps | ~750KB/s ❌ 超限 |

## 5. App 端使用

```
外网:
  服务器地址: http://smart.example.com:8000
  视频流:     http://smart.example.com:8000/video/stream_low

局域网:
  服务器地址: http://192.168.0.100:8000
  视频流:     http://192.168.0.100:8000/video/stream
```

## 6. 管理面板

浏览器打开 `http://云服务器IP:7500`
- 用户名: admin
- 密码: admin123

可以查看连接状态、流量统计等。

## 7. 故障排查

```bash
# 查看客户端日志
journalctl -u frpc -n 50

# 查看服务端日志
journalctl -u frps -n 50

# 测试 FRP 端口连通性
telnet 云服务器IP 7000

# 测试转发是否工作
curl http://云服务器IP:8000/health