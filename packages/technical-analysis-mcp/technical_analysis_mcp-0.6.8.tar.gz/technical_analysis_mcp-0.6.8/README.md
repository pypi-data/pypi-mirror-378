# 技术指标分析工具

该工具提供MCP服务器和HTTP API用于分析ETF和股票的技术指标。它使用`akshare`库获取历史数据，并计算RSI、布林带和移动平均线等技术指标。

## 环境要求

- Python 3.9+
- 依赖库：akshare, pandas, fastapi, mcp, uvicorn

## 安装依赖

```bash
# 方式1：安装所有依赖
pip install -r requirements.txt

# 方式2：仅安装核心依赖
pip install akshare pandas fastapi mcp uvicorn openai backtrader scipy
```

## 快速启动

### 方式1：使用启动脚本（推荐）

**Linux/Mac:**
```bash
# 启动MCP服务器
./run_mcp_server.sh [stdio|streamable-http]

# 启动HTTP服务器
./run_http_server.sh [port]

# 示例
./run_mcp_server.sh stdio
./run_http_server.sh 8000
```

**Windows:**
```cmd
# 启动MCP服务器
run_mcp_server.bat [stdio|streamable-http]

# 启动HTTP服务器
run_http_server.bat [port]

# 示例
run_mcp_server.bat stdio
run_http_server.bat 8000
```

### 方式2：直接通过模块启动

```bash
# 启动MCP服务器
python3 -m technical_analysis.main --transport stdio
python3 -m technical_analysis.main --transport streamable-http

# 启动HTTP服务器
python3 -m uvicorn technical_analysis.http_server:app --reload --port 8000
```

### 方式3：使用npm脚本

```bash
# 启动MCP服务器
npm start

# 启动HTTP服务器
npm run http
```


## API文档

mcp服务器提供的接口:

### analyze_etf_technical

```python
@mcp.tool()
def analyze_etf_technical(etf_code='510300', with_market_style=False):
    """
    ETF技术指标分析工具
    :param etf_code: ETF代码 (例如'510300')
    :param with_market_style: 是否包含市场风格分类 (True/False)
    :param base_date: 基准日期，格式为YYYYMMDD (可选)
    :return: 包含技术指标的Markdown表格(最后5条记录)
    """
```

**新增字段说明**:


**参数**:
- `etf_code`: ETF代码，默认为'510300'(沪深300ETF)

**返回值**:
- 包含以下技术指标的Markdown表格:
  - 价格数据
  - RSI指标
  - 布林带
  - 移动平均线
  - `atr`: 平均真实波幅(10日)，衡量价格波动性的指标，数值越大表示波动越大
  - `mkt_style`: 市场风格分类结果

**示例**:
```python
result = analyze_etf_technical('510300')
print(result)
```

### analyze_stock_hist_technical

```python
@mcp.tool()
def analyze_stock_hist_technical(stock_code='000001'):
    """
    股票历史数据技术指标分析工具
    :param stock_code: 股票代码 (例如'000001')
    :param base_date: 基准日期，格式为YYYYMMDD (可选)
    :return: 包含技术指标的Markdown表格(最后5条记录)
    """
```

**参数**:
- `stock_code`: 股票代码，默认为'000001'(平安银行)

**返回值**:
- 包含以下技术指标的Markdown表格:
  - 价格数据
  - RSI指标
  - 布林带
  - 移动平均线
  - `atr`: 平均真实波幅(10日)，衡量价格波动性的指标，数值越大表示波动越大
  - `mkt_style`: 市场风格分类结果

**示例**:
```python
result = analyze_stock_hist_technical('000001')
print(result)
```

### get_stock_news

```python
@mcp.tool()
def get_stock_news(news_count=3, publish_before=None):
    """
    以时间线方式获取股票市场最新事件，包括政策、行业动态和市场行情
    :param news_count: 返回新闻数量 (默认3条)
    :param publish_before: 发布日期上限 (格式YYYY-MM-DD)
    :return: 新闻列表 (JSON格式)
    """
```

**参数**:
- `news_count`: 返回新闻数量，默认为3条
- `publish_before`: 发布日期上限，格式为YYYY-MM-DD

**返回值**:
- 新闻列表 (JSON格式)

**示例**:
```python
result = get_stock_news(news_count=5)
print(result)
```

### screen_etf_anomaly_in_tech

```python
@mcp.tool()
def screen_etf_anomaly_in_tech(etf_codes="513050", base_date=None, lookback_days=60, top_k=10):
    """
    筛选ETF异动行情，基于技术指标分析找出近期表现异常的ETF
    :param etf_codes: 要筛选的ETF代码列表，默认为"513050"，多个代码用逗号分隔
    :param base_date: 基准日期(格式YYYYMMDD)，默认为当前日期
    :param lookback_days: 回溯天数，用于计算技术指标(默认60天)
    :param top_k: 返回排名前几的ETF(默认10个)
    :return: 包含异动ETF信息的Markdown表格，包括ETF代码、名称、异常指标和得分
    """
```

**参数**:
- `etf_codes`: ETF代码列表，默认为"513050"
- `base_date`: 基准日期，格式为YYYYMMDD
- `lookback_days`: 回溯天数，默认为60天
- `top_k`: 返回排名前几的ETF，默认为10个

**返回值**:
- 包含异动ETF信息的Markdown表格

**示例**:
```python
result = screen_etf_anomaly_in_tech(etf_codes="513050,510300")
print(result)
```

## 安装与配置

### 源码安装（推荐）
```bash
# 克隆项目
git clone <repository-url>
cd technical_analysis

# 安装依赖
pip install -r requirements.txt

# 直接运行（无需安装包）
python3 -m technical_analysis.main --transport stdio
```

### 包安装（可选）
```bash
# 从源码安装
pip install -e .

# 运行
technical-analysis-mcp
```

### 配置
1. 确保已安装Python 3.9+版本
2. 安装所需依赖库
3. 数据文件会自动生成，无需额外配置

### 市场风格分类示例
```python
# 获取带市场风格分类的ETF技术指标
result = analyze_etf_technical('510300', with_market_style=True)
print(result)

# 获取带市场风格分类的股票技术指标
result = analyze_stock_hist_technical('000001', with_market_style=True)
print(result)
```

## MCP配置示例

### 方式1：使用启动脚本
```json
{
  "mcpServers": {
    "technical-analysis-mcp": {
      "command": "/path/to/technical_analysis/run_mcp_server.sh",
      "args": ["stdio"]
    }
  }
}
```

### 方式2：直接使用模块
```json
{
  "mcpServers": {
    "technical-analysis-mcp": {
      "command": "python3",
      "args": ["-m", "technical_analysis.main", "--transport", "stdio"]
    }
  }
}
```

### 方式3：使用npm脚本
```json
{
  "mcpServers": {
    "technical-analysis-mcp": {
      "command": "npm",
      "args": ["start"]
    }
  }
}
```

## RESTful API

### 启动HTTP服务器
```bash
# 方式1：使用启动脚本
./run_http_server.sh 8000

# 方式2：直接启动
python3 -m uvicorn technical_analysis.http_server:app --reload --port 8000

# 方式3：使用npm脚本
npm run http
```

### API文档
服务器启动后，可以通过以下地址访问：
- **API文档**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### API端点

#### ETF技术分析
```
GET /api/etf/{etf_code}
```

参数：
- `etf_code`: ETF代码 (例如'510300')
- `with_market_style`: 是否包含市场风格分类 (默认true)
- `base_date`: 基准日期 (格式YYYYMMDD)
- `return_days`: 返回数据条数 (默认5)

#### ETF异动筛选
```
GET /api/etf/screen
```

参数：
- `etf_codes`: ETF代码列表 (逗号分隔)
- `base_date`: 基准日期 (格式YYYYMMDD)
- `top_k`: 返回数量 (默认10)

## 项目结构

```
technical_analysis/
├── technical_analysis/          # 主包目录
│   ├── __init__.py             # 包初始化
│   ├── __main__.py             # 模块入口
│   ├── main.py                 # MCP服务器主程序
│   ├── http_server.py          # HTTP服务器
│   ├── stock_data.py           # 股票数据获取
│   ├── etf_screener.py         # ETF异动筛选
│   ├── trading_strategy.py     # 交易策略
│   ├── market_sentiment.py     # 市场情绪分析
│   ├── grid_strategy_backtest.py  # 网格策略回测
│   ├── grid_loader.py          # 网格加载器
│   ├── vector_db.py            # 向量数据库
│   ├── broker_stock_analysis.py # 券商股票分析
│   └── backtest_data.py        # 回测数据
├── requirements.txt            # Python依赖
├── pyproject.toml             # 项目配置
├── package.json               # npm脚本配置
├── run_mcp_server.sh         # MCP服务器启动脚本(Linux/Mac)
├── run_http_server.sh        # HTTP服务器启动脚本(Linux/Mac)
├── run_mcp_server.bat        # MCP服务器启动脚本(Windows)
├── run_http_server.bat       # HTTP服务器启动脚本(Windows)
├── s.yaml                    # 阿里云函数计算配置
└── README.md                 # 项目文档
```

## 特性

- 📊 **技术指标分析**: RSI、布林带、移动平均线、ATR等
- 🎯 **市场风格分类**: 自动识别市场状态
- 📈 **ETF异动筛选**: 基于技术指标的异常检测
- 🔍 **市场情绪分析**: 复合情绪分数计算
- 📰 **新闻事件检索**: 股票市场新闻获取
- 🧠 **LLM集成**: 支持AI驱动的交易策略生成
- 🚀 **多部署方式**: 本地、云函数、容器化部署
- 🔌 **标准化接口**: MCP协议和RESTful API
- 🌏 **中文市场支持**: 专注中国金融数据

## 许可证

MIT License