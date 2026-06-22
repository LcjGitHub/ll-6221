"""Pydantic 请求/响应模型。"""

from pydantic import BaseModel, Field


class SamplingPointBase(BaseModel):
    """采样点公共字段。"""

    location: str = Field(..., min_length=1, description="地点")
    source_type: str = Field(..., min_length=1, description="声源类型")
    audible_time_period: str = Field(..., min_length=1, description="可听时间段")
    direction: str = Field(..., min_length=1, description="方向")
    notes: str = Field(default="", description="备注")


class SamplingPointCreate(SamplingPointBase):
    """创建采样点。"""


class SamplingPointUpdate(SamplingPointBase):
    """更新采样点。"""


class SamplingPoint(SamplingPointBase):
    """采样点响应。"""

    id: int

    model_config = {"from_attributes": True}
