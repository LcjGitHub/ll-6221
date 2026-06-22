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


class SamplingRecordBase(BaseModel):
    """采样记录公共字段。"""

    point_id: int = Field(..., gt=0, description="关联采样点编号")
    sampling_date: str = Field(..., min_length=1, description="采样日期")
    actual_chime_time: str = Field(..., min_length=1, description="实际听到报时的时间")
    noise_level: str = Field(..., min_length=1, description="环境噪声等级")
    sampler_name: str = Field(..., min_length=1, description="采样员姓名")
    description: str = Field(default="", description="说明文字")


class SamplingRecordCreate(SamplingRecordBase):
    """创建采样记录。"""


class SamplingRecordUpdate(SamplingRecordBase):
    """更新采样记录。"""


class SamplingRecord(SamplingRecordBase):
    """采样记录响应。"""

    id: int

    model_config = {"from_attributes": True}
