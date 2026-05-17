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
https://65ac6ab7.r7.cpolar.top
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
      "plate_number": "京A12345",
      "plate_color": "蓝"
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

## 11. 视频流 — Android 端详细集成指南

### 11.1 服务端接口

| 端点 | 格式 | 说明 |
|------|------|------|
| `GET /video/stream` | MJPEG 流 | 实时视频（带 AI 检测框），无需认证 |
| `GET /video/snapshot` | JPEG 图片 | 当前帧快照，无需认证 |

### 11.2 整体思路

```
┌──────────────────────────────────────────────────┐
│  Android App                                      │
│                                                    │
│  ┌──────────────────────────────────────────┐     │
│  │  Activity / Fragment                       │     │
│  │                                            │     │
│  │  ┌──────────────────────────────────┐     │     │
│  │  │  WebView / TextureView            │     │     │
│  │  │  显示 MJPEG 视频流                 │     │     │
│  │  └──────────────────────────────────┘     │     │
│  │                                            │     │
│  │  ┌─────┐  ┌─────┐  ┌──────────┐  ┌────┐ │     │
│  │  │温度 │  │湿度 │  │ 车牌号    │  │开灯│ │     │
│  │  │25.5°│  │ 60% │  │ 京A12345 │  │ 🔔 │ │     │
│  │  └─────┘  └─────┘  └──────────┘  └────┘ │     │
│  └──────────────────────────────────────────┘     │
│                                                    │
│  服务器地址: http://192.168.0.100:8000             │
│  视频流:    http://192.168.0.100:8000/video/stream │
└──────────────────────────────────────────────────┘
```

### 11.3 方案选择

| 方案 | 优点 | 缺点 | 推荐场景 |
|------|------|------|---------|
| WebView 加载 MJPEG | 最简单，几行代码 | 无法叠加自定义 UI | 快速集成 |
| MjpegInputStream 解码 | 可自定义画面、叠加 UI | 代码稍多 | 需要在视频上画控件 |
| ImageView 定时刷新快照 | 最省带宽 | 帧率低（~5fps） | 省流量模式 |

---

### 11.4 方案 A：WebView 加载（最简单）

#### XML 布局

```xml
<!-- res/layout/activity_video.xml -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <!-- 视频区域 -->
    <WebView
        android:id="@+id/videoWebView"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1" />

    <!-- 下方控制面板 -->
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal"
        android:padding="16dp">

        <Button android:id="@+id/btnLight"
            android:text="开灯"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content" />

        <Button android:id="@+id/btnRefresh"
            android:text="刷新视频"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content" />
    </LinearLayout>
</LinearLayout>
```

#### Activity 代码

```java
public class VideoActivity extends AppCompatActivity {

    private WebView videoWebView;
    private String serverUrl = "http://192.168.0.100:8000";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_video);

        videoWebView = findViewById(R.id.videoWebView);

        // WebView 设置
        WebSettings settings = videoWebView.getSettings();
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        settings.setBuiltInZoomControls(false);

        // 允许 HTTP（Android 9+ 默认禁止）
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            videoWebView.setMixedContentMode(
                WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
            );
        }

        // 加载视频流
        loadVideoStream();

        // 刷新按钮
        findViewById(R.id.btnRefresh).setOnClickListener(v -> loadVideoStream());
    }

    private void loadVideoStream() {
        String videoUrl = serverUrl + "/video/stream";
        videoWebView.loadUrl(videoUrl);
    }

    @Override
    protected void onPause() {
        super.onPause();
        // 页面不可见时停止视频流，节省流量
        videoWebView.loadUrl("about:blank");
    }

    @Override
    protected void onResume() {
        super.onResume();
        loadVideoStream();
    }
}
```

#### AndroidManifest.xml 权限

```xml
<uses-permission android:name="android.permission.INTERNET" />

<!-- Android 9+ 允许 HTTP 明文 -->
<application
    android:usesCleartextTraffic="true"
    ...>
```

---

### 11.5 方案 B：MJPEG 解码 + 自定义渲染（推荐）

适合需要在视频上叠加自定义控件（温度、车牌号浮层等）的场景。

#### MJPEG 解码工具类

```java
/**
 * MJPEG 流解码器
 * 从 HTTP 流中逐帧解析 JPEG 图片
 */
public class MjpegInputStream {
    private static final byte[] JPEG_START = {(byte) 0xFF, (byte) 0xD8};
    private static final byte[] JPEG_END   = {(byte) 0xFF, (byte) 0xD9};
    private static final String BOUNDARY = "--frame";

    private final InputStream inputStream;

    public MjpegInputStream(InputStream is) {
        this.inputStream = is;
    }

    /**
     * 读取下一帧 JPEG 图片
     * @return Bitmap 或 null（流结束）
     */
    public Bitmap readFrame() throws IOException {
        byte[] buffer = new byte[1024 * 256]; // 256KB 缓冲
        int length = 0;

        // 跳过 boundary 行
        boolean foundStart = false;
        while (true) {
            // 读取一行
            String line = readLine();
            if (line == null) return null;

            if (line.contains("Content-Type: image/jpeg")) {
                foundStart = true;
                continue;
            }
            if (foundStart && line.isEmpty()) {
                break; // 空行后面就是 JPEG 数据
            }
        }

        // 读取 JPEG 数据（从 FF D8 到 FF D9）
        boolean jpegStarted = false;
        int jpegLength = 0;
        int b;

        while ((b = inputStream.read()) != -1) {
            if (!jpegStarted) {
                if (b == (byte) 0xFF) {
                    int next = inputStream.read();
                    if (next == (byte) 0xD8) {
                        buffer[0] = (byte) 0xFF;
                        buffer[1] = (byte) 0xD8;
                        jpegLength = 2;
                        jpegStarted = true;
                    }
                }
            } else {
                buffer[jpegLength++] = (byte) b;
                // 检查 JPEG 结束标记 FF D9
                if (jpegLength >= 2 &&
                    buffer[jpegLength - 2] == (byte) 0xFF &&
                    buffer[jpegLength - 1] == (byte) 0xD9) {
                    break;
                }
            }
        }

        if (jpegLength <= 0) return null;

        byte[] jpegData = new byte[jpegLength];
        System.arraycopy(buffer, 0, jpegData, 0, jpegLength);
        return BitmapFactory.decodeByteArray(jpegData, 0, jpegLength);
    }

    private String readLine() throws IOException {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        int b;
        while ((b = inputStream.read()) != -1) {
            if (b == '\r') {
                inputStream.read(); // skip \n
                return baos.toString();
            }
            baos.write(b);
        }
        return null;
    }

    public void close() throws IOException {
        inputStream.close();
    }
}
```

#### MJPEG 读取线程

```java
public class MjpegThread extends Thread {
    public interface FrameCallback {
        void onFrame(Bitmap bitmap);
        void onError(String error);
    }

    private final String url;
    private final FrameCallback callback;
    private volatile boolean running = true;

    public MjpegThread(String url, FrameCallback callback) {
        this.url = url;
        this.callback = callback;
    }

    public void stopStream() {
        running = false;
    }

    @Override
    public void run() {
        while (running) {
            HttpURLConnection conn = null;
            try {
                URL videoUrl = new URL(url);
                conn = (HttpURLConnection) videoUrl.openConnection();
                conn.setReadTimeout(10000);
                conn.setConnectTimeout(5000);

                MjpegInputStream mjpeg = new MjpegInputStream(conn.getInputStream());

                while (running) {
                    Bitmap frame = mjpeg.readFrame();
                    if (frame == null) break;

                    callback.onFrame(frame);
                }

                mjpeg.close();
            } catch (Exception e) {
                if (running) {
                    callback.onError("连接失败: " + e.getMessage());
                    try { Thread.sleep(3000); } catch (InterruptedException ignored) {}
                }
            } finally {
                if (conn != null) conn.disconnect();
            }
        }
    }
}
```

#### Activity 使用

```java
public class VideoActivity extends AppCompatActivity {

    private ImageView videoView;
    private MjpegThread mjpegThread;
    private String serverUrl = "http://192.168.0.100:8000";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_video);

        videoView = findViewById(R.id.videoView);

        // 启动 MJPEG 流
        startVideoStream();
    }

    private void startVideoStream() {
        String videoUrl = serverUrl + "/video/stream";

        mjpegThread = new MjpegThread(videoUrl, new MjpegThread.FrameCallback() {
            @Override
            public void onFrame(Bitmap bitmap) {
                runOnUiThread(() -> {
                    // 回收旧 Bitmap 防止内存泄漏
                    Bitmap old = (Bitmap) videoView.getTag();
                    if (old != null && !old.isRecycled()) old.recycle();

                    videoView.setImageBitmap(bitmap);
                    videoView.setTag(bitmap);
                });
            }

            @Override
            public void onError(String error) {
                runOnUiThread(() ->
                    Toast.makeText(VideoActivity.this, error, Toast.LENGTH_SHORT).show()
                );
            }
        });

        mjpegThread.start();
    }

    @Override
    protected void onPause() {
        super.onPause();
        if (mjpegThread != null) mjpegThread.stopStream();
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (mjpegThread == null || !mjpegThread.isAlive()) {
            startVideoStream();
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (mjpegThread != null) mjpegThread.stopStream();
    }
}
```

#### 对应 XML 布局

```xml
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <!-- 视频画面 -->
    <ImageView
        android:id="@+id/videoView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:scaleType="centerCrop" />

    <!-- 叠加信息浮层 -->
    <LinearLayout
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="top|start"
        android:background="#80000000"
        android:orientation="vertical"
        android:padding="12dp">

        <TextView android:id="@+id/tvTemp"
            android:text="温度: --"
            android:textColor="@android:color/white"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content" />

        <TextView android:id="@+id/tvHum"
            android:text="湿度: --"
            android:textColor="@android:color/white"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content" />

        <TextView android:id="@+id/tvPlate"
            android:text="车牌: --"
            android:textColor="#FFD700"
            android:textStyle="bold"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content" />
    </LinearLayout>

    <!-- 控制按钮浮层 -->
    <LinearLayout
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="bottom|center_horizontal"
        android:padding="16dp">

        <Button android:id="@+id/btnLight"
            android:text="💡 开灯"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginEnd="8dp" />

        <Button android:id="@+id/btnDoor"
            android:text="🚪 开门"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content" />
    </LinearLayout>
</FrameLayout>
```

---

### 11.6 方案 C：快照定时刷新（省流量）

最低带宽方案，每 200ms 请求一张 JPEG 快照。

```java
public class SnapshotHelper {
    private final Handler handler = new Handler(Looper.getMainLooper());
    private final ImageView imageView;
    private final String snapshotUrl;
    private volatile boolean running;
    private int intervalMs = 200; // 200ms ≈ 5fps

    public SnapshotHelper(ImageView imageView, String serverUrl) {
        this.imageView = imageView;
        this.snapshotUrl = serverUrl + "/video/snapshot";
    }

    public void start() {
        running = true;
        handler.post(fetchRunnable);
    }

    public void stop() {
        running = false;
        handler.removeCallbacks(fetchRunnable);
    }

    public void setInterval(int ms) {
        this.intervalMs = ms;
    }

    private final Runnable fetchRunnable = new Runnable() {
        @Override
        public void run() {
            if (!running) return;

            new Thread(() -> {
                try {
                    URL url = new URL(snapshotUrl);
                    HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                    conn.setConnectTimeout(2000);
                    conn.setReadTimeout(2000);

                    Bitmap bitmap = BitmapFactory.decodeStream(conn.getInputStream());
                    conn.disconnect();

                    if (bitmap != null) {
                        handler.post(() -> {
                            Bitmap old = (Bitmap) imageView.getTag();
                            imageView.setImageBitmap(bitmap);
                            imageView.setTag(bitmap);
                            if (old != null && !old.isRecycled()) old.recycle();
                        });
                    }
                } catch (Exception ignored) {}

                if (running) {
                    handler.postDelayed(this, intervalMs);
                }
            }).start();
        }
    };
}
```

使用：
```java
SnapshotHelper snapshot = new SnapshotHelper(imageView, "http://192.168.0.100:8000");
snapshot.start();  // 开始刷新
snapshot.stop();   // 停止刷新
```

---

### 11.7 视频流注意事项

1. **生命周期管理**：`onPause` 停止视频流，`onResume` 恢复，避免后台浪费流量
2. **内存管理**：Bitmap 使用后必须 `recycle()`，否则会 OOM
3. **HTTP 明文**：Android 9+ 需配置 `android:usesCleartextTraffic="true"`
4. **外网访问**：cpolar 穿透后 URL 为 `https://xxx.cpolar.top/video/stream`
5. **自动重连**：MJPEG 断开后应有自动重连逻辑（方案 B 已内置）
6. **视频质量**：服务端 JPEG 质量 60%，分辨率 640x360，带宽约 0.5-1Mbps

## 12. API 文档

浏览器打开 `http://<RK3568-IP>:8000/docs` 查看完整的 Swagger 交互式文档。
