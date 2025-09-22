#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @License  ：(C)Copyright 2025, 数道智融科技
# @Author   ：李锋
# @Software ：PyCharm
# @Date     ：2025/8/18 下午7:43
# @Desc     ：

from typing import Optional, Any

from pydantic import BaseModel


class BaseResponse(BaseModel):
    success: bool = True
    code: int = 200
    name: Optional[str] = None
    message: str = ""


class DataResponse(BaseResponse):
    data: Optional[Any] = None


class ErrorResponse(BaseResponse):
    error: Optional[Any] = None
