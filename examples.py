"""
搜索引擎API使用示例
=====================

这是一个完整的使用示例，展示如何使用搜索引擎API的各种功能。
"""

import httpx
import json

API_BASE_URL = "http://localhost:8000/api/v1"


def example_basic_search():
    """基本搜索示例"""
    print("=" * 50)
    print("1. 基本搜索示例")
    print("=" * 50)
    
    query = {
        "query": "python",
        "index": "documents",
        "limit": 10,
        "attributes_to_highlight": ["title", "content"]
    }
    
    with httpx.Client() as client:
        response = client.post(f"{API_BASE_URL}/search/", json=query)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"查询: {result['query']}")
            print(f"处理时间: {result['processing_time_ms']}ms")
            print(f"结果数量: {len(result['hits'])}")
            for hit in result['hits'][:3]:
                print(f"  - {hit.get('title', 'N/A')}")
    print()


def example_typo_tolerance():
    """拼写错误容错示例"""
    print("=" * 50)
    print("2. 拼写错误容错示例")
    print("=" * 50)
    
    query = {
        "query": "phyton",
        "index": "documents",
        "limit": 5
    }
    
    with httpx.Client() as client:
        response = client.post(f"{API_BASE_URL}/search/", json=query)
        print(f"查询: 'phyton' (拼写错误)")
        if response.status_code == 200:
            result = response.json()
            print(f"找到 {len(result['hits'])} 个结果 (自动纠错)")
            for hit in result['hits'][:3]:
                print(f"  - {hit.get('title', 'N/A')}")
    print()


def example_filter_search():
    """带筛选的搜索示例"""
    print("=" * 50)
    print("3. 带筛选的搜索示例")
    print("=" * 50)
    
    query = {
        "query": "programming",
        "index": "documents",
        "limit": 10,
        "filter": "category = 'tech' AND rating > 4",
        "sort": ["rating:desc"]
    }
    
    with httpx.Client() as client:
        response = client.post(f"{API_BASE_URL}/search/", json=query)
        print(f"筛选条件: category = 'tech' AND rating > 4")
        print(f"排序: rating 降序")
        if response.status_code == 200:
            result = response.json()
            print(f"找到 {len(result['hits'])} 个结果")
            for hit in result['hits'][:3]:
                print(f"  - {hit.get('title', 'N/A')} (评分: {hit.get('rating', 'N/A')})")
    print()


def example_faceted_search():
    """分面搜索示例"""
    print("=" * 50)
    print("4. 分面搜索示例")
    print("=" * 50)
    
    query = {
        "query": "tutorial",
        "index": "documents",
        "limit": 10,
        "facets": ["category", "language", "difficulty"]
    }
    
    with httpx.Client() as client:
        response = client.post(f"{API_BASE_URL}/search/", json=query)
        if response.status_code == 200:
            result = response.json()
            print("分面统计:")
            facets = result.get('facet_distribution', {})
            for facet_name, values in facets.items():
                print(f"  {facet_name}:")
                for value, count in list(values.items())[:5]:
                    print(f"    - {value}: {count}")
    print()


def example_quick_search():
    """快速搜索示例 (GET方式)"""
    print("=" * 50)
    print("5. 快速搜索示例 (GET方式)")
    print("=" * 50)
    
    with httpx.Client() as client:
        params = {
            "q": "machine learning",
            "index": "documents",
            "limit": 5
        }
        response = client.get(f"{API_BASE_URL}/search/quick", params=params)
        if response.status_code == 200:
            result = response.json()
            print(f"查询: 'machine learning'")
            print(f"找到 {len(result['hits'])} 个结果")
            for hit in result['hits']:
                print(f"  - {hit.get('title', 'N/A')}")
    print()


def example_add_documents():
    """添加文档示例"""
    print("=" * 50)
    print("6. 添加文档示例")
    print("=" * 50)
    
    documents = [
        {
            "id": 1,
            "title": "Python 编程入门教程",
            "content": "这是一个关于Python编程的完整教程，涵盖基础语法、数据结构和高级特性。",
            "category": "tech",
            "language": "zh",
            "rating": 4.8,
            "difficulty": "beginner"
        },
        {
            "id": 2,
            "title": "Machine Learning with Python",
            "content": "Learn machine learning concepts and implementations using Python and popular libraries.",
            "category": "tech",
            "language": "en",
            "rating": 4.9,
            "difficulty": "intermediate"
        },
        {
            "id": 3,
            "title": "JavaScript 前端开发指南",
            "content": "现代JavaScript前端开发技术，包括React、Vue和Angular框架。",
            "category": "tech",
            "language": "zh",
            "rating": 4.5,
            "difficulty": "intermediate"
        }
    ]
    
    with httpx.Client() as client:
        response = client.post(f"{API_BASE_URL}/documents/documents", json=documents)
        if response.status_code == 200:
            result = response.json()
            print(f"文档添加任务已创建: task_uid = {result['task_uid']}")
            print(f"状态: {result['status']}")
    print()


def example_search_suggestions():
    """搜索建议示例"""
    print("=" * 50)
    print("7. 搜索建议示例 (输入即搜)")
    print("=" * 50)
    
    with httpx.Client() as client:
        params = {
            "q": "pyth",
            "index": "documents",
            "limit": 5
        }
        response = client.get(f"{API_BASE_URL}/search/suggest", params=params)
        if response.status_code == 200:
            result = response.json()
            print(f"输入: 'pyth'")
            print(f"建议:")
            for suggestion in result.get('suggestions', []):
                print(f"  - {suggestion.get('text', 'N/A')}")
    print()


def example_setup_synonyms():
    """配置同义词示例"""
    print("=" * 50)
    print("8. 配置同义词示例")
    print("=" * 50)
    
    synonyms = {
        "python": ["py", "python3", "蟒"],
        "javascript": ["js", "es", "ecmascript"],
        "machine learning": ["ml", "ai", "机器学习", "人工智能"]
    }
    
    with httpx.Client() as client:
        response = client.put(
            f"{API_BASE_URL}/settings/documents/synonyms",
            json=synonyms
        )
        if response.status_code == 200:
            result = response.json()
            print(f"同义词配置任务已创建: task_uid = {result['task_uid']}")
            print("配置的同义词:")
            for word, syn_list in synonyms.items():
                print(f"  {word}: {', '.join(syn_list)}")
    print()


def example_hybrid_search():
    """混合搜索示例 (关键词 + 语义)"""
    print("=" * 50)
    print("9. 混合搜索示例 (关键词 + 语义)")
    print("=" * 50)
    
    query = {
        "query": "如何学习编程",
        "index": "documents",
        "limit": 10,
        "hybrid": True,
        "semantic_ratio": 0.5,
        "embedder": "default"
    }
    
    print("注意: 混合搜索需要先配置嵌入器(embedder)")
    print(f"查询: {query['query']}")
    print(f"混合模式: 关键词({1-query['semantic_ratio']}) + 语义({query['semantic_ratio']})")
    print()


def example_multi_search():
    """多索引搜索示例"""
    print("=" * 50)
    print("10. 多索引搜索示例")
    print("=" * 50)
    
    query = {
        "queries": [
            {
                "query": "python",
                "index": "documents",
                "limit": 3
            },
            {
                "query": "javascript",
                "index": "articles",
                "limit": 3
            }
        ]
    }
    
    print("同时搜索 'documents' 和 'articles' 两个索引")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("搜索引擎API使用示例")
    print("=" * 60)
    print()
    
    print("确保服务已启动:")
    print("  docker-compose up -d")
    print("或")
    print("  pip install -r requirements.txt")
    print("  启动 Meilisearch: docker run -p 7700:7700 getmeili/meilisearch")
    print("  python -m uvicorn app.main:app --reload")
    print()
    
    example_add_documents()
    example_basic_search()
    example_typo_tolerance()
    example_filter_search()
    example_faceted_search()
    example_quick_search()
    example_search_suggestions()
    example_setup_synonyms()
    example_hybrid_search()
    example_multi_search()
    
    print("=" * 60)
    print("示例执行完成!")
    print("=" * 60)
