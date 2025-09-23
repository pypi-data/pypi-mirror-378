#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @License  ：(C)Copyright 2025, 数道智融科技
# @Author   ：李锋
# @Software ：PyCharm
# @Date     ：2025/9/2 下午4:24
# @Desc     ：

from datetime import datetime, timezone
from typing import Optional

from pydantic import EmailStr
from sqlalchemy import BigInteger
from sqlmodel import SQLModel, Field

from ..schemas.response import BaseResponse
from ..utils.generate_unique_id import get_primary_id


class AuthUserBase(SQLModel):
    auth_user_id: Optional[int] = Field(default_factory=get_primary_id, primary_key=True, sa_type=BigInteger)
    username: str = Field(unique=True, index=True, max_length=50)
    password: str
    email: Optional[EmailStr] = Field(None, max_length=100)
    is_active: bool = True


class AuthUser(AuthUserBase, table=True):
    """ 数据模型 - 数据库表 T_Auth_User 结构模型 """
    __tablename__ = "t_auth_user"
    __table_args__ = {"comment": "鉴权用户表"}

    last_login: Optional[datetime] = Field(default_factory=datetime.utcnow, description="aa")
    created_at: datetime = Field(lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AuthUserResponse(BaseResponse):
    auth_user_id: Optional[int] = Field(sa_type=BigInteger)
    username: str = Field(max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=100)
    is_active: bool = True


class AuthLogin(SQLModel):
    """ 登录模型 """
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=50)


class AuthRegister(AuthLogin):
    """ 登录模型 """
    email: Optional[EmailStr] = Field(None, max_length=100)


class AuthPassword(SQLModel):
    """ 修改密码模型 """
    old_password: str
    new_password: str = Field(min_length=6, max_length=50)
