from fastapi import APIRouter, HTTPException, Query
from typing import Any, Dict, List, Optional, Union
from app.models import Document, BatchDocumentRequest, TaskInfo
from app.search.document import document_manager
from app.search.client import search_client

router = APIRouter(prefix="/documents", tags=["文档管理"])


@router.post("/{index_uid}")
async def add_documents(
    index_uid: str,
    documents: List[Dict[str, Any]],
    primary_key: Optional[str] = Query(None, description="主键字段名")
) -> Dict[str, Any]:
    """
    添加或更新文档
    
    如果文档ID已存在，则更新该文档
    """
    try:
        task = document_manager.add_documents(index_uid, documents, primary_key)
        return {"task_uid": task.task_uid, "status": "enqueued", "index_uid": index_uid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加文档失败: {str(e)}")


@router.put("/{index_uid}")
async def update_documents(
    index_uid: str,
    documents: List[Dict[str, Any]],
    primary_key: Optional[str] = Query(None, description="主键字段名")
) -> Dict[str, Any]:
    """
    部分更新文档
    
    只更新文档中存在的字段，其他字段保持不变
    """
    try:
        task = document_manager.update_documents(index_uid, documents, primary_key)
        return {"task_uid": task.task_uid, "status": "enqueued", "index_uid": index_uid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新文档失败: {str(e)}")


@router.get("/{index_uid}/{document_id}")
async def get_document(
    index_uid: str,
    document_id: Union[str, int],
    fields: Optional[List[str]] = Query(None, description="要返回的字段列表")
) -> Dict[str, Any]:
    """
    获取单个文档
    """
    try:
        document = document_manager.get_document(index_uid, document_id, fields)
        return document
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"文档不存在: {str(e)}")


@router.get("/{index_uid}")
async def list_documents(
    index_uid: str,
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    fields: Optional[List[str]] = Query(None, description="要返回的字段列表"),
    filter: Optional[str] = Query(None, description="筛选条件")
) -> Dict[str, Any]:
    """
    列出索引中的文档
    """
    try:
        documents = document_manager.get_documents(
            index_uid, limit, offset, fields, filter
        )
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文档列表失败: {str(e)}")


@router.delete("/{index_uid}/{document_id}")
async def delete_document(
    index_uid: str,
    document_id: Union[str, int]
) -> Dict[str, Any]:
    """
    删除单个文档
    """
    try:
        task = document_manager.delete_document(index_uid, document_id)
        return {"task_uid": task.task_uid, "status": "enqueued", "index_uid": index_uid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除文档失败: {str(e)}")


@router.delete("/{index_uid}")
async def delete_documents_batch(
    index_uid: str,
    document_ids: List[Union[str, int]]
) -> Dict[str, Any]:
    """
    批量删除文档
    """
    try:
        task = document_manager.delete_documents(index_uid, document_ids)
        return {"task_uid": task.task_uid, "status": "enqueued", "index_uid": index_uid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量删除文档失败: {str(e)}")


@router.delete("/{index_uid}/all")
async def delete_all_documents(index_uid: str) -> Dict[str, Any]:
    """
    删除索引中的所有文档
    """
    try:
        task = document_manager.delete_all_documents(index_uid)
        return {"task_uid": task.task_uid, "status": "enqueued", "index_uid": index_uid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空文档失败: {str(e)}")
