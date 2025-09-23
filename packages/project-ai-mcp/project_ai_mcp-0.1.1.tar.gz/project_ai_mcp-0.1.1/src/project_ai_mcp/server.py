import os

import requests
from mcp.server.fastmcp import FastMCP

from project_ai_mcp.config import config

# Create an MCP server
mcp = FastMCP("Project AI")


@mcp.tool()
def update_feature_status(feature_id: str, status: int) -> str:
    """
    修改功能点状态

    Args:
        feature_id: 功能点ID
        status: 功能点状态（必填，1-未开始,2-进行中,3-已完成 ）

    Returns:
        str: 更新功能点状态结果
    """
    api_path = "/api/feature/update-status"
    api_url = os.path.join(config.project_ai_base_url, api_path)
    payload = {"featureId": feature_id, "status": status}

    response = requests.post(api_url, json=payload)

    if response.status_code == 200 and response.json().get("success"):
        return "success"

    return "failed: " + response.json().get("message")


def main():
    print("Hello from Project AI MCP!")

    # 验证必需的环境变量
    try:
        config.ensure_required_config()
        print("✓ 环境变量配置验证通过")
    except ValueError as e:
        print(f"❌ {e}")
        return

    mcp.run()


if __name__ == "__main__":
    main()
