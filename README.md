# 搜索引擎API v2.0.0

基于 **Meilisearch** 构建的高性能搜索引擎API，支持实时搜索、拼写错误容错、混合搜索、同义词、多语种等特性。v2.0.0版本新增**因果推理搜索**功能，支持知识图谱管理、反事实推理、用户意图理解等高级能力。

---

## ✨ 核心特性

### 🎯 基础搜索特性

| 特性 | 描述 |
|------|------|
| **实时搜索** | 输入即搜，毫秒级响应 |
| **拼写错误容错** | 内置拼写检查，自动纠错 |
| **混合搜索** | 关键词搜索 + 语义搜索（支持OpenAI嵌入） |
| **筛选与排序** | 灵活的过滤条件和多维度排序 |
| **分面搜索** | 聚合统计，分类导航 |
| **高亮显示** | 搜索结果关键词高亮 |
| **同义词支持** | 内置多语言同义词库，可自定义 |
| **多语种支持** | 自动语言检测，多语言停用词处理 |

### 🔬 高级因果推理搜索特性 (v2.0.0 新增)

| 特性 | 描述 |
|------|------|
| **知识图谱管理** | 构建领域知识图谱，标注实体间的因果关系 |
| **因果路径分析** | 发现实体间的多步因果链路，生成可解释的因果路径 |
| **反事实推理** | 探索假设情景（What-if分析），评估不同条件下的结果概率 |
| **用户意图理解** | 自动分析用户查询意图（8种类型），识别潜在需求 |
| **因果相关性评分** | 结合因果关系的搜索结果排序机制 |
| **相关实体发现** | 基于因果链的关联实体扩展搜索 |
| **可解释性** | 自然语言解释因果关系和搜索结果 |

---

## 🛠️ 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.9+ | 核心开发语言 |
| **FastAPI** | 0.115.0 | Web框架，高性能异步API |
| **Meilisearch** | Latest | 搜索引擎核心，毫秒级响应 |
| **Uvicorn** | 0.34.0 | ASGI服务器 |
| **Pydantic** | 2.9.2 | 数据验证和序列化 |
| **Httpx** | 0.27.2 | HTTP客户端 |
| **Docker** | - | 容器化部署 |

---

## 📁 项目结构

```
search-engine-api/
├── app/
│   ├── api/                          # RESTful API层
│   │   ├── search.py                 # 搜索API
│   │   ├── documents.py              # 文档管理API
│   │   ├── indexes.py                # 索引管理API
│   │   ├── settings.py               # 索引设置API
│   │   ├── tasks.py                  # 任务管理API
│   │   └── causal.py                 # 因果推理搜索API (新增)
│   │
│   ├── causal/                       # 因果推理模块 (新增)
│   │   ├── knowledge_graph.py        # 知识图谱管理
│   │   ├── causal_engine.py          # 因果推理引擎
│   │   ├── intent_analyzer.py        # 用户意图分析
│   │   └── causal_search_service.py  # 因果搜索整合服务
│   │
│   ├── search/                       # 搜索引擎核心模块
│   │   ├── client.py                 # Meilisearch客户端封装
│   │   ├── document.py               # 文档管理
│   │   ├── search_service.py         # 搜索服务
│   │   └── index_settings.py         # 索引设置管理
│   │
│   ├── utils/                        # 工具模块
│   │   ├── synonyms.py               # 多语言同义词预设
│   │   ├── multilingual.py           # 多语种支持
│   │   └── search_helpers.py         # 搜索辅助工具
│   │
│   ├── main.py                       # FastAPI主入口
│   ├── config.py                     # 配置管理
│   └── models.py                     # Pydantic数据模型
│
├── Dockerfile                        # API服务Docker镜像
├── docker-compose.yml                # 完整部署配置
├── requirements.txt                  # Python依赖
├── .env.example                      # 环境变量示例
├── examples.py                       # 使用示例代码
└── README.md                         # 项目说明文档
```

---

## 🚀 快速开始

### 方式1: Docker Compose（推荐）

```bash
# 1. 复制环境变量配置
cp .env.example .env

# 2. 启动所有服务（API + Meilisearch）
docker-compose up -d

# 3. 访问API文档
# - Swagger UI:  http://localhost:8000/docs
# - ReDoc:      http://localhost:8000/redoc
```

### 方式2: 本地开发

```bash
# 1. 启动Meilisearch
docker run -d -p 7700:7700 getmeili/meilisearch:latest

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动API服务
python -m uvicorn app.main:app --reload --port 8000
```

---

## 🔗 API端点概览

### 📊 基础API

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v1/search/` | POST/GET | 执行搜索 |
| `/api/v1/search/multi` | POST | 多索引搜索 |
| `/api/v1/search/suggest` | GET | 搜索建议 |
| `/api/v1/documents/{index}` | POST/PUT/GET/DELETE | 文档CRUD |
| `/api/v1/indexes/` | GET/POST | 索引管理 |
| `/api/v1/settings/{index}/synonyms` | PUT | 同义词配置 |
| `/api/v1/settings/{index}/filterable-attributes` | PUT | 可筛选属性 |
| `/api/v1/tasks/` | GET | 任务列表 |

### 🔬 因果推理API (v2.0.0 新增)

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v1/causal/search` | POST/GET | 因果推理搜索 |
| `/api/v1/causal/counterfactual` | POST | 反事实推理 |
| `/api/v1/causal/intent/analyze` | POST | 意图分析 |
| `/api/v1/causal/intent/summary` | GET | 意图摘要 |
| `/api/v1/causal/graph/info` | GET | 知识图谱统计 |
| `/api/v1/causal/entities/` | POST/GET/DELETE | 实体管理 |
| `/api/v1/causal/relations/` | POST/GET/DELETE | 关系管理 |
| `/api/v1/causal/causal-paths` | GET | 发现因果路径 |
| `/api/v1/causal/related-entities` | GET | 发现相关实体 |

---

## 📝 使用示例

### 示例1: 基础搜索

```python
import httpx

API_BASE = "http://localhost:8000/api/v1"

# 执行搜索
response = httpx.post(f"{API_BASE}/search/", json={
    "query": "python",
    "index": "documents",
    "limit": 10,
    "filter": "rating > 4",
    "sort": ["rating:desc"]
})

results = response.json()
print(f"找到 {results['estimatedTotalHits']} 条结果")
for hit in results["hits"]:
    print(f"- {hit['title']} (评分: {hit.get('rating', 'N/A')})")
```

### 示例2: 配置同义词

```python
# 配置同义词
httpx.put(f"{API_BASE}/settings/documents/synonyms", json={
    "python": ["py", "python3", "蟒"],
    "javascript": ["js", "es", "ecmascript"],
    "汽车": ["车辆", "轿车", "机动车"]
})

# 配置可筛选属性
httpx.put(f"{API_BASE}/settings/documents/filterable-attributes", 
          json=["category", "rating", "price"])

# 配置可排序属性
httpx.put(f"{API_BASE}/settings/documents/sortable-attributes", 
          json=["rating", "price", "createdAt"])
```

### 示例3: 构建知识图谱（因果推理）

```python
# 1. 添加实体
entities = [
    {"id": "smoking", "name": "吸烟", "entityType": "behavior", "description": "吸烟行为"},
    {"id": "lung_cancer", "name": "肺癌", "entityType": "disease", "description": "肺部恶性肿瘤"},
    {"id": "hypertension", "name": "高血压", "entityType": "disease", "description": "血压升高"},
    {"id": "heart_disease", "name": "心脏病", "entityType": "disease", "description": "心脏疾病"},
    {"id": "death", "name": "死亡", "entityType": "outcome", "description": "生命终结"}
]

for entity in entities:
    httpx.post(f"{API_BASE}/causal/entities", json=entity)

# 2. 添加因果关系
relations = [
    {"sourceEntity": "smoking", "targetEntity": "lung_cancer", "relationType": "causes", "strength": 0.85},
    {"sourceEntity": "smoking", "targetEntity": "hypertension", "relationType": "causes", "strength": 0.6},
    {"sourceEntity": "hypertension", "targetEntity": "heart_disease", "relationType": "leads_to", "strength": 0.75},
    {"sourceEntity": "lung_cancer", "targetEntity": "death", "relationType": "results_in", "strength": 0.9},
    {"sourceEntity": "heart_disease", "targetEntity": "death", "relationType": "results_in", "strength": 0.8}
]

for relation in relations:
    httpx.post(f"{API_BASE}/causal/relations", json=relation)
```

### 示例4: 发现因果路径

```python
# 查找从"吸烟"到"死亡"的因果路径
response = httpx.get(
    f"{API_BASE}/causal/causal-paths",
    params={
        "source": "smoking",
        "target": "death",
        "max_depth": 3,
        "min_strength": 0.5
    }
)

paths = response.json()
print(f"找到 {paths['pathCount']} 条因果路径:")
for i, path in enumerate(paths["paths"], 1):
    print(f"\n路径 {i}: {path['explanation']}")
    print(f"强度: {path['totalStrength']:.2f}")
    print(f"置信度: {path['confidence']:.2f}")
```

### 示例5: 反事实推理

```python
# 分析"如果不吸烟，会得肺癌吗？"
response = httpx.post(
    f"{API_BASE}/causal/counterfactual",
    json={
        "query": "我吸烟",
        "assumeFact": "我不吸烟",
        "targetOutcome": "我会得肺癌",
        "explorePaths": True,
        "maxPaths": 5
    }
)

result = response.json()
print("=" * 50)
print("反事实推理分析")
print("=" * 50)
print(f"原始事实: {result['result']['originalFact']}")
print(f"假设事实: {result['result']['assumedFact']}")
print(f"目标结果: {result['result']['targetOutcome']}")
print(f"结果概率: {result['result']['outcomeProbability']:.2%}")
print("-" * 50)
print(f"解释: {result['result']['explanation']}")
```

### 示例6: 用户意图分析

```python
# 分析用户查询意图
response = httpx.post(
    f"{API_BASE}/causal/intent/analyze",
    params={"query": "为什么吸烟会导致肺癌？"}
)

intent = response.json()
print("=" * 50)
print("用户意图分析结果")
print("=" * 50)
print(f"意图类型: {intent['intentType']}")
print(f"关键实体: {', '.join(intent['queryEntities'])}")
print(f"推断目标: {intent['inferredGoal']}")
print(f"置信度: {intent['confidence']:.2%}")
print("-" * 50)
print("潜在需求:")
for need in intent["potentialNeeds"]:
    print(f"- {need}")
```

### 示例7: 因果推理搜索

```python
# 执行因果搜索
response = httpx.post(
    f"{API_BASE}/causal/search",
    json={
        "query": "吸烟与肺癌的关系",
        "index": "documents",
        "limit": 10,
        "includeCausalPaths": True,
        "maxCausalDepth": 3,
        "exploreRelatedEntities": True,
        "intentAnalysis": True
    }
)

result = response.json()
print("=" * 50)
print("因果搜索结果")
print("=" * 50)
print(f"查询: {result['query']}")
print(f"处理时间: {result['processingTimeMs']}ms")

if result.get('userIntent'):
    print(f"用户意图: {result['userIntent']['intentType']}")

print(f"搜索结果: {len(result['hits'])} 条")

for i, hit in enumerate(result['hits'][:3], 1):
    print("-" * 50)
    print(f"结果 {i}:")
    print(f"标题: {hit['document']['title']}")
    print(f"因果相关性: {hit['causalRelevance']:.2%}")
    print(f"相关实体: {', '.join(hit['relatedEntities'][:3])}")
    if hit.get('explanation'):
        print(f"解释: {hit['explanation']}")
```

---

## 🎯 意图类型识别

系统支持8种用户意图类型的自动识别：

| 意图类型 | 英文标识 | 描述 | 示例查询 |
|----------|----------|------|----------|
| **信息查询** | `informational` | 获取知识或信息 | "什么是Python？" |
| **导航** | `navigational` | 找到特定内容 | "搜索Python教程" |
| **交易** | `transactional` | 执行某种操作 | "下载Python安装包" |
| **因果查询** | `causal` | 理解因果关系 | "为什么吸烟会导致肺癌？" |
| **反事实推理** | `counterfactual` | 探索假设情景 | "如果我不学习，能找到工作吗？" |
| **比较** | `comparative` | 对比不同选项 | "Python vs Java，哪个更好？" |
| **问题排查** | `troubleshooting` | 解决问题 | "为什么我的代码报错？" |
| **探索** | `exploratory` | 发现相关内容 | "还有什么和Python相关的？" |

---

## 🔗 因果关系类型

支持多种因果关系类型：

| 关系类型 | 英文标识 | 方向 | 强度权重 | 示例 |
|----------|----------|------|----------|------|
| **导致** | `causes` | 正向 | 1.0 | 吸烟 → 肺癌 |
| **导致** | `leads_to` | 正向 | 0.9 | 高血压 → 心脏病 |
| **结果是** | `results_in` | 正向 | 0.85 | 肺癌 → 死亡 |
| **使能够** | `enables` | 正向 | 0.7 | 教育 → 就业 |
| **阻止** | `prevents` | 负向 | 0.9 | 锻炼 → 肥胖 |
| **影响** | `influences` | 双向 | 0.6 | 压力 → 睡眠 |
| **相关** | `correlates_with` | 双向 | 0.3 | 年龄 → 收入 |
| **需要** | `requires` | 反向 | 0.8 | 成功 → 努力 |
| **依赖** | `depends_on` | 反向 | 0.75 | 植物 → 阳光 |

---

## 🌍 多语言同义词支持

内置6种语言的同义词库：

| 语言 | 示例同义词 |
|------|-------------|
| **中文 (zh)** | 汽车=车辆=轿车, 计算机=电脑=PC |
| **英文 (en)** | python=py=python3, javascript=js=es |
| **日文 (ja)** | 車=自動車, パソコン=コンピュータ |
| **法文 (fr)** | voiture=automobile=véhicule |
| **德文 (de)** | auto=wagen=fahrzeug |
| **西班牙文 (es)** | coche=automóvil=vehículo |

---

## 🎯 应用场景

| 场景 | 描述 |
|------|------|
| **文档搜索** | 搜索文档、文章、知识库等文本内容 |
| **电商搜索** | 商品搜索、价格筛选等电商场景 |
| **混合搜索** | 同时搜索多种类型的数据 |
| **医疗知识图谱** | 构建医疗知识图谱，分析疾病因果关系 |
| **用户行为分析** | 分析用户行为，发现因果链路 |
| **推荐系统** | 基于因果关系的个性化推荐 |
| **决策支持** | 反事实推理辅助决策 |
| **问答系统** | 理解用户意图，提供精准回答 |

---

## 📊 版本历史

| 版本 | 发布日期 | 主要更新 |
|------|----------|----------|
| **v1.0.0** | - | 基础搜索功能：实时搜索、拼写容错、混合搜索、同义词、多语种 |
| **v2.0.0** | 2026-04-28 | 新增因果推理搜索：知识图谱管理、因果路径分析、反事实推理、用户意图理解、因果相关性评分 |

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

---

## 📄 许可证

MIT License

---

## 🔄 核心设计理念

1. **高性能**：基于Meilisearch，毫秒级响应
2. **可扩展性**：模块化设计，易于扩展新功能
3. **可解释性**：因果路径自然语言解释，搜索结果透明
4. **易用性**：RESTful API，自动生成Swagger文档
5. **可部署性**：Docker一键部署，易于维护

---

这个项目是一个功能完整的**企业级搜索引擎API**，特别适合需要**智能搜索**、**知识图谱**、**因果推理**能力的应用场景。通过结合传统搜索技术和因果推理方法，它能够更好地理解用户意图，提供更精准、更可解释的搜索结果。
