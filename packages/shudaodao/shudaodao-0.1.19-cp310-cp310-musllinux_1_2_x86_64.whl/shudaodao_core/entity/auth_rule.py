#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @License  ：(C)Copyright 2025, 数道智融科技
# @Author   ：李锋
# @Software ：PyCharm
# @Date     ：2025/9/17 上午11:06
# @Desc     ：

from typing import Optional

from sqlmodel import SQLModel, Field


class AuthRule(SQLModel, table=True):
    __tablename__ = "t_auth_rule"
    id: Optional[int] = Field(default=None, primary_key=True)
    ptype: Optional[str] = Field(max_length=32, alias="ptype")  # 代替 ptype，如 "p" 或 "g"
    v0: Optional[str] = Field(max_length=255)  # 代替 v0
    v1: Optional[str] = Field(max_length=255)  # 代替 v1
    v2: Optional[str] = Field(max_length=255)  # 代替 v2
    v3: Optional[str] = Field(max_length=255)  # 自定义字段
    v4: Optional[str] = Field(max_length=255)  # 自定义字段
    v5: Optional[str] = Field(max_length=255)  # 自定义字段

    # rule_id: Optional[int] = Field(default=None, primary_key=True, alias="id")
    # policy_type: Optional[str] = Field(max_length=32, alias="ptype")  # 代替 ptype，如 "p" 或 "g"
    # subject: Optional[str] = Field(max_length=255,alias="v0")  # 代替 v0
    # object: Optional[str] = Field(max_length=255,alias="v1") # 代替 v1
    # action: Optional[str] = Field(max_length=255,alias="v2")  # 代替 v2
    # description: Optional[str] = Field(max_length=255,alias="v3")  # 自定义字段

    def __repr__(self):
        return f"<CasbinRule {self.ptype}, {self.v0}, {self.v1}, {self.v2}>"
