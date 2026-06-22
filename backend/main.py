"""城市报时声采样点 API。"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from database import get_connection, init_db
from schemas import SamplingPoint, SamplingPointCreate, SamplingPointUpdate
from seed import seed_if_empty

app = FastAPI(title="城市报时声采样点 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5101", "http://127.0.0.1:5101"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def row_to_point(row) -> SamplingPoint:
    """将 SQLite Row 转为 Pydantic 模型。"""
    return SamplingPoint(
        id=row["id"],
        location=row["location"],
        source_type=row["source_type"],
        audible_time_period=row["audible_time_period"],
        direction=row["direction"],
        notes=row["notes"] or "",
    )


@app.on_event("startup")
def on_startup() -> None:
    """启动时初始化数据库并写入种子数据。"""
    init_db()
    seed_if_empty()


@app.get("/api/health")
def health() -> dict:
    """健康检查。"""
    return {"status": "ok"}


@app.get("/api/sampling-points", response_model=list[SamplingPoint])
def list_sampling_points() -> list[SamplingPoint]:
    """获取全部采样点。"""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM sampling_points ORDER BY id ASC"
        ).fetchall()
        return [row_to_point(row) for row in rows]
    finally:
        conn.close()


@app.get("/api/sampling-points/{point_id}", response_model=SamplingPoint)
def get_sampling_point(point_id: int) -> SamplingPoint:
    """获取单个采样点。"""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM sampling_points WHERE id = ?", (point_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="采样点不存在")
        return row_to_point(row)
    finally:
        conn.close()


@app.post("/api/sampling-points", response_model=SamplingPoint, status_code=201)
def create_sampling_point(payload: SamplingPointCreate) -> SamplingPoint:
    """新建采样点。"""
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO sampling_points
                (location, source_type, audible_time_period, direction, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                payload.location,
                payload.source_type,
                payload.audible_time_period,
                payload.direction,
                payload.notes,
            ),
        )
        conn.commit()
        return get_sampling_point(cursor.lastrowid)
    finally:
        conn.close()


@app.put("/api/sampling-points/{point_id}", response_model=SamplingPoint)
def update_sampling_point(
    point_id: int, payload: SamplingPointUpdate
) -> SamplingPoint:
    """更新采样点。"""
    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id FROM sampling_points WHERE id = ?", (point_id,)
        ).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="采样点不存在")
        conn.execute(
            """
            UPDATE sampling_points SET
                location = ?,
                source_type = ?,
                audible_time_period = ?,
                direction = ?,
                notes = ?
            WHERE id = ?
            """,
            (
                payload.location,
                payload.source_type,
                payload.audible_time_period,
                payload.direction,
                payload.notes,
                point_id,
            ),
        )
        conn.commit()
        return get_sampling_point(point_id)
    finally:
        conn.close()


@app.delete("/api/sampling-points/{point_id}", status_code=204)
def delete_sampling_point(point_id: int) -> None:
    """删除采样点。"""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM sampling_points WHERE id = ?", (point_id,)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="采样点不存在")
    finally:
        conn.close()
