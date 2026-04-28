from fastapi import APIRouter, HTTPException, Query
from typing import Any, Dict, Optional
from app.search.client import search_client

router = APIRouter(prefix="/indexes", tags=["索引管理"])


@router.get("/")
async def list_indexes() -> Dict[str, Any]:
    """
    列出所有索引
    """
    try:
        indexes = search_client.get_indexes()
        return indexes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取索引列表失败: {str(e)}")


@router.post("/{uid}")
async def create_index(
    uid: str,
    primary_key: Optional[str] = Query(None, description="主键字段名")
) -> Dict[str, Any]:
    """
    创建新索引
    """
    try:
        task = search_client.create_index(uid, primary_key)
        return {"task_uid": task.task_uid, "status": "enqueued", "index_uid": uid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建索引失败: {str(e)}")


@router.get("/{uid}")
async def get_index(uid: str) -> Dict[str, Any]:
    """
    获取索引信息
    """
    try:
        index_info = search_client.get_index_info(uid)
        return index_info
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"索引不存在: {str(e)}")


@router.delete("/{uid}")
async def delete_index(uid: str) -> Dict[str, Any]:
    """
    删除索引
    """
    try:
        task = search_client.delete_index(uid)
        return {"task_uid": task.task_uid, "status": "enqueued", "index_uid": uid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除索引失败: {str(e)}")
