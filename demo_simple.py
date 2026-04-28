"""
搜索引擎API演示脚本
====================

这个脚本展示了搜索引擎API的各种功能。
"""

import httpx
import json
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

API_BASE_URL = "http://127.0.0.1:8000"


def print_separator(title=""):
    print("\n" + "=" * 60)
    if title:
        print(f"  {title}")
    print("=" * 60)


def demo_service_status():
    """演示服务状态检查"""
    print_separator("1. 服务状态检查")
    
    with httpx.Client() as client:
        response = client.get(f"{API_BASE_URL}/")
        print(f"[OK] 根路径响应状态: {response.status_code}")
        
        data = response.json()
        print(f"\n服务名称: {data['name']}")
        print(f"版本: {data['version']}")
        print(f"状态: {data['status']}")
        print(f"文档地址: {data['docs']}")
        print(f"\n支持的功能:")
        for feature in data['features']:
            print(f"  - {feature}")
        
        response = client.get(f"{API_BASE_URL}/health")
        print(f"\n[OK] 健康检查响应: {response.json()}")


def demo_api_structure():
    """演示API结构"""
    print_separator("2. API结构概览")
    
    with httpx.Client() as client:
        response = client.get(f"{API_BASE_URL}/openapi.json")
        openapi_spec = response.json()
        
        print(f"API标题: {openapi_spec['info']['title']}")
        print(f"API版本: {openapi_spec['info']['version']}")
        print(f"描述: {openapi_spec['info']['description']}")
        
        paths = openapi_spec['paths']
        print(f"\n[OK] 总API端点数量: {len(paths)}")
        
        tags = {}
        for path, methods in paths.items():
            for method, details in methods.items():
                if method in ['get', 'post', 'put', 'delete', 'patch']:
                    tag = details.get('tags', ['default'])[0]
                    if tag not in tags:
                        tags[tag] = 0
                    tags[tag] += 1
        
        print("\n按功能分类的端点数量:")
        for tag, count in sorted(tags.items()):
            print(f"  - {tag}: {count} 个端点")


def demo_search_endpoints():
    """演示搜索API端点"""
    print_separator("3. 搜索API端点展示")
    
    search_endpoints = [
        {
            "method": "POST",
            "path": "/api/v1/search/",
            "description": "执行搜索请求",
            "features": [
                "实时搜索（输入即搜）",
                "拼写错误容错",
                "混合搜索（关键词+语义）",
                "筛选与排序",
                "高亮显示",
                "分面搜索"
            ]
        },
        {
            "method": "POST",
            "path": "/api/v1/search/multi",
            "description": "多索引搜索",
            "features": ["在单个请求中搜索多个索引"]
        },
        {
            "method": "GET",
            "path": "/api/v1/search/quick",
            "description": "快速搜索（GET方式）",
            "features": ["适用于简单的搜索场景，支持实时搜索"]
        },
        {
            "method": "GET",
            "path": "/api/v1/search/suggest",
            "description": "搜索建议",
            "features": ["输入即搜的自动补全功能"]
        }
    ]
    
    for endpoint in search_endpoints:
        print(f"\n[{endpoint['method']}] {endpoint['path']}")
        print(f"  描述: {endpoint['description']}")
        print(f"  功能:")
        for feature in endpoint['features']:
            print(f"    - {feature}")


def demo_document_management():
    """演示文档管理API"""
    print_separator("4. 文档管理API")
    
    doc_endpoints = [
        ("POST", "/api/v1/documents/{index_uid}", "添加或更新文档"),
        ("PUT", "/api/v1/documents/{index_uid}", "部分更新文档"),
        ("GET", "/api/v1/documents/{index_uid}", "列出索引中的文档"),
        ("GET", "/api/v1/documents/{index_uid}/{document_id}", "获取单个文档"),
        ("DELETE", "/api/v1/documents/{index_uid}/{document_id}", "删除单个文档"),
        ("DELETE", "/api/v1/documents/{index_uid}", "批量删除文档"),
        ("DELETE", "/api/v1/documents/{index_uid}/all", "删除所有文档"),
    ]
    
    print("文档操作端点:")
    for method, path, desc in doc_endpoints:
        print(f"  [{method}] {path}")
        print(f"      {desc}")


def demo_index_settings():
    """演示索引设置API"""
    print_separator("5. 高级功能配置（索引设置）")
    
    advanced_features = [
        {
            "endpoint": "PUT /api/v1/settings/{index_uid}/synonyms",
            "description": "同义词配置",
            "example": {
                "python": ["py", "python3", "蟒"],
                "javascript": ["js", "es", "ecmascript"]
            },
            "languages": ["中文", "英文", "日文", "法文", "德文", "西班牙文"]
        },
        {
            "endpoint": "PUT /api/v1/settings/{index_uid}/filterable-attributes",
            "description": "可筛选属性配置",
            "example": ["category", "rating", "price", "date"],
            "usage": "只有配置的属性才能在搜索时使用 filter 参数"
        },
        {
            "endpoint": "PUT /api/v1/settings/{index_uid}/sortable-attributes",
            "description": "可排序属性配置",
            "example": ["rating:desc", "date:asc", "price:asc"],
            "usage": "只有配置的属性才能在搜索时使用 sort 参数"
        },
        {
            "endpoint": "PUT /api/v1/settings/{index_uid}/typo-tolerance",
            "description": "拼写错误容错配置",
            "config": {
                "enabled": True,
                "minWordSizeForTypos": {
                    "oneTypo": 5,
                    "twoTypos": 9
                }
            },
            "feature": "搜索 'phyton' 会自动匹配 'python'"
        },
        {
            "endpoint": "PUT /api/v1/settings/{index_uid}/embedders",
            "description": "嵌入器配置（混合搜索）",
            "config": {
                "default": {
                    "source": "openAi",
                    "model": "text-embedding-ada-002",
                    "dimensions": 1536
                }
            },
            "feature": "启用语义搜索，支持关键词+语义混合搜索"
        }
    ]
    
    for feature in advanced_features:
        print(f"\n[*] {feature['description']}")
        print(f"   端点: {feature['endpoint']}")
        
        if 'example' in feature:
            print(f"   示例: {json.dumps(feature['example'], ensure_ascii=False)}")
        
        if 'config' in feature:
            print(f"   配置示例: {json.dumps(feature['config'], indent=2, ensure_ascii=False)}")
        
        if 'usage' in feature:
            print(f"   说明: {feature['usage']}")
        
        if 'feature' in feature:
            print(f"   特性: {feature['feature']}")
        
        if 'languages' in feature:
            print(f"   支持语言: {', '.join(feature['languages'])}")


def demo_deployment():
    """演示部署方式"""
    print_separator("6. 部署方式")
    
    print("""
方式1: Docker Compose（推荐）
==============================
# 1. 复制环境变量配置
cp .env.example .env

# 2. 启动所有服务
docker-compose up -d

# 3. 访问API文档
# - Swagger UI:  http://localhost:8000/docs
# - ReDoc:      http://localhost:8000/redoc

方式2: 本地开发
===============
# 1. 启动Meilisearch
docker run -d -p 7700:7700 getmeili/meilisearch:latest

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动API服务
python -m uvicorn app.main:app --reload --port 8000
    """)


def main():
    print("""
================================================================
                    搜索引擎API演示
            基于Meilisearch的高性能搜索引擎
================================================================
    """)
    
    demo_service_status()
    demo_api_structure()
    demo_search_endpoints()
    demo_document_management()
    demo_index_settings()
    demo_deployment()
    
    print_separator("演示完成")
    print("""
访问API文档进行交互式测试:
   - Swagger UI:  http://127.0.0.1:8000/docs
   - ReDoc:       http://127.0.0.1:8000/redoc

下一步操作:
   1. 安装Docker Desktop（如果还没有）
   2. 运行 docker-compose up -d 启动完整服务
   3. 使用 examples.py 中的代码进行实际测试
    """)


if __name__ == "__main__":
    main()
