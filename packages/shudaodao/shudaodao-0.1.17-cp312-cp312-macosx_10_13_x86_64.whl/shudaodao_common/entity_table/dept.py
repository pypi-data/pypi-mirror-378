#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @License  ：(C)Copyright 2025, 数道智融科技
# @Author   ：李锋
# @Software ：PyCharm
# @Date     ：2025/8/29 上午2:13
# @Desc     ：

from typing import Optional

from sqlmodel import SQLModel, Field

from shudaodao_core import get_primary_id


class DeptBase(SQLModel):
    dept_id: Optional[int] = Field(default_factory=get_primary_id, primary_key=True)
    dept_name: str = Field(max_length=100, description="部门名称")


class Dept(DeptBase, table=True):
    __tablename__ = "t_dept"
    __table_args__ = {"schema": "shudao_acm", "comment": "部门表"}


class DeptCreate(DeptBase):
    ...


class DeptResponse(DeptBase):
    ...


class DeptUpdate(DeptBase):
    ...
