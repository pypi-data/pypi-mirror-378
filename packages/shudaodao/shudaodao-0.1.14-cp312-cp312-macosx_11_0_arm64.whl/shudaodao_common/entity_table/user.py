#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @License  ：(C)Copyright 2025, 数道智融科技
# @Author   ：李锋
# @Software ：PyCharm
# @Date     ：2025/8/28 下午5:04
# @Desc     ：


from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship

from shudaodao_core import get_primary_id


class UserBase(SQLModel):
    """ 基础对象 - 共用字段 """
    username: str = Field(unique=True, index=True, max_length=50)
    email: str = Field(unique=True, index=True, max_length=100)
    nickname: Optional[str] = Field(default=None, max_length=100)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    role: str = Field(default="user", max_length=20)


class User(UserBase, table=True):
    """ 数据模型 - 数据库表 T_User 结构模型 """
    __tablename__ = "t_user"
    user_id: Optional[int] = Field(default_factory=get_primary_id, primary_key=True)
    password: str  # 不直接暴露给API
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(default_factory=datetime.utcnow)
    # 关系
    tokens: List["UserToken"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    """ 创建模型 - 用于[post]创建接口 """
    password: str = Field(min_length=8, alias="register-password")  # 密码不应直接存储在数据库模型中
    username: str = Field(alias="register-username")
    email: str = Field(alias="register-email")


class UserUpdate(UserBase):
    """ 更新模型 - 用于[patch]更新接口 """
    username: str = Field(None)
    updated_at: datetime = Field(None)


class UserResponse(UserBase):
    """ 响应模型 - 用于响应前端"""
    user_id: int


class UserToken(SQLModel, table=True):
    token_id: Optional[int] = Field(default_factory=get_primary_id, primary_key=True)
    token: str = Field(unique=True, index=True)
    user_id: int = Field(foreign_key="t_user.user_id")
    expires_at: datetime
    is_revoked: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # 关系
    user: User = Relationship(back_populates="tokens")
