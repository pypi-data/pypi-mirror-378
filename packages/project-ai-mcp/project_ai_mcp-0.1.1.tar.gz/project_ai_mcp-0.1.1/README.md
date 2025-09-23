# Project AI MCP Server

一个用于 [Project AI](https://project-ai.hailiangedu.com) 平台集成的 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 服务器。

## 功能特性

- 🚀 基于 FastMCP 构建的高性能 MCP 服务器
- 📋 支持 Project AI 功能点状态管理
- 🔐 安全的环境变量配置管理
- 🛠 支持多种安装和运行方式

## 环境要求

- Python 3.12+
- 可访问 Project AI API 端点

## 安装

### 方法一：使用 uvx（推荐）

```bash
# 临时运行
uvx project-ai-mcp

# 或永久安装
uv tool install project-ai-mcp
```

### 方法二：使用 pip

```bash
pip install project-ai-mcp
```

### 方法三：开发安装

```bash
git clone <repository-url>
cd project-ai-mcp
uv sync
uv run python main.py
```

## 使用方法

### 作为独立服务器运行

```bash
# 使用 uvx
uvx project-ai-mcp

# 或使用已安装的命令
project-ai-mcp

# 或使用 Python 模块
python -m project_ai_mcp
```

### 在 Claude Code 中使用

**注意**: 如果不设置 `PROJECT_AI_BASE_URL`，将使用默认的 API 端点：`https://project-ai.hailiangedu.com`

```base
# 使用默认的 API 端点
claude mcp add project-ai -s user -- uvx project-ai-mcp


# 使用自定义的 API 端点
claude mcp add project-ai -s user -e "PROJECT_AI_BASE_URL=XXXXX" -- uvx project-ai-mcp
```


## 可用工具

### `update_feature_status`

修改 Project AI 平台上功能点的状态。

**参数：**
- `feature_id` (string): 功能点 ID
- `status` (int): 功能点状态，支持：
  - `1`: 未开始
  - `2`: 进行中
  - `3`: 已完成

**返回值：**
- `"success"`: 操作成功
- `"failed: [错误信息]"`: 操作失败及错误详情

**示例使用：**
```python
# 将功能点标记为进行中
update_feature_status(
    feature_id="feature_123",
    status=2
)

# 将功能点标记为已完成
update_feature_status(
    feature_id="feature_456",
    status=3
)
```

## 开发

### 环境设置

```bash
# 克隆仓库
git clone <repository-url>
cd project-ai-mcp

# 创建虚拟环境并安装依赖
uv venv
uv sync

# 运行开发服务器
uv run python main.py
```

### 代码质量检查

```bash
# 运行 linter
ruff check

# 格式化代码
ruff format
```

### 构建和发布

```bash
# 构建包
uv build

# 发布到 PyPI（需要配置 PyPI 凭据）
twine upload dist/*
```

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 支持

如有问题，请在 [GitHub Issues](https://github.com/philoveritas/project-ai-mcp/issues) 中提出。