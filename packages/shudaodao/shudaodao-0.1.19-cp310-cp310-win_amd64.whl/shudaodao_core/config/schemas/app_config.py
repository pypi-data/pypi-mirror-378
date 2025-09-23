#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @License  ：(C)Copyright 2025, 数道智融科技
# @Author   ：李锋
# @Software ：PyCharm
# @Date     ：2025/7/20 下午1:20
# @Desc     ：

from typing import Literal, Optional, List

from pydantic import Field, BaseModel

from .auth import AuthConfigSetting
from .models import ModelCollectionConfigSetting
from .routers import RouterConfigSetting
from .snowflake import SnowflakeConfigSetting
from .storage import StorageConfigSetting
from .webapp import FastAPIConfigSetting


class EnvironmentConfigSetting(BaseModel):
    model: Literal["dev", "prod"] = Field(..., description="环境配置")
    logging_level: str = Field("debug", description="日志级别")
    show_merge_yaml: bool = Field(True, description="显示合并yaml")

    @property
    def is_prod(self) -> bool:
        return self.model == "prod"

    @property
    def model_desc(self) -> str:
        return "开发环境" if self.model == "dev" else "生产环境"

    @property
    def logging_level_desc(self) -> str:
        if self.logging_level == "debug":
            return "调试"
        elif self.logging_level == "info":
            return "提醒"
        elif self.logging_level == "warning":
            return "警告"
        elif self.logging_level == "error":
            return "错误"
        else:
            raise ValueError(f"Unknown logging level: {self.logging_level}")


class AppConfigSetting(BaseModel):
    environment: EnvironmentConfigSetting = Field(default_factory=EnvironmentConfigSetting, description="环境配置")
    webapp: FastAPIConfigSetting = Field(default_factory=FastAPIConfigSetting, description="FastAPI启动")
    auth: AuthConfigSetting = Field(default_factory=AuthConfigSetting, description="认证、鉴权")
    generate_snowflake: SnowflakeConfigSetting = Field(SnowflakeConfigSetting, description="雪花算法ID生成配置")
    routers: Optional[List[RouterConfigSetting]] = Field(None, description="路由配置")
    storage: Optional[StorageConfigSetting] = Field(None, description="存储配置")
    models: Optional[ModelCollectionConfigSetting] = Field(None, description="模型配置")
