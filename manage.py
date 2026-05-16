#!/usr/bin/env python3
"""用户管理 CLI 工具

用法:
    python manage.py create-admin <username> <password>
    python manage.py create-user <username> <password>
    python manage.py list-users
    python manage.py delete-user <username>
    python manage.py change-password <username> <new_password>
    python manage.py toggle-active <username>
"""

import os
import sys
import sqlite3
import hashlib

# 将项目根目录添加到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "smart_home.db")


def get_db():
    """获取数据库连接"""
    if not os.path.exists(DB_PATH):
        print(f"❌ 数据库不存在: {DB_PATH}")
        print("   请先启动系统一次（会自动创建数据库）")
        sys.exit(1)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def create_admin(username: str, password: str):
    """创建管理员"""
    conn = get_db()
    try:
        existing = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
        if existing:
            print(f"❌ 用户名 '{username}' 已存在")
            return
        conn.execute(
            "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, 1)",
            (username, hash_password(password)),
        )
        conn.commit()
        print(f"✅ 管理员 '{username}' 创建成功")
    finally:
        conn.close()


def create_user(username: str, password: str):
    """创建普通用户"""
    conn = get_db()
    try:
        existing = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
        if existing:
            print(f"❌ 用户名 '{username}' 已存在")
            return
        conn.execute(
            "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, 0)",
            (username, hash_password(password)),
        )
        conn.commit()
        print(f"✅ 用户 '{username}' 创建成功")
    finally:
        conn.close()


def list_users():
    """列出所有用户"""
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT id, username, is_admin, is_active, created_at FROM users ORDER BY id"
        ).fetchall()

        if not rows:
            print("没有用户")
            return

        print(f"{'ID':<5} {'用户名':<15} {'角色':<10} {'状态':<8} {'创建时间'}")
        print("-" * 60)
        for r in rows:
            role = "管理员" if r["is_admin"] else "普通用户"
            status = "启用" if r["is_active"] else "禁用"
            print(f"{r['id']:<5} {r['username']:<15} {role:<10} {status:<8} {r['created_at']}")
    finally:
        conn.close()


def delete_user(username: str):
    """删除用户"""
    conn = get_db()
    try:
        row = conn.execute("SELECT id, is_admin FROM users WHERE username=?", (username,)).fetchone()
        if not row:
            print(f"❌ 用户 '{username}' 不存在")
            return
        if row["is_admin"]:
            print(f"❌ 不能删除管理员账户 '{username}'")
            return
        conn.execute("DELETE FROM users WHERE username=?", (username,))
        conn.commit()
        print(f"✅ 用户 '{username}' 已删除")
    finally:
        conn.close()


def change_password(username: str, new_password: str):
    """修改密码"""
    conn = get_db()
    try:
        row = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
        if not row:
            print(f"❌ 用户 '{username}' 不存在")
            return
        conn.execute(
            "UPDATE users SET password_hash=? WHERE username=?",
            (hash_password(new_password), username),
        )
        conn.commit()
        print(f"✅ 用户 '{username}' 密码已修改")
    finally:
        conn.close()


def toggle_active(username: str):
    """启用/禁用用户"""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT id, is_admin, is_active FROM users WHERE username=?", (username,)
        ).fetchone()
        if not row:
            print(f"❌ 用户 '{username}' 不存在")
            return
        if row["is_admin"]:
            print(f"❌ 不能禁用管理员账户 '{username}'")
            return
        new_status = 0 if row["is_active"] else 1
        conn.execute("UPDATE users SET is_active=? WHERE username=?", (new_status, username))
        conn.commit()
        status_text = "启用" if new_status else "禁用"
        print(f"✅ 用户 '{username}' 已{status_text}")
    finally:
        conn.close()


def print_help():
    print(__doc__)


def main():
    if len(sys.argv) < 2:
        print_help()
        return

    cmd = sys.argv[1]

    if cmd == "create-admin" and len(sys.argv) >= 4:
        create_admin(sys.argv[2], sys.argv[3])
    elif cmd == "create-user" and len(sys.argv) >= 4:
        create_user(sys.argv[2], sys.argv[3])
    elif cmd == "list-users":
        list_users()
    elif cmd == "delete-user" and len(sys.argv) >= 3:
        delete_user(sys.argv[2])
    elif cmd == "change-password" and len(sys.argv) >= 4:
        change_password(sys.argv[2], sys.argv[3])
    elif cmd == "toggle-active" and len(sys.argv) >= 3:
        toggle_active(sys.argv[2])
    else:
        print_help()


if __name__ == "__main__":
    main()