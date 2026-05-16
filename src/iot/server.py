"""FastAPI 智能家居服务器 - 替代 OneNET + 云服务器

功能：
1. 用户认证（JWT），复用现有后端逻辑
2. 设备状态查询（替代 OneNET query-device-property）
3. 设备控制（替代 OneNET set-device-property）
4. 历史传感器数据
5. AI 视觉检测结果
"""

import os
import time
import json
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
import hashlib

from src.utils.logger import setup_logger

logger = setup_logger("iot_server")

# ── 配置 ──────────────────────────────────────────────

JWT_SECRET = "rk3568_smart_home_secret_key_2026"
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 168  # 7 天

# ── SQLite 数据库 ─────────────────────────────────────

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "smart_home.db")


def _init_db():
    """初始化数据库"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 用户表
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # 传感器历史数据表
    c.execute("""CREATE TABLE IF NOT EXISTS sensor_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        temperature REAL,
        humidity REAL,
        position INTEGER,
        limit_sw INTEGER
    )""")

    # AI 检测事件表
    c.execute("""CREATE TABLE IF NOT EXISTS ai_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        event_type TEXT,
        details TEXT
    )""")

    # 创建默认管理员（密码: admin123）
    c.execute("SELECT COUNT(*) FROM users WHERE username='admin'")
    if c.fetchone()[0] == 0:
        admin_hash = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute("INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, 1)",
                  ("admin", admin_hash))
        logger.info("默认管理员已创建: admin / admin123")

    conn.commit()
    conn.close()


def _get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── JWT 工具 ──────────────────────────────────────────

def _create_token(username: str, is_admin: bool) -> str:
    payload = {
        "username": username,
        "is_admin": is_admin,
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def _verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token 已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token 无效")


# ── FastAPI 应用 ──────────────────────────────────────

app = FastAPI(title="RK3568 智能家居服务器", version="1.0.0")

# CORS（允许 App 跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)

# 全局 MQTT 客户端引用（由 main.py 注入）
_mqtt_client = None
# 全局 AI 检测结果引用
_ai_results = {"persons": None, "plates": None}


def set_mqtt_client(client):
    """注入 MQTT 客户端"""
    global _mqtt_client
    _mqtt_client = client


def set_ai_results(persons, plates):
    """更新 AI 检测结果"""
    global _ai_results
    _ai_results = {"persons": persons, "plates": plates}


def _get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """从 Token 获取当前用户"""
    if not credentials:
        raise HTTPException(status_code=401, detail="未提供认证信息")
    return _verify_token(credentials.credentials)


# ── 请求/响应模型 ─────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str

class ControlRequest(BaseModel):
    product_id: str = "0g0k8iPR77"    # 兼容 App（忽略）
    device_name: str = "esp8266"
    params: dict

class CreateUserRequest(BaseModel):
    username: str
    password: str
    is_admin: bool = False

class ChangePasswordRequest(BaseModel):
    new_password: str


# ── API 路由 ──────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "service": "RK3568 智能家居服务器",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "mqtt_connected": _mqtt_client.is_connected if _mqtt_client else False,
        "timestamp": time.time(),
    }


# ── 认证 API（兼容原有 App） ─────────────────────────

@app.post("/api/login")
async def login(req: LoginRequest):
    """用户登录"""
    conn = _get_db()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE username=? AND is_active=1",
            (req.username,)
        ).fetchone()

        if not row:
            raise HTTPException(status_code=401, detail="用户名或密码错误")

        password_hash = hashlib.sha256(req.password.encode()).hexdigest()
        if row["password_hash"] != password_hash:
            raise HTTPException(status_code=401, detail="用户名或密码错误")

        token = _create_token(row["username"], bool(row["is_admin"]))
        return {
            "success": True,
            "message": "登录成功",
            "token": token,
            "username": row["username"],
            "is_admin": bool(row["is_admin"]),
        }
    finally:
        conn.close()


@app.post("/api/verify-token")
async def verify_token(user: dict = Depends(_get_current_user)):
    return {"valid": True, "username": user["username"]}


# ── 管理员 API（兼容原有 App） ─────────────────────────

def _require_admin(user: dict = Depends(_get_current_user)):
    """要求管理员权限"""
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user


@app.post("/api/admin/create-user")
async def admin_create_user(req: CreateUserRequest, admin: dict = Depends(_require_admin)):
    """管理员创建用户"""
    conn = _get_db()
    try:
        existing = conn.execute("SELECT id FROM users WHERE username=?", (req.username,)).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="用户名已存在")

        password_hash = hashlib.sha256(req.password.encode()).hexdigest()
        conn.execute(
            "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
            (req.username, password_hash, 1 if req.is_admin else 0),
        )
        conn.commit()
        return {"success": True, "message": f"用户 {req.username} 创建成功"}
    finally:
        conn.close()


@app.get("/api/admin/users")
async def admin_list_users(admin: dict = Depends(_require_admin)):
    """管理员获取用户列表"""
    conn = _get_db()
    try:
        rows = conn.execute(
            "SELECT id, username, is_admin, is_active, created_at FROM users ORDER BY id"
        ).fetchall()
        return {
            "users": [
                {
                    "id": r["id"],
                    "username": r["username"],
                    "is_admin": bool(r["is_admin"]),
                    "is_active": bool(r["is_active"]),
                    "created_at": r["created_at"],
                }
                for r in rows
            ]
        }
    finally:
        conn.close()


@app.delete("/api/admin/users/{user_id}")
async def admin_delete_user(user_id: int, admin: dict = Depends(_require_admin)):
    """管理员删除用户"""
    conn = _get_db()
    try:
        row = conn.execute("SELECT username, is_admin FROM users WHERE id=?", (user_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="用户不存在")
        if row["is_admin"]:
            raise HTTPException(status_code=400, detail="不能删除管理员账户")
        conn.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()
        return {"success": True, "message": f"用户 {row['username']} 已删除"}
    finally:
        conn.close()


@app.put("/api/admin/users/{user_id}/toggle-active")
async def admin_toggle_active(user_id: int, admin: dict = Depends(_require_admin)):
    """管理员启用/禁用用户"""
    conn = _get_db()
    try:
        row = conn.execute("SELECT username, is_admin, is_active FROM users WHERE id=?", (user_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="用户不存在")
        if row["is_admin"]:
            raise HTTPException(status_code=400, detail="不能禁用管理员账户")
        new_status = 0 if row["is_active"] else 1
        conn.execute("UPDATE users SET is_active=? WHERE id=?", (new_status, user_id))
        conn.commit()
        status_text = "启用" if new_status else "禁用"
        return {"success": True, "message": f"用户 {row['username']} 已{status_text}"}
    finally:
        conn.close()


@app.put("/api/admin/users/{user_id}/change-password")
async def admin_change_password(user_id: int, req: ChangePasswordRequest, admin: dict = Depends(_require_admin)):
    """管理员修改用户密码"""
    conn = _get_db()
    try:
        row = conn.execute("SELECT username FROM users WHERE id=?", (user_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="用户不存在")
        password_hash = hashlib.sha256(req.new_password.encode()).hexdigest()
        conn.execute("UPDATE users SET password_hash=? WHERE id=?", (password_hash, user_id))
        conn.commit()
        return {"success": True, "message": f"用户 {row['username']} 密码已修改"}
    finally:
        conn.close()


# ── 设备状态 API（替代 OneNET query-device-property）───

@app.get("/thingmodel/query-device-property")
async def query_device_property(
    product_id: str = "0g0k8iPR77",
    device_name: str = "esp8266",
    user: dict = Depends(_get_current_user),
):
    """查询设备最新属性（替代 OneNET HTTP API，App 直接调用）"""
    if not _mqtt_client:
        raise HTTPException(status_code=503, detail="MQTT 服务未就绪")

    status = _mqtt_client.get_device_status()
    return status


# ── 设备控制 API（替代 OneNET set-device-property）────

@app.post("/thingmodel/set-device-property")
async def set_device_property(
    req: ControlRequest,
    user: dict = Depends(_get_current_user),
):
    """设置设备属性（替代 OneNET HTTP API，App 直接调用）"""
    if not _mqtt_client:
        raise HTTPException(status_code=503, detail="MQTT 服务未就绪")

    success = _mqtt_client.send_control(req.device_name, req.params)
    if success:
        return {"code": 0, "msg": "success"}
    else:
        raise HTTPException(status_code=500, detail="命令发送失败")


# ── 传感器历史数据 API ────────────────────────────────

@app.get("/api/sensor-data")
async def get_sensor_data(
    hours: int = 24,
    user: dict = Depends(_get_current_user),
):
    """获取历史传感器数据"""
    conn = _get_db()
    try:
        since = (datetime.now() - timedelta(hours=hours)).isoformat()
        rows = conn.execute(
            "SELECT * FROM sensor_history WHERE timestamp>? ORDER BY timestamp",
            (since,)
        ).fetchall()

        return {
            "hours": hours,
            "count": len(rows),
            "data": [dict(r) for r in rows],
        }
    finally:
        conn.close()


# ── AI 视觉数据 API ──────────────────────────────────

@app.get("/api/ai/detection")
async def get_ai_detection(user: dict = Depends(_get_current_user)):
    """获取 AI 视觉检测结果"""
    return _ai_results


# ── 数据采集定时任务 ──────────────────────────────────

def collect_sensor_data():
    """定时采集传感器数据（从 MQTT 缓存写入 SQLite）"""
    if not _mqtt_client:
        return

    status = _mqtt_client.get_device_status()
    data = {item["identifier"]: item["value"] for item in status.get("data", [])}

    if not data:
        return

    try:
        conn = _get_db()
        conn.execute(
            "INSERT INTO sensor_history (temperature, humidity, position, limit_sw) VALUES (?,?,?,?)",
            (
                float(data.get("tremp", 0)),
                float(data.get("hum", 0)),
                int(data.get("position", 0)),
                int(data.get("limit_sw", 0)),
            )
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"传感器数据采集失败: {e}")


# ── 启动服务 ──────────────────────────────────────────

def run_server(host: str = "0.0.0.0", port: int = 8000):
    """启动 FastAPI 服务（在独立线程中运行）"""
    import uvicorn
    _init_db()
    logger.info(f"智能家居服务器启动: http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="warning")