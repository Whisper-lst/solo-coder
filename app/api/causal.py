from fastapi import APIRouter, HTTPException, Query
from typing import Any, Dict, List, Optional
from app.models import (
    Entity,
    CausalRelation,
    CausalSearchRequest,
    CausalSearchResponse,
    CounterfactualRequest,
    EntitySearchRequest,
    RelationSearchRequest,
    KnowledgeGraphInfo,
    UserIntent
)
from app.causal.knowledge_graph import knowledge_graph_manager
from app.causal.causal_engine import causal_reasoning_engine
from app.causal.intent_analyzer import intent_analyzer
from app.causal.causal_search_service import causal_search_service

router = APIRouter(prefix="/causal", tags=["因果推理搜索"])


@router.post("/search", response_model=CausalSearchResponse)
async def causal_search(request: CausalSearchRequest) -> Dict[str, Any]:
    """
    执行因果推理搜索
    
    该接口结合传统搜索和因果推理，提供：
    - 用户意图理解与分析
    - 因果相关性评分
    - 相关实体发现
    - 因果路径分析
    - 可解释的搜索结果
    """
    try:
        result = causal_search_service.search(request)
        return result.model_dump(by_alias=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"因果搜索失败: {str(e)}")


@router.get("/search/quick")
async def quick_causal_search(
    q: str = Query(..., description="搜索查询"),
    index: str = Query("default", description="索引名称"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    include_causal_paths: bool = Query(True, alias="includeCausalPaths", description="包含因果路径"),
    max_causal_depth: int = Query(3, alias="maxCausalDepth", ge=1, le=5, description="最大因果深度"),
    intent_analysis: bool = Query(True, alias="intentAnalysis", description="启用意图分析")
) -> Dict[str, Any]:
    """
    快速因果搜索（GET方式）
    
    适用于简单的因果搜索场景
    """
    try:
        request = CausalSearchRequest(
            query=q,
            index=index,
            limit=limit,
            offset=offset,
            include_causal_paths=include_causal_paths,
            max_causal_depth=max_causal_depth,
            intent_analysis=intent_analysis
        )
        result = causal_search_service.search(request)
        return result.model_dump(by_alias=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"快速因果搜索失败: {str(e)}")


@router.post("/counterfactual")
async def counterfactual_reasoning(request: CounterfactualRequest) -> Dict[str, Any]:
    """
    执行反事实推理
    
    探索假设情景下的因果关系：
    - 分析假设事实对目标结果的影响
    - 发现因果路径
    - 探索替代方案
    - 评估结果概率
    
    示例：
    - 假设事实："我没有学习Python"
    - 目标结果："我能找到工作吗？"
    """
    try:
        result = causal_search_service.counterfactual_search(
            query=request.query,
            assume_fact=request.assume_fact,
            target_outcome=request.target_outcome,
            index=request.index,
            explore_paths=request.explore_paths,
            max_paths=request.max_paths
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"反事实推理失败: {str(e)}")


@router.post("/intent/analyze", response_model=UserIntent)
async def analyze_intent(
    query: str = Query(..., description="用户查询")
) -> Dict[str, Any]:
    """
    分析用户查询意图
    
    识别用户的真实需求和潜在目标：
    - 意图类型分类（信息查询、导航、交易、因果、反事实等）
    - 关键实体提取
    - 潜在需求识别
    - 置信度评估
    """
    try:
        intent = intent_analyzer.analyze(query)
        return intent.model_dump(by_alias=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"意图分析失败: {str(e)}")


@router.get("/intent/summary")
async def get_intent_summary(
    query: str = Query(..., description="用户查询")
) -> Dict[str, Any]:
    """
    获取意图分析摘要
    
    返回用户友好的意图分析结果和行动建议
    """
    try:
        intent = intent_analyzer.analyze(query)
        summary = intent_analyzer.generate_intent_summary(intent)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取意图摘要失败: {str(e)}")


@router.get("/graph/info", response_model=KnowledgeGraphInfo)
async def get_graph_info() -> Dict[str, Any]:
    """
    获取知识图谱统计信息
    
    返回：
    - 实体总数
    - 关系总数
    - 因果关系数量
    - 领域类型列表
    """
    try:
        info = knowledge_graph_manager.get_graph_info()
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取图谱信息失败: {str(e)}")


@router.post("/entities")
async def add_entity(entity: Entity) -> Dict[str, Any]:
    """
    添加实体到知识图谱
    
    实体是知识图谱的节点，代表现实世界中的事物
    """
    try:
        result = knowledge_graph_manager.add_entity(entity)
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加实体失败: {str(e)}")


@router.post("/entities/batch")
async def add_entities_batch(entities: List[Entity]) -> Dict[str, Any]:
    """
    批量添加实体
    """
    try:
        result = knowledge_graph_manager.add_entities_batch(entities)
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量添加实体失败: {str(e)}")


@router.get("/entities/{entity_id}")
async def get_entity(entity_id: str) -> Dict[str, Any]:
    """
    获取单个实体信息
    """
    try:
        entity = knowledge_graph_manager.get_entity(entity_id)
        if not entity:
            raise HTTPException(status_code=404, detail="实体不存在")
        return entity
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取实体失败: {str(e)}")


@router.post("/entities/search")
async def search_entities(request: EntitySearchRequest) -> Dict[str, Any]:
    """
    搜索实体
    
    按名称、类型或描述搜索知识图谱中的实体
    """
    try:
        results = knowledge_graph_manager.search_entities(
            query=request.query,
            entity_types=request.entity_types,
            limit=request.limit,
            offset=request.offset
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索实体失败: {str(e)}")


@router.delete("/entities/{entity_id}")
async def delete_entity(entity_id: str) -> Dict[str, Any]:
    """
    删除实体
    
    同时会删除与该实体相关的所有关系
    """
    try:
        result = knowledge_graph_manager.delete_entity(entity_id)
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除实体失败: {str(e)}")


@router.post("/relations")
async def add_relation(relation: CausalRelation) -> Dict[str, Any]:
    """
    添加关系到知识图谱
    
    关系是知识图谱的边，连接两个实体。
    支持因果关系类型：
    - causes: 导致
    - leads_to: 导致
    - enables: 使能够
    - prevents: 阻止
    - influences: 影响
    - requires: 需要
    - depends_on: 依赖于
    """
    try:
        result = knowledge_graph_manager.add_relation(relation)
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加关系失败: {str(e)}")


@router.post("/relations/batch")
async def add_relations_batch(relations: List[CausalRelation]) -> Dict[str, Any]:
    """
    批量添加关系
    """
    try:
        result = knowledge_graph_manager.add_relations_batch(relations)
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量添加关系失败: {str(e)}")


@router.post("/relations/search")
async def search_relations(request: RelationSearchRequest) -> Dict[str, Any]:
    """
    搜索关系
    
    按源实体、目标实体或关系类型搜索知识图谱中的关系
    """
    try:
        results = knowledge_graph_manager.search_relations(
            source_entity=request.source_entity,
            target_entity=request.target_entity,
            relation_types=request.relation_types,
            causal_only=request.causal_only,
            limit=request.limit,
            offset=request.offset
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索关系失败: {str(e)}")


@router.get("/entities/{entity_id}/outgoing")
async def get_outgoing_relations(
    entity_id: str,
    limit: int = Query(50, ge=1, le=200)
) -> Dict[str, Any]:
    """
    获取实体的出边关系
    
    返回从该实体出发的所有关系
    """
    try:
        relations = knowledge_graph_manager.get_outgoing_relations(entity_id, limit)
        return {"entityId": entity_id, "relations": relations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取出边关系失败: {str(e)}")


@router.get("/entities/{entity_id}/incoming")
async def get_incoming_relations(
    entity_id: str,
    limit: int = Query(50, ge=1, le=200)
) -> Dict[str, Any]:
    """
    获取实体的入边关系
    
    返回指向该实体的所有关系
    """
    try:
        relations = knowledge_graph_manager.get_incoming_relations(entity_id, limit)
        return {"entityId": entity_id, "relations": relations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取入边关系失败: {str(e)}")


@router.get("/causal-paths")
async def find_causal_paths(
    source: str = Query(..., description="源实体ID"),
    target: str = Query(..., description="目标实体ID"),
    max_depth: int = Query(3, ge=1, le=5, description="最大路径深度"),
    min_strength: float = Query(0.3, ge=0.0, le=1.0, description="最小关系强度")
) -> Dict[str, Any]:
    """
    发现因果路径
    
    查找从源实体到目标实体的所有因果路径
    """
    try:
        paths = causal_reasoning_engine.find_causal_paths(
            source_entity=source,
            target_entity=target,
            max_depth=max_depth,
            min_strength=min_strength
        )
        return {
            "sourceEntity": source,
            "targetEntity": target,
            "paths": [p.model_dump() for p in paths],
            "pathCount": len(paths)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发现因果路径失败: {str(e)}")


@router.get("/related-entities")
async def find_related_entities(
    entities: List[str] = Query(..., description="查询实体ID列表"),
    max_depth: int = Query(2, ge=1, le=4, description="最大搜索深度"),
    min_strength: float = Query(0.4, ge=0.0, le=1.0, description="最小关系强度")
) -> Dict[str, Any]:
    """
    发现相关实体
    
    基于因果链发现与查询实体相关的其他实体
    """
    try:
        related = causal_reasoning_engine.find_related_entities(
            query_entities=entities,
            max_depth=max_depth,
            min_strength=min_strength
        )
        return {
            "queryEntities": entities,
            "relatedEntities": related,
            "totalCount": len(related)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发现相关实体失败: {str(e)}")
