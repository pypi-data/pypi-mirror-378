# NagaAgent Core

NagaAgent核心依赖包，包含核心功能和API服务器相关依赖。

## 版本

当前版本：1.0.1

## 包含的依赖

### 核心依赖
- `mcp>=1.6.0` - MCP协议支持
- `openai>=1.76.0` - OpenAI API客户端
- `python-dotenv>=1.1.0` - 环境变量管理
- `requests>=2.32.3` - HTTP请求库
- `aiohttp>=3.11.18` - 异步HTTP客户端

### API服务器相关依赖
- `flask>=3.1.0` - Flask Web框架
- `gevent>=25.5.1` - 异步网络库
- `fastapi>=0.115.0` - FastAPI Web框架
- `uvicorn[standard]>=0.34.0` - ASGI服务器

## 安装

```bash
pip install nagaagent-core==1.0.1
```

## 开发安装

```bash
git clone <repository-url>
cd nagaagent-core
pip install -e .
```

## 许可证

MIT License
