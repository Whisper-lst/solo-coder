from fastapi import APIRouter, HTTPException, Query
from typing import Any, Dict, List, Optional
from app.models import (
    SearchRequest,
    SearchResponse,
    MultiSearchRequest,
    MultiSearchResponse
)
from app.search.search_service import search_service

router = APIRouter(prefix="/search", tags=["搜索"])


@router.post("/", response_model=SearchResponse)
async def search(request: SearchRequest) -> Dict[str, Any]:
    """
    执行搜索请求
    
    支持以下功能：
    - 实时搜索（输入即搜）
    - 拼写错误容错
    - 混合搜索（关键词+语义）
    - 筛选与排序
    - 高亮显示
    - 分面搜索
    """
    try:
        results = search_service.search(request)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.post("/multi", response_model=MultiSearchResponse)
async def multi_search(request: MultiSearchRequest) -> Dict[str, Any]:
    """
    执行多索引搜索
    
    在单个请求中搜索多个索引
    """
    try:
        results = search_service.multi_search(request.queries)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"多索引搜索失败: {str(e)}")


@router.get("/quick")
async def quick_search(
    q: str = Query(..., description="搜索关键词"),
    index: str = Query("default", description="索引名称"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    filter: Optional[str] = Query(None, description="筛选条件"),
    sort: Optional[List[str]] = Query(None, description="排序条件"),
) -> Dict[str, Any]:
    """
    快速搜索接口（GET方式）
    
    适用于简单的搜索场景，支持实时搜索
    """
    try:
        request = SearchRequest(
            query=q,
            index=index,
            limit=limit,
            offset=offset,
            filter=filter,
            sort=sort
        )
        results = search_service.search(request)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"快速搜索失败: {str(e)}")


@router.get("/suggest")
async def search_suggestions(
    q: str = Query(..., description="搜索关键词"),
    index: str = Query("default", description="索引名称"),
    limit: int = Query(5, ge=1, le=20, description="返回数量"),
) -> Dict[str, Any]:
    """
    搜索建议接口
    
    提供输入即搜的自动补全功能
    """
    try:
        request = SearchRequest(
            query=q,
            index=index,
            limit=limit,
            attributes_to_retrieve=["id", "title"],
            attributes_to_highlight=["*"]
        )
        results = search_service.search(request)
        return {
            "query": q,
            "suggestions": [
                {
                    "id": hit.get("id"),
                    "text": hit.get("_formatted", hit).get("title") or hit.get("title") or str(hit.get("id"))
                }
                for hit in results.get("hits", [])
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取搜索建议失败: {str(e)}")
