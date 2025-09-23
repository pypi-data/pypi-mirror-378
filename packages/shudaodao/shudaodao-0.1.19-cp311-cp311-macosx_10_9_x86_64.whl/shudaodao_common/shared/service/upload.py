#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @License  ：(C)Copyright 2025, 数道智融科技
# @Author   ：李锋
# @Software ：PyCharm
# @Date     ：2025/7/9 下午3:02
# @Desc     ：

import os
from datetime import datetime
from typing import List

from fastapi import UploadFile, File, HTTPException

from shudaodao_core import logging, CoreUtil, DiskEngine
from ..entity.upload import UploadFileModel


class UploadService:
    def __init__(self, path_name: str, disk_name: str = "Upload"):
        self._disk_name = disk_name
        self._path_name = path_name
        self._storage = DiskEngine()

    def get_file_path(self, file_name: str):
        # 目录
        storage_path = self._storage.get_path(self._disk_name, self._path_name)
        # 文件
        file_path = storage_path / file_name
        # 存在
        if os.path.exists(file_path):
            return file_path
        # 不存在
        return None

    def list_files(self):  # -> List[UploadFileModel]:
        files_info = []
        # 目录
        storage_path = self._storage.get_path(self._disk_name, self._path_name)
        for file_name in os.listdir(storage_path):
            file_path = os.path.join(storage_path, file_name)
            # 跳过目录
            if not os.path.isfile(file_path):
                continue
            files_info.append(UploadFileModel(
                name=file_name,
                size=os.path.getsize(file_path),
                upload_time=datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
            ))
        # 按日期排序
        files_info = sorted(files_info, key=lambda s: s.upload_time)
        total_files = len(files_info)
        # raise HTTPException(status_code=400, detail="aaaa")
        return {
            "status": "success",
            "message": f"成功获取 {total_files} 个文件",
            "files": files_info,
            "total_files": total_files,
        }

    async def save_files(self, files: List[UploadFile] = File(...)):
        """上传到web路径的upload"""
        file_info = []
        # 目录
        storage_path = self._storage.get_path(self._disk_name, self._path_name)
        # 格式
        allowed_extensions = {"txt", "pdf", "docx", "md"}
        """保存上传文件"""
        for file in files:
            if not any(file.filename.endswith(ext) for ext in allowed_extensions):
                raise HTTPException(status_code=400,
                                    detail=f"不支持{os.path.splitext(file.filename)[1]}")
            # 文件
            file_path = os.path.join(storage_path, file.filename)
            if os.path.exists(file_path):
                CoreUtil.remove_path(file_path)
                logging.debug(f"删除文件 --> {file_path}")
            # 保存
            with open(file_path, "wb") as buffer:
                while content := await file.read(1024 * 1024):  # 每次读取1MB
                    buffer.write(content)

            file_info.append({
                "filename": file.filename,
            })
            logging.debug(f"保存文件 --> {file_path}")
        total_files = len(file_info)
        return {
            "status": "success",
            "message": f"成功上传 {total_files} 个文件",
            "files": file_info,
            "total_files": total_files,
        }

    async def delete_files(self, files: list[UploadFileModel]):
        file_info = []
        # 目录
        storage_path = self._storage.get_path(self._disk_name, self._path_name)

        for file in files:
            file_path = storage_path / file.name
            CoreUtil.remove_path(file_path)
            file_info.append({
                "filename": file.name
            })
            logging.debug(f"删除文件 --> {file_path}")
        total_files = len(file_info)
        return {
            "status": "success",
            "message": f"成功删除 {total_files} 个文件",
            "files": file_info,
            "total_files": total_files,
        }
