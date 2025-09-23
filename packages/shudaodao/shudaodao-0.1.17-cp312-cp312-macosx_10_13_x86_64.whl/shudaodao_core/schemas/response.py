#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @License  ：(C)Copyright 2025, 数道智融科技
# @Author   ：李锋
# @Software ：PyCharm
# @Date     ：2025/8/18 下午7:43
# @Desc     ：

from typing import Any, Dict
from typing import Optional

from pydantic import Field, BaseModel
from sqlalchemy import BigInteger
from sqlmodel import SQLModel


class BaseResponse(SQLModel):
    """
    自动将所有 sa_type=BigInteger 的字段，在 model_dump() 时转为字符串。
    支持嵌套模型递归转换。
    不新增字段，直接原地替换值类型。
    """

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        # 先获取原始 dump 结果（不包含嵌套模型的转换）
        data = super().model_dump(*args, **kwargs)

        # 遍历所有字段定义
        for field_name, field_info in self.model_fields.items():
            # value = data.get(field_name)  # 从原始数据字典获取 无法进行实例判断
            value = getattr(self, field_name)  # 从模型实例获取 才能判断类型
            # 情况1: 该字段是 sa_type=BigInteger → 转为字符串
            if hasattr(field_info, 'sa_type') and field_info.sa_type is BigInteger:
                if value is not None:
                    data[field_name] = str(value)

            # 情况2: 该字段值是 BaseReadModel 的实例 → 递归转换
            elif isinstance(value, BaseResponse):
                data[field_name] = value.model_dump(*args, **kwargs)

            # 情况3: 该字段是列表，且元素是 BaseReadModel → 递归转换每个元素
            # 查询接口已经处理过了

        return data

    # 兼容 Pydantic v1 / jsonable_encoder
    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        return self.model_dump(*args, **kwargs)


class DataResponse(BaseResponse):
    success: bool = True
    code: int = Field(200, description="Response code")
    name: Optional[str] = None
    message: str = ""
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    success: bool = True
    code: int = Field(..., description="Response code")
    name: Optional[str] = None
    message: str = ""
    error: Optional[Any] = None
