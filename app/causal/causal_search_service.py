from typing import Any, Dict, List, Optional
import time
from app.causal.knowledge_graph import knowledge_graph_manager
from app.causal.causal_engine import causal_reasoning_engine
from app.causal.intent_analyzer import intent_analyzer
from app.search.search_service import search_service
from app.models import (
    CausalSearchRequest,
    CausalSearchResponse,
    CausalSearchResult,
    SearchRequest,
    SearchResult,
    UserIntent
)


class CausalSearchService:
    def __init__(self):
        self.kg = knowledge_graph_manager
        self.causal_engine = causal_reasoning_engine
        self.intent_analyzer = intent_analyzer
        self.base_search = search_service
    
    def search(self, request: CausalSearchRequest) -> CausalSearchResponse:
        start_time = time.time()
        
        user_intent = None
        if request.intent_analysis:
            user_intent = self.intent_analyzer.analyze(request.query)
        
        query_entities = []
        if user_intent:
            query_entities = user_intent.query_entities
        
        if not query_entities:
            query_entities = self._extract_entities_from_query(request.query)
        
        base_request = SearchRequest(
            query=request.query,
            index=request.index,
            limit=request.limit * 2,
            offset=request.offset,
            filter=request.filter,
            sort=request.sort
        )
        
        base_results = self.base_search.search(base_request)
        
        causal_results = []
        for hit in base_results.get("hits", []):
            search_result = SearchResult(**hit)
            
            causal_relevance = self._calculate_causal_relevance(
                search_result, query_entities, request
            )
            
            related_entities = self._find_document_related_entities(
                search_result, query_entities, request
            )
            
            causal_paths = None
            if request.include_causal_paths and query_entities:
                causal_paths = self._find_document_causal_paths(
                    search_result, query_entities, request
                )
            
            explanation = self._generate_causal_explanation(
                search_result, causal_relevance, related_entities, causal_paths
            )
            
            causal_result = CausalSearchResult(
                document=search_result,
                causal_relevance=causal_relevance,
                related_entities=[e.get("entityName", "") for e in related_entities[:5]],
                causal_paths=causal_paths if causal_paths else None,
                explanation=explanation
            )
            
            causal_results.append(causal_result)
        
        causal_results.sort(key=lambda x: (x.causal_relevance, x.document.score or 0), reverse=True)
        
        limited_results = causal_results[request.offset:request.offset + request.limit]
        
        related_entities_info = []
        if request.explore_related_entities and query_entities:
            related_entities_info = self.causal_engine.find_related_entities(
                query_entities,
                max_depth=request.max_causal_depth
            )
        
        causal_insights = self.causal_engine.generate_causal_insights(
            request.query, query_entities
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return CausalSearchResponse(
            query=request.query,
            user_intent=user_intent,
            hits=limited_results,
            related_entities=related_entities_info[:10] if related_entities_info else [],
            causal_insights=causal_insights,
            processing_time_ms=processing_time,
            limit=request.limit,
            offset=request.offset
        )
    
    def _extract_entities_from_query(self, query: str) -> List[str]:
        search_results = self.kg.search_entities(query, limit=5)
        entities = []
        for hit in search_results.get("hits", []):
            entity_id = hit.get("id")
            if entity_id:
                entities.append(entity_id)
        return entities
    
    def _calculate_causal_relevance(
        self,
        document: SearchResult,
        query_entities: List[str],
        request: CausalSearchRequest
    ) -> float:
        base_score = document.score or 0.5
        
        if not query_entities:
            return base_score * 0.5
        
        causal_score = 0.0
        doc_text = f"{document.title or ''} {document.content or ''}".lower()
        
        for entity in query_entities:
            entity_info = self.kg.get_entity(entity)
            if entity_info:
                entity_name = entity_info.get("name", entity).lower()
                if entity_name in doc_text:
                    causal_score += 0.2
                
                aliases = entity_info.get("aliases", [])
                for alias in aliases:
                    if alias.lower() in doc_text:
                        causal_score += 0.1
        
        outgoing = []
        for entity in query_entities:
            relations = self.kg.get_outgoing_relations(entity, limit=10)
            outgoing.extend(relations)
        
        for rel in outgoing:
            target_name = rel.get("targetEntity", "").lower()
            if target_name in doc_text:
                causal_score += rel.get("strength", 0.3) * 0.15
        
        incoming = []
        for entity in query_entities:
            relations = self.kg.get_incoming_relations(entity, limit=10)
            incoming.extend(relations)
        
        for rel in incoming:
            source_name = rel.get("sourceEntity", "").lower()
            if source_name in doc_text:
                causal_score += rel.get("strength", 0.3) * 0.1
        
        combined_score = (base_score * 0.5) + (causal_score * 0.5)
        
        return min(combined_score, 1.0)
    
    def _find_document_related_entities(
        self,
        document: SearchResult,
        query_entities: List[str],
        request: CausalSearchRequest
    ) -> List[Dict[str, Any]]:
        if not query_entities:
            return []
        
        related = []
        doc_text = f"{document.title or ''} {document.content or ''}".lower()
        
        for entity in query_entities:
            chains = self.kg.build_causal_chain(
                entity,
                max_depth=request.max_causal_depth,
                min_strength=0.3
            )
            
            for chain in chains:
                end_entity = chain["endEntity"]
                entity_info = self.kg.get_entity(end_entity)
                
                if entity_info:
                    entity_name = entity_info.get("name", end_entity).lower()
                    if entity_name in doc_text:
                        related.append({
                            "entityId": end_entity,
                            "entityName": entity_info.get("name", end_entity),
                            "entityType": entity_info.get("entityType", "unknown"),
                            "strength": chain["totalStrength"]
                        })
        
        related.sort(key=lambda x: x["strength"], reverse=True)
        return related[:10]
    
    def _find_document_causal_paths(
        self,
        document: SearchResult,
        query_entities: List[str],
        request: CausalSearchRequest
    ) -> List[Dict[str, Any]]:
        if not query_entities:
            return []
        
        doc_text = f"{document.title or ''} {document.content or ''}".lower()
        doc_entities = self._extract_entities_from_query(doc_text)
        
        all_paths = []
        
        for query_entity in query_entities[:2]:
            for doc_entity in doc_entities[:3]:
                if query_entity == doc_entity:
                    continue
                
                paths = self.causal_engine.find_causal_paths(
                    query_entity,
                    doc_entity,
                    max_depth=request.max_causal_depth,
                    min_strength=0.3
                )
                
                for path in paths[:2]:
                    all_paths.append(path.model_dump())
        
        all_paths.sort(key=lambda x: x.get("totalStrength", 0), reverse=True)
        return all_paths[:5]
    
    def _generate_causal_explanation(
        self,
        document: SearchResult,
        causal_relevance: float,
        related_entities: List[Dict[str, Any]],
        causal_paths: Optional[List[Dict[str, Any]]]
    ) -> str:
        explanation_parts = []
        
        if causal_relevance >= 0.7:
            explanation_parts.append("这份文档与查询具有高度因果相关性。")
        elif causal_relevance >= 0.5:
            explanation_parts.append("这份文档与查询具有中等因果相关性。")
        else:
            explanation_parts.append("这份文档与查询的因果相关性较低。")
        
        if related_entities:
            entity_names = [e.get("entityName", "") for e in related_entities[:3]]
            explanation_parts.append(f"发现相关实体：{', '.join(entity_names)}。")
        
        if causal_paths:
            path_count = len(causal_paths)
            explanation_parts.append(f"发现 {path_count} 条因果路径。")
            
            for i, path in enumerate(causal_paths[:2]):
                explanation_parts.append(f"路径 {i+1}: {path.get('explanation', '')}")
        
        return " ".join(explanation_parts)
    
    def counterfactual_search(
        self,
        query: str,
        assume_fact: str,
        target_outcome: str,
        index: str = "default",
        explore_paths: bool = True,
        max_paths: int = 5
    ) -> Dict[str, Any]:
        original_fact = query or "当前事实"
        
        result = self.causal_engine.counterfactual_reasoning(
            original_fact=original_fact,
            assumed_fact=assume_fact,
            target_outcome=target_outcome,
            explore_paths=explore_paths,
            max_paths=max_paths
        )
        
        related_docs = []
        if result.causal_paths:
            entities_to_search = set()
            for path in result.causal_paths:
                for entity in path.entities:
                    entities_to_search.add(entity)
            
            if entities_to_search:
                search_query = " ".join(list(entities_to_search)[:3])
                base_request = SearchRequest(
                    query=search_query,
                    index=index,
                    limit=10
                )
                search_results = self.base_search.search(base_request)
                related_docs = search_results.get("hits", [])
        
        return {
            "result": result.model_dump(),
            "relatedDocuments": related_docs[:5]
        }


causal_search_service = CausalSearchService()
