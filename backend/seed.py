"""初始化种子数据。"""

from database import get_connection

SEED_DATA = [
    {
        "location": "北京钟楼",
        "source_type": "古钟",
        "audible_time_period": "06:00-07:00, 12:00-13:00",
        "direction": "东南",
        "notes": "晨间与午间整点报时，风大时传播更远",
    },
    {
        "location": "上海外滩海关大楼",
        "source_type": "电子钟",
        "audible_time_period": "整点全天",
        "direction": "东",
        "notes": "江面反射，对岸可闻",
    },
    {
        "location": "西安鼓楼",
        "source_type": "鼓声",
        "audible_time_period": "19:00-21:00",
        "direction": "西北",
        "notes": "傍晚游客区，背景噪声较高",
    },
    {
        "location": "苏州寒山寺",
        "source_type": "古钟",
        "audible_time_period": "04:00-05:00",
        "direction": "南",
        "notes": "清晨钟声，需避开施工时段采样",
    },
    {
        "location": "广州陈家祠",
        "source_type": "电子钟",
        "audible_time_period": "08:00-18:00",
        "direction": "西南",
        "notes": "工作日与周末可听时段略有差异",
    },
]


def seed_if_empty() -> None:
    """表为空时写入 5 条种子数据。"""
    conn = get_connection()
    try:
        row = conn.execute("SELECT COUNT(*) AS cnt FROM sampling_points").fetchone()
        if row and row["cnt"] > 0:
            return
        conn.executemany(
            """
            INSERT INTO sampling_points
                (location, source_type, audible_time_period, direction, notes)
            VALUES
                (:location, :source_type, :audible_time_period, :direction, :notes)
            """,
            SEED_DATA,
        )
        conn.commit()
    finally:
        conn.close()
