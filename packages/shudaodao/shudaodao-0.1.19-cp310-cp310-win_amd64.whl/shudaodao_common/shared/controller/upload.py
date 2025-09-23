#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @License  ：(C)Copyright 2025, 数道智融科技
# @Author   ：李锋
# @Software ：PyCharm
# @Date     ：2025/7/7 下午8:32
# @Desc     ：

from typing import List

from fastapi import UploadFile, File

from shudaodao_core import AuthRouter
from ..entity.upload import UploadFileModel
from ..service.upload import UploadService

Upload_Router = AuthRouter(
    prefix="/v1/files",
    tags=["通用功能"]
)


# 获取目录下所有文件列表
@Upload_Router.get("/{path_name}")
async def get_files(path_name: str):
    return UploadService(path_name).list_files()


# 多文件上传到目录
@Upload_Router.post("/{path_name}")
async def upload(path_name: str, files: List[UploadFile] = File(...), ):
    return await UploadService(path_name).save_files(files)


# 删除多文件
@Upload_Router.delete("/{path_name}")
async def delete_file(path_name: str, files: list[UploadFileModel]):
    return await UploadService(path_name).delete_files(files)
