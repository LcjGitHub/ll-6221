"""城市报时声采样点 API。"""

import csv
import io
from typing import Optional

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from database import get_connection, init_db
from schemas import (
    ImportResult,
    SamplingPoint,
    SamplingPointCreate,
    SamplingPointUpdate,
    SamplingRecord,
    SamplingRecordCreate,
    SamplingRecordUpdate,
    SourceType,
    SourceTypeCreate,
    Statistics,
)
from seed import seed_if_empty, seed_source_types_if_empty

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


def row_to_record(row) -> SamplingRecord:
    """将 SQLite Row 转为 SamplingRecord 模型。"""
    return SamplingRecord(
        id=row["id"],
        point_id=row["point_id"],
        sampling_date=row["sampling_date"],
        actual_chime_time=row["actual_chime_time"],
        noise_level=row["noise_level"],
        sampler_name=row["sampler_name"],
        description=row["description"] or "",
    )


@app.on_event("startup")
def on_startup() -> None:
    """启动时初始化数据库并写入种子数据。"""
    init_db()
    seed_source_types_if_empty()
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


@app.get("/api/sampling-points/export")
def export_sampling_points() -> StreamingResponse:
    """导出全部采样点为 CSV 文件。"""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT location, source_type, audible_time_period, direction, notes FROM sampling_points ORDER BY id ASC"
        ).fetchall()

        output = io.StringIO()
        output.write("\ufeff")
        writer = csv.writer(output)
        writer.writerow(["地点", "声源类型", "可听时间段", "方向", "备注"])
        for row in rows:
            writer.writerow([
                row["location"],
                row["source_type"],
                row["audible_time_period"],
                row["direction"],
                row["notes"],
            ])

        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": "attachment; filename=sampling_points.csv"
            },
        )
    finally:
        conn.close()


@app.post("/api/sampling-points/import", response_model=ImportResult)
def import_sampling_points(file: UploadFile = File(...)) -> ImportResult:
    """批量导入采样点，跳过地点重复的条目。"""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="仅支持 CSV 文件")

    content = file.file.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))

    field_mapping = {
        "地点": "location",
        "声源类型": "source_type",
        "可听时间段": "audible_time_period",
        "方向": "direction",
        "备注": "notes",
    }

    headers = reader.fieldnames or []
    missing_fields = [cn for cn in field_mapping if cn not in headers]
    if missing_fields:
        raise HTTPException(
            status_code=400,
            detail=f"CSV 缺少必要列：{', '.join(missing_fields)}",
        )

    conn = get_connection()
    try:
        total_count = 0
        success_count = 0
        skip_count = 0
        failed_count = 0
        errors: list[str] = []

        for idx, row in enumerate(reader, start=2):
            total_count += 1
            location = (row.get("地点") or "").strip()
            source_type = (row.get("声源类型") or "").strip()
            audible_time_period = (row.get("可听时间段") or "").strip()
            direction = (row.get("方向") or "").strip()
            notes = (row.get("备注") or "").strip()

            if not location:
                failed_count += 1
                errors.append(f"第 {idx} 行：地点不能为空")
                continue
            if not source_type:
                failed_count += 1
                errors.append(f"第 {idx} 行：声源类型不能为空")
                continue
            if not audible_time_period:
                failed_count += 1
                errors.append(f"第 {idx} 行：可听时间段不能为空")
                continue
            if not direction:
                failed_count += 1
                errors.append(f"第 {idx} 行：方向不能为空")
                continue

            existing = conn.execute(
                "SELECT id FROM sampling_points WHERE location = ?",
                (location,),
            ).fetchone()
            if existing is not None:
                skip_count += 1
                continue

            conn.execute(
                """
                INSERT INTO sampling_points
                    (location, source_type, audible_time_period, direction, notes)
                VALUES (?, ?, ?, ?, ?)
                """,
                (location, source_type, audible_time_period, direction, notes),
            )
            success_count += 1

        conn.commit()
        return ImportResult(
            total_count=total_count,
            success_count=success_count,
            skip_count=skip_count,
            failed_count=failed_count,
            errors=errors,
        )
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


@app.get("/api/sampling-records", response_model=list[SamplingRecord])
def list_sampling_records(
    point_id: Optional[int] = Query(default=None, description="按采样点编号筛选")
) -> list[SamplingRecord]:
    """获取采样记录列表，可按采样点筛选。"""
    conn = get_connection()
    try:
        if point_id is not None:
            rows = conn.execute(
                "SELECT * FROM sampling_records WHERE point_id = ? ORDER BY sampling_date DESC, id DESC",
                (point_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM sampling_records ORDER BY sampling_date DESC, id DESC"
            ).fetchall()
        return [row_to_record(row) for row in rows]
    finally:
        conn.close()


@app.get("/api/sampling-records/{record_id}", response_model=SamplingRecord)
def get_sampling_record(record_id: int) -> SamplingRecord:
    """获取单条采样记录。"""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM sampling_records WHERE id = ?", (record_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="采样记录不存在")
        return row_to_record(row)
    finally:
        conn.close()


@app.post("/api/sampling-records", response_model=SamplingRecord, status_code=201)
def create_sampling_record(payload: SamplingRecordCreate) -> SamplingRecord:
    """新建采样记录。"""
    conn = get_connection()
    try:
        point = conn.execute(
            "SELECT id FROM sampling_points WHERE id = ?", (payload.point_id,)
        ).fetchone()
        if point is None:
            raise HTTPException(status_code=400, detail="关联的采样点不存在")
        cursor = conn.execute(
            """
            INSERT INTO sampling_records
                (point_id, sampling_date, actual_chime_time, noise_level, sampler_name, description)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                payload.point_id,
                payload.sampling_date,
                payload.actual_chime_time,
                payload.noise_level,
                payload.sampler_name,
                payload.description,
            ),
        )
        conn.commit()
        return get_sampling_record(cursor.lastrowid)
    finally:
        conn.close()


@app.put("/api/sampling-records/{record_id}", response_model=SamplingRecord)
def update_sampling_record(
    record_id: int, payload: SamplingRecordUpdate
) -> SamplingRecord:
    """更新采样记录。"""
    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id FROM sampling_records WHERE id = ?", (record_id,)
        ).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="采样记录不存在")
        point = conn.execute(
            "SELECT id FROM sampling_points WHERE id = ?", (payload.point_id,)
        ).fetchone()
        if point is None:
            raise HTTPException(status_code=400, detail="关联的采样点不存在")
        conn.execute(
            """
            UPDATE sampling_records SET
                point_id = ?,
                sampling_date = ?,
                actual_chime_time = ?,
                noise_level = ?,
                sampler_name = ?,
                description = ?
            WHERE id = ?
            """,
            (
                payload.point_id,
                payload.sampling_date,
                payload.actual_chime_time,
                payload.noise_level,
                payload.sampler_name,
                payload.description,
                record_id,
            ),
        )
        conn.commit()
        return get_sampling_record(record_id)
    finally:
        conn.close()


@app.delete("/api/sampling-records/{record_id}", status_code=204)
def delete_sampling_record(record_id: int) -> None:
    """删除采样记录。"""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM sampling_records WHERE id = ?", (record_id,)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="采样记录不存在")
    finally:
        conn.close()


@app.get("/api/statistics", response_model=Statistics)
def get_statistics() -> Statistics:
    """获取统计汇总数据。"""
    conn = get_connection()
    try:
        total_rows = conn.execute(
            "SELECT COUNT(*) as cnt FROM sampling_points"
        ).fetchone()
        total_points = total_rows["cnt"]

        source_type_rows = conn.execute(
            "SELECT source_type, COUNT(*) as cnt FROM sampling_points GROUP BY source_type"
        ).fetchall()
        source_type_counts = {row["source_type"]: row["cnt"] for row in source_type_rows}

        direction_rows = conn.execute(
            "SELECT direction, COUNT(*) as cnt FROM sampling_points GROUP BY direction"
        ).fetchall()
        direction_counts = {row["direction"]: row["cnt"] for row in direction_rows}

        return Statistics(
            total_points=total_points,
            source_type_counts=source_type_counts,
            direction_counts=direction_counts,
        )
    finally:
        conn.close()


@app.get("/api/source-types", response_model=list[SourceType])
def list_source_types() -> list[SourceType]:
    """获取全部声源类型。"""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM source_types ORDER BY id ASC"
        ).fetchall()
        return [SourceType(id=row["id"], name=row["name"]) for row in rows]
    finally:
        conn.close()


@app.post("/api/source-types", response_model=SourceType, status_code=201)
def create_source_type(payload: SourceTypeCreate) -> SourceType:
    """新增声源类型。"""
    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id FROM source_types WHERE name = ?", (payload.name,)
        ).fetchone()
        if existing is not None:
            raise HTTPException(status_code=400, detail="声源类型已存在")
        cursor = conn.execute(
            "INSERT INTO source_types (name) VALUES (?)",
            (payload.name,),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM source_types WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return SourceType(id=row["id"], name=row["name"])
    finally:
        conn.close()


@app.delete("/api/source-types/{type_id}", status_code=204)
def delete_source_type(type_id: int) -> None:
    """删除声源类型。"""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM source_types WHERE id = ?", (type_id,)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="声源类型不存在")
    finally:
        conn.close()
