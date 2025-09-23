#!/usr/bin/env python3
"""
配置文件 - 管理Project AI API endpoints和其他配置信息
"""

import os


class Config:
    """配置类"""

    def __init__(self):
        # Project AI 配置
        self.default_project_ai_base_url = "https://project-ai.hailiangedu.com"
        self.project_ai_base_url = os.getenv("PROJECT_AI_BASE_URL", "")
        if not self.project_ai_base_url:
            self.project_ai_base_url = self.default_project_ai_base_url

    def validate_config(self) -> list:
        """验证配置是否完整"""
        errors = []

        # if not self.xx:
        #     errors.append("PROJECTXX_AI_BASE_URL 环境变量是必需的")

        return errors

    def ensure_required_config(self):
        """确保必需的配置存在，否则抛出异常"""
        errors = self.validate_config()
        if errors:
            raise ValueError("配置错误：\n" + "\n".join(f"- {error}" for error in errors))


# 创建全局配置实例
config = Config()
