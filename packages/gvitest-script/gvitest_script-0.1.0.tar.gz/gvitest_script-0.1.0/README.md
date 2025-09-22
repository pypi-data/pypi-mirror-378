# Script Server - 自动化脚本生成器

基于 Jinja2 模板引擎的自动化脚本生成系统，支持 Agent/Manual 双模式执行、控制流、条件表达式和预期结果验证。

## 🚀 快速开始

### 1. 安装启动

```bash
cd script_server

# 使用 uv 同步依赖并创建虚拟环境（基于 pyproject.toml / uv.lock）
uv sync

# 激活虚拟环境
source .venv/bin/activate

# 使用默认文件服务器配置
script-server
```

### 2. 文件服务器配置

默认文件服务器URL：`http://localhost:8080`

```bash
# 使用默认文件服务器（推荐）
script-server

# 自定义文件服务器URL
script-server --file-server-url http://{FILE_SERVER_URL}

# 通过环境变量设置文件服务器
export FILE_SERVER_URL=http://localhost:3000
script-server

# 本地模式（不支持文件服务器的下载和上传，使用和返回本地文件）
script-server --file-server-url ""
```

### 3. 工作空间配置

默认工作空间路径：`项目目录/script_workspace`

```bash
# 使用默认工作空间（推荐）
script-server

# 自定义工作空间路径
script-server --workspace /path/to/custom/workspace

# 通过环境变量设置工作空间
export WORKSPACE_PATH=/path/to/custom/workspace
script-server
```




