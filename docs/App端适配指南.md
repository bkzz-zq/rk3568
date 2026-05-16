# App 端适配指南 — 对接 RK3568 本地服务器

## 概述

原 App 连接 OneNET 云服务器 + 自建后端服务器，现改为直接连接 RK3568 本地 FastAPI 服务器。

### 架构变化

```
原架构:
  App → OneNET API (设备查询/控制)
  App → 云服务器 API (登录/用户管理)

新架构:
  App → RK3568 FastAPI (所有功能合一)
  App → cpolar 穿透地址 (外网访问)
```

## 1. 服务器地址配置

### 局域网访问

```
http://192.168.0.100:8000
```

### 外网访问（cpolar 穿透）

```
https://xxxxxx.cpolar.top
```

> App 设置中需支持配置服务器地址，两种格式都要兼容（有端口 / 无端口，http / https）。

## 2. 用户认证

### 登录接口（与原服务器兼容）

```
POST /api/login
Content-Type: application/json

请求体:
{
  "username": "admin",
  "password": "admin123"
}

响应:
{
  "success": true,
  "message": "登录成功",
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "username": "admin",
  "is_admin": true
}
```

**与原服务器的差异**：
- ✅ 请求/响应格式完全兼容
- ⚠️ JWT Secret 不同（原服务器有自己的 secret，RK3568 用 `rk3568_smart_home_secret_key_2026`）
- ⚠️ Token 有效期 7 天（原服务器可能不同）
- ⚠️ 密码加密方式：SHA256（原服务器可能用 bcrypt）

### Token 验证

```
POST /api/verify-token
Authorization: Bearer <token>

响应:
{
  "valid": true,
  "username": "admin"
}
```

### 认证方式

所有需要认证的接口，在请求头中携带：
```
Authorization: Bearer <token>
```

## 3. 设备查询（替代 OneNET）

### 原接口（OneNET）

```
GET https://iot-api.heclouds.com/thingmodel/query-device-property
  ?product_id=0g0k8iPR77
  &device_name=esp8266
Header: Authorization: <OneNET token>
```

### 新接口（RK3568）

```
GET /thingmodel/query-device-property
  ?product_id=0g0k8iPR77    # 保留，但忽略
  &device_name=esp8266       # 保留，但忽略
Header: Authorization: Bearer <JWT token>
```

### 响应格式

```json
{
  "data": [
    {
      "identifier": "tremp",
      "value": "25.5"
    },
    {
      "identifier": "hum",
      "value": "60"
    },
    {
      "identifier": "position",
      "value": "50"
    },
    {
      "identifier": "limit_sw",
      "value": "0"
    }
  ],
  "online": true,
  "last_update": 1715865600.0
}
```

**差异**：
- ✅ 响应格式与 OneNET 兼容（`data[].identifier` + `data[].value`）
- ⚠️ 新增 `online` 和 `last_update` 字段
- ⚠️ `product_id` 参数保留但不使用
- ⚠️ 认证方式从 OneNET token 改为 JWT Bearer token

## 4. 设备控制（替代 OneNET）

### 原接口（OneNET）

```
POST https://iot-api.heclouds.com/thingmodel/set-device-property
Header: Authorization: <OneNET token>

{
  "product_id": "0g0k8iPR77",
  "device_name": "esp8266",
  "params": {"led": true}
}
```

### 新接口（RK3568）

```
POST /thingmodel/set-device-property
Header: Authorization: Bearer <JWT token>
Content-Type: application/json

{
  "product_id": "0g0k8iPR77",    # 保留，兼容 App
  "device_name": "esp8266",
  "params": {"led": true}
}
```

### 响应

成功：
```json
{
  "code": 0,
  "msg": "success"
}
```

失败：
```json
{
  "detail": "命令发送失败"
}
```

**差异**：
- ✅ 请求格式兼容
- ✅ 成功响应格式兼容（`code: 0`）
- ⚠️ 认证方式从 OneNET token 改为 JWT Bearer token

## 5. AI 视觉检测（新功能）

```
GET /api/ai/detection
Header: Authorization: Bearer <token>

响应:
{
  "persons": [
    {
      "bbox": [1083, 12, 1917, 993],
      "confidence": 0.859,
      "label": "person"
    }
  ],
  "plates": [
    {
      "bbox": [100, 200, 300, 280],
      "confidence": 0.92,
      "plate": "京A12345",
      "color": "蓝"
    }
  ]
}
```

> 这是新增接口，原服务器没有。可选择性使用。

## 6. 传感器历史数据

```
GET /api/sensor-data?hours=24
Header: Authorization: Bearer <token>

响应:
{
  "hours": 24,
  "count": 480,
  "data": [
    {
      "id": 1,
      "timestamp": "2026-05-16 20:00:00",
      "temperature": 25.5,
      "humidity": 60.0,
      "position": 50,
      "limit_sw": 0
    }
  ]
}
```

## 7. 管理员接口

### 用户列表

```
GET /api/admin/users
Header: Authorization: Bearer <admin_token>

响应:
{
  "users": [
    {
      "id": 1,
      "username": "admin",
      "is_admin": true,
      "is_active": true,
      "created_at": "2026-05-16 19:33:31"
    }
  ]
}
```

### 创建用户

```
POST /api/admin/create-user
Header: Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "username": "test",
  "password": "test123",
  "is_admin": false
}
```

### 其他管理接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/admin/users/{id}` | DELETE | 删除用户 |
| `/api/admin/users/{id}/toggle-active` | PUT | 启用/禁用 |
| `/api/admin/users/{id}/change-password` | PUT | 改密码 |

## 8. 默认账号

| 账号 | 密码 | 角色 |
|------|------|------|
| admin | admin123 | 管理员 |

首次启动自动创建。

## 9. App 端修改清单

### 必须修改

1. **服务器地址**：支持配置为 `http://IP:8000` 或 `https://xxx.cpolar.top`
2. **认证方式**：登录接口改为 `POST /api/login`，返回 JWT token
3. **请求头**：所有 API 请求头改为 `Authorization: Bearer <JWT token>`
4. **设备查询**：改为 `GET /thingmodel/query-device-property`
5. **设备控制**：改为 `POST /thingmodel/set-device-property`

### 可选新增

6. **AI 检测**：`GET /api/ai/detection` 显示行人/车牌检测结果
7. **传感器历史**：`GET /api/sensor-data` 显示温湿度曲线
8. **视频流**：通过 WebSocket `ws://IP:8765` 接收带检测框的视频帧

### 不需要修改

- 登录请求/响应格式（兼容）
- 设备查询/控制的请求体格式（兼容）
- 数据解析逻辑（兼容 OneNET 格式）

## 10. 错误码

| HTTP 状态码 | 说明 |
|-------------|------|
| 200 | 成功 |
| 400 | 参数错误 |
| 401 | 未认证 / Token 过期 / 密码错误 |
| 403 | 权限不足（非管理员） |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
| 503 | MQTT 服务未就绪 |

## 11. 视频流（海康威视实时画面）

### MJPEG 实时视频流

```
GET /video/stream

无需认证，直接在浏览器或 WebView 加载。
```

**App 端使用**：
- Android WebView 加载 URL 即可显示
- iOS WKWebView 同样支持
- 局域网：`http://192.168.0.100:8000/video/stream`
- 外网：`https://xxxxxx.cpolar.top/video/stream`

**特点**：
- 带行人检测框（绿色）+ 车牌检测框（红色）叠加
- ~10fps，JPEG 质量 70%，带宽约 1-2Mbps
- 标准 MJPEG 格式，兼容所有平台

### JPEG 快照

```
GET /video/snapshot

返回当前帧的 JPEG 图片。
```

可用于 App 端截图或定时刷新显示单帧。

### App 端集成方式

**方式 1：WebView（推荐）**
```java
// Android
WebView webView = findViewById(R.id.webView);
webView.getSettings().setLoadWithOverviewMode(true);
webView.loadUrl("http://192.168.0.100:8000/video/stream");
```

```swift
// iOS
let webView = WKWebView()
let url = URL(string: "http://192.168.0.100:8000/video/stream")
webView.load(URLRequest(url: url!))
```

**方式 2：ImageView 定时刷新快照**
```java
// 每 200ms 刷新一张快照
Handler handler = new Handler();
Runnable refresh = new Runnable() {
    public void run() {
        imageView.setImageUrl("http://IP:8000/video/snapshot");
        handler.postDelayed(this, 200);
    }
};
handler.post(refresh);
```

## 12. API 文档

浏览器打开 `http://<RK3568-IP>:8000/docs` 查看完整的 Swagger 交互式文档。
