#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @License  ：(C)Copyright 2025, 数道智融科技
# @Author   ：李锋
# @Software ：PyCharm
# @Date     ：2025/8/29 下午3:57
# @Desc     ：

from typing import Optional

from sqlmodel import SQLModel, Field


class DeptUserBase(SQLModel):
    name: Optional[str]
    email: Optional[str]
    username: Optional[str]
    full_name: Optional[str]


class DeptUser(SQLModel, table=True):
    __tablename__ = 'v_dept_user'
    user_id: int = Field(primary_key=True)
