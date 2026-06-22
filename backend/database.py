"""SQLite 数据库连接与初始化。"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "data" / "chime.db"


def get_connection() -> sqlite3.Connection:
    """获取 SQLite 连接，启用 Row 工厂便于按列名访问。"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """创建采样点表（若不存在）。"""
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sampling_points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT NOT NULL,
                source_type TEXT NOT NULL,
                audible_time_period TEXT NOT NULL,
                direction TEXT NOT NULL,
                notes TEXT DEFAULT ''
            )
            """
        )
        conn.commit()
    finally:
        conn.close()
