from fastapi import APIRouter, HTTPException, Query
from typing import Any, Dict, Optional
from app.search.client import search_client

router = APIRouter(prefix="/tasks", tags=["任务管理"])


@router.get("/")
async def list_tasks(
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    from_: Optional[int] = Query(None, alias="from", description="起始任务ID"),
    status: Optional[str] = Query(None, description="任务状态筛选"),
    task_type: Optional[str] = Query(None, description="任务类型筛选"),
    index_uid: Optional[str] = Query(None, description="索引UID筛选")
) -> Dict[str, Any]:
    """
    列出所有任务
    """
    try:
        params = {"limit": limit}
        if from_:
            params["from"] = from_
        if status:
            params["status"] = status
        if task_type:
            params["type"] = task_type
        if index_uid:
            params["indexUid"] = index_uid
        
        tasks = search_client.client.get_tasks(params)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务列表失败: {str(e)}")


@router.get("/{task_uid}")
async def get_task(task_uid: int) -> Dict[str, Any]:
    """
    获取单个任务信息
    """
    try:
        task = search_client.get_task(task_uid)
        return task
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"任务不存在: {str(e)}")


@router.post("/{task_uid}/wait")
async def wait_for_task(
    task_uid: int,
    timeout: int = Query(5000, ge=1000, le=60000, description="超时时间（毫秒）")
) -> Dict[str, Any]:
    """
    等待任务完成
    
    阻塞直到任务完成或超时
    """
    try:
        task = search_client.wait_for_task(task_uid, timeout)
        return task
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"等待任务失败: {str(e)}")


@router.delete("/{task_uid}")
async def cancel_task(task_uid: int) -> Dict[str, Any]:
    """
    取消任务
    """
    try:
        task = search_client.client.cancel_tasks({"uids": [task_uid]})
        return {"task_uid": task.task_uid, "status": "enqueued"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取消任务失败: {str(e)}")
