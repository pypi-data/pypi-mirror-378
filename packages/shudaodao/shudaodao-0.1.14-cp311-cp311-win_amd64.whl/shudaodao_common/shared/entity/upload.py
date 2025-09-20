#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @License  ：(C)Copyright 2025, 数道智融科技
# @Author   ：李锋
# @Software ：PyCharm
# @Date     ：2025/8/27 上午1:29
# @Desc     ：


from pydantic import BaseModel, Field


class UploadFileModel(BaseModel):
    name: str = Field(..., description="文件名")
    size: int = Field(None, description="文件大小")
    upload_time: str = Field(None, description="上传时间")
