#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @License  ：(C)Copyright 2025, 数道智融科技
# @Author   ：李锋
# @Software ：PyCharm
# @Date     ：2025/9/17 上午11:06
# @Desc     ：


# custom_model.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from ..utils.generate_unique_id import get_primary_id

Base = declarative_base()


class AuthRule(Base):
    __tablename__ = "t_auth_rule"
    rule_id = Column(Integer, default=get_primary_id, primary_key=True, autoincrement=False)
    policy_type = Column(String(32), nullable=False)  # 代替 ptype，如 "p" 或 "g"
    subject = Column(String(255), nullable=False)  # 代替 v0
    object = Column(String(255), nullable=False)  # 代替 v1
    action = Column(String(255), nullable=False)  # 代替 v2
    description = Column(String(255))  # 自定义字段

    def __repr__(self):
        return f"<CasbinRule {self.policy_type}, {self.subject}, {self.object}, {self.action}>"
