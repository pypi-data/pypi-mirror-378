#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @License  ：(C)Copyright 2025, 数道智融科技
# @Author   ：李锋
# @Software ：PyCharm
# @Date     ：2025/9/21 下午8:47
# @Desc     ：


from pydantic import BaseModel, Field


class AuthConfigSetting(BaseModel):
    token_key: str = Field(..., description="JWT TOKEN_SECRET_KEY")
    rebuild_permission_rule: bool = Field(False, description="重置")
    default_admin_roles: list[str] = ["admin"]
    default_admin_users: list[str] = ["admin"]
