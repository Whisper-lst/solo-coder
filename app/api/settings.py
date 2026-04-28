from fastapi import APIRouter, HTTPException
from typing import Any, Dict, List, Optional
from app.models import IndexSettings
from app.search.index_settings import index_settings_manager

router = APIRouter(prefix="/settings", tags=["索引设置"])


@router.get("/{index_uid}")
async def get_settings(index_uid: str) -> Dict[str, Any]:
    """
    获取索引设置
    """
    try:
        settings = index_settings_manager.get_settings(index_uid)
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取设置失败: {str(e)}")


@router.patch("/{index_uid}")
async def update_settings(index_uid: str, settings: IndexSettings) -> Dict[str, Any]:
    """
    更新索引设置
    """
    try:
        settings_dict = settings.model_dump(exclude_none=True, by_alias=True)
        task = index_settings_manager.update_settings(index_uid, settings_dict)
        return {"task_uid": task.task_uid, "status": "enqueued", "index_uid": index_uid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新设置失败: {str(e)}")


@router.delete("/{index_uid}")
async def reset_settings(index_uid: str) -> Dict[str, Any]:
    """
    重置索引设置为默认值
    """
    try:
        task = index_settings_manager.reset_settings(index_uid)
        return {"task_uid": task.task_uid, "status": "enqueued", "index_uid": index_uid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重置设置失败: {str(e)}")


@router.put("/{index_uid}/filterable-attributes")
async def update_filterable_attributes(
    index_uid: str,
    attributes: List[str]
) -> Dict[str, Any]:
    """
    更新可筛选属性
    
    只有配置为可筛选的属性才能在搜索时使用filter参数
    """
    try:
        task = index_settings_manager.update_filterable_attributes(index_uid, attributes)
        return {"task_uid": task.task_uid, "status": "enqueued", "index_uid": index_uid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新可筛选属性失败: {str(e)}")


@router.put("/{index_uid}/sortable-attributes")
async def update_sortable_attributes(
    index_uid: str,
    attributes: List[str]
) -> Dict[str, Any]:
    """
    更新可排序属性
    
    只有配置为可排序的属性才能在搜索时使用sort参数
    """
    try:
        task = index_settings_manager.update_sortable_attributes(index_uid, attributes)
        return {"task_uid": task.task_uid, "status": "enqueued", "index_uid": index_uid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新可排序属性失败: {str(e)}")


@router.put("/{index_uid}/searchable-attributes")
async def update_searchable_attributes(
    index_uid: str,
    attributes: List[str]
) -> Dict[str, Any]:
    """
    更新可搜索属性
    
    配置哪些属性用于搜索，属性的顺序影响相关性评分
    """
    try:
        task = index_settings_manager.update_searchable_attributes(index_uid, attributes)
        return {"task_uid": task.task_uid, "status": "enqueued", "index_uid": index_uid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新可搜索属性失败: {str(e)}")


@router.put("/{index_uid}/synonyms")
async def update_synonyms(
    index_uid: str,
    synonyms: Dict[str, List[str]]
) -> Dict[str, Any]:
    """
    更新同义词
    
    配置同义词关系，例如: {"car": ["automobile", "vehicle"]}
    """
    try:
        task = index_settings_manager.update_synonyms(index_uid, synonyms)
        return {"task_uid": task.task_uid, "status": "enqueued", "index_uid": index_uid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新同义词失败: {str(e)}")


@router.put("/{index_uid}/stop-words")
async def update_stop_words(
    index_uid: str,
    stop_words: List[str]
) -> Dict[str, Any]:
    """
    更新停用词
    
    配置在搜索时忽略的词汇，例如: ["the", "a", "an"]
    """
    try:
        task = index_settings_manager.update_stop_words(index_uid, stop_words)
        return {"task_uid": task.task_uid, "status": "enqueued", "index_uid": index_uid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新停用词失败: {str(e)}")


@router.put("/{index_uid}/typo-tolerance")
async def update_typo_tolerance(
    index_uid: str,
    typo_tolerance: Dict[str, Any]
) -> Dict[str, Any]:
    """
    更新拼写错误容错设置
    
    配置拼写错误容错的行为
    """
    try:
        task = index_settings_manager.update_typo_tolerance(index_uid, typo_tolerance)
        return {"task_uid": task.task_uid, "status": "enqueued", "index_uid": index_uid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新拼写容错设置失败: {str(e)}")


@router.put("/{index_uid}/ranking-rules")
async def update_ranking_rules(
    index_uid: str,
    rules: List[str]
) -> Dict[str, Any]:
    """
    更新排序规则
    
    配置搜索结果的相关性排序规则
    """
    try:
        task = index_settings_manager.update_ranking_rules(index_uid, rules)
        return {"task_uid": task.task_uid, "status": "enqueued", "index_uid": index_uid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新排序规则失败: {str(e)}")


@router.put("/{index_uid}/embedders")
async def update_embedders(
    index_uid: str,
    embedders: Dict[str, Any]
) -> Dict[str, Any]:
    """
    更新嵌入器配置
    
    配置用于语义搜索的嵌入器，支持混合搜索
    """
    try:
        task = index_settings_manager.update_embedders(index_uid, embedders)
        return {"task_uid": task.task_uid, "status": "enqueued", "index_uid": index_uid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新嵌入器配置失败: {str(e)}")
