from typing import Any, Dict, List, Optional, Set
import uuid
from app.search.client import search_client
from app.models import Entity, CausalRelation


ENTITY_INDEX = "kg_entities"
RELATION_INDEX = "kg_relations"


class KnowledgeGraphManager:
    def __init__(self):
        self.client = search_client
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        try:
            entity_index = self.client.get_index(ENTITY_INDEX)
        except Exception:
            self.client.create_index(ENTITY_INDEX, primary_key="id")
        
        try:
            relation_index = self.client.get_index(RELATION_INDEX)
        except Exception:
            self.client.create_index(RELATION_INDEX, primary_key="id")
        
        self._configure_index_settings()
    
    def _configure_index_settings(self):
        try:
            entity_index = self.client.get_index(ENTITY_INDEX)
            entity_index.update_filterable_attributes([
                "entityType", "name", "aliases"
            ])
            entity_index.update_searchable_attributes([
                "name", "description", "aliases"
            ])
            
            relation_index = self.client.get_index(RELATION_INDEX)
            relation_index.update_filterable_attributes([
                "sourceEntity", "targetEntity", "relationType", 
                "causalDirection", "isDirect", "strength"
            ])
            relation_index.update_searchable_attributes([
                "sourceEntity", "targetEntity", "relationType", "evidence"
            ])
        except Exception:
            pass
    
    def add_entity(self, entity: Entity) -> Dict[str, Any]:
        entity_dict = entity.model_dump(by_alias=True, exclude_none=True)
        if "id" not in entity_dict or not entity_dict["id"]:
            entity_dict["id"] = f"entity_{uuid.uuid4().hex[:12]}"
        
        index = self.client.get_index(ENTITY_INDEX)
        task = index.add_documents([entity_dict])
        return {"task_uid": task.task_uid, "entity_id": entity_dict["id"]}
    
    def add_entities_batch(self, entities: List[Entity]) -> Dict[str, Any]:
        entity_dicts = []
        for entity in entities:
            entity_dict = entity.model_dump(by_alias=True, exclude_none=True)
            if "id" not in entity_dict or not entity_dict["id"]:
                entity_dict["id"] = f"entity_{uuid.uuid4().hex[:12]}"
            entity_dicts.append(entity_dict)
        
        index = self.client.get_index(ENTITY_INDEX)
        task = index.add_documents(entity_dicts)
        return {"task_uid": task.task_uid}
    
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        try:
            index = self.client.get_index(ENTITY_INDEX)
            document = index.get_document(entity_id)
            return document
        except Exception:
            return None
    
    def search_entities(
        self,
        query: str,
        entity_types: Optional[List[str]] = None,
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        index = self.client.get_index(ENTITY_INDEX)
        
        search_params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset
        }
        
        if entity_types:
            type_filters = [f"entityType = '{t}'" for t in entity_types]
            search_params["filter"] = " OR ".join(type_filters)
        
        results = index.search(query, search_params)
        return results
    
    def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        updates["id"] = entity_id
        index = self.client.get_index(ENTITY_INDEX)
        task = index.update_documents([updates])
        return {"task_uid": task.task_uid}
    
    def delete_entity(self, entity_id: str) -> Dict[str, Any]:
        index = self.client.get_index(ENTITY_INDEX)
        task = index.delete_document(entity_id)
        self._delete_relations_for_entity(entity_id)
        return {"task_uid": task.task_uid}
    
    def _delete_relations_for_entity(self, entity_id: str):
        try:
            index = self.client.get_index(RELATION_INDEX)
            index.delete_documents_by_filter(
                f"sourceEntity = '{entity_id}' OR targetEntity = '{entity_id}'"
            )
        except Exception:
            pass
    
    def add_relation(self, relation: CausalRelation) -> Dict[str, Any]:
        relation_dict = relation.model_dump(by_alias=True, exclude_none=True)
        if "id" not in relation_dict or not relation_dict["id"]:
            relation_dict["id"] = f"relation_{uuid.uuid4().hex[:12]}"
        
        index = self.client.get_index(RELATION_INDEX)
        task = index.add_documents([relation_dict])
        return {"task_uid": task.task_uid, "relation_id": relation_dict["id"]}
    
    def add_relations_batch(self, relations: List[CausalRelation]) -> Dict[str, Any]:
        relation_dicts = []
        for relation in relations:
            relation_dict = relation.model_dump(by_alias=True, exclude_none=True)
            if "id" not in relation_dict or not relation_dict["id"]:
                relation_dict["id"] = f"relation_{uuid.uuid4().hex[:12]}"
            relation_dicts.append(relation_dict)
        
        index = self.client.get_index(RELATION_INDEX)
        task = index.add_documents(relation_dicts)
        return {"task_uid": task.task_uid}
    
    def get_relation(self, relation_id: str) -> Optional[Dict[str, Any]]:
        try:
            index = self.client.get_index(RELATION_INDEX)
            document = index.get_document(relation_id)
            return document
        except Exception:
            return None
    
    def search_relations(
        self,
        source_entity: Optional[str] = None,
        target_entity: Optional[str] = None,
        relation_types: Optional[List[str]] = None,
        causal_only: bool = False,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        index = self.client.get_index(RELATION_INDEX)
        
        search_params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset
        }
        
        filters = []
        
        if source_entity:
            filters.append(f"sourceEntity = '{source_entity}'")
        
        if target_entity:
            filters.append(f"targetEntity = '{target_entity}'")
        
        if relation_types:
            type_filters = [f"relationType = '{t}'" for t in relation_types]
            filters.append(f"({' OR '.join(type_filters)})")
        
        if causal_only:
            causal_types = ["causes", "leads_to", "results_in", "enables", "prevents", "influences"]
            causal_filters = [f"relationType = '{t}'" for t in causal_types]
            filters.append(f"({' OR '.join(causal_filters)})")
        
        if filters:
            search_params["filter"] = " AND ".join(filters)
        
        results = index.search("", search_params)
        return results
    
    def get_outgoing_relations(self, entity_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        results = self.search_relations(source_entity=entity_id, limit=limit)
        return results.get("hits", [])
    
    def get_incoming_relations(self, entity_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        results = self.search_relations(target_entity=entity_id, limit=limit)
        return results.get("hits", [])
    
    def delete_relation(self, relation_id: str) -> Dict[str, Any]:
        index = self.client.get_index(RELATION_INDEX)
        task = index.delete_document(relation_id)
        return {"task_uid": task.task_uid}
    
    def get_graph_info(self) -> Dict[str, Any]:
        try:
            entity_index = self.client.get_index(ENTITY_INDEX)
            entity_stats = entity_index.get_stats()
            entity_count = entity_stats.get("numberOfDocuments", 0)
            
            relation_index = self.client.get_index(RELATION_INDEX)
            relation_stats = relation_index.get_stats()
            relation_count = relation_stats.get("numberOfDocuments", 0)
            
            causal_results = self.search_relations(causal_only=True, limit=1)
            causal_count = causal_results.get("estimatedTotalHits", 0)
            
            entity_types = self._get_distinct_entity_types()
            
            return {
                "entityCount": entity_count,
                "relationCount": relation_count,
                "causalRelationCount": causal_count,
                "domainTypes": entity_types
            }
        except Exception as e:
            return {
                "entityCount": 0,
                "relationCount": 0,
                "causalRelationCount": 0,
                "domainTypes": [],
                "error": str(e)
            }
    
    def _get_distinct_entity_types(self) -> List[str]:
        try:
            index = self.client.get_index(ENTITY_INDEX)
            index.update_filterable_attributes(["entityType"])
            
            results = index.search(
                "",
                {
                    "facets": ["entityType"],
                    "limit": 0
                }
            )
            
            facet_dist = results.get("facetDistribution", {})
            entity_types = list(facet_dist.get("entityType", {}).keys())
            return entity_types
        except Exception:
            return []
    
    def build_causal_chain(
        self,
        start_entity: str,
        max_depth: int = 3,
        min_strength: float = 0.3
    ) -> List[Dict[str, Any]]:
        chains = []
        visited = set()
        
        def dfs(current_entity: str, path: List[Dict[str, Any]], depth: int):
            if depth > max_depth:
                return
            
            if current_entity in visited:
                return
            
            visited.add(current_entity)
            
            outgoing = self.get_outgoing_relations(current_entity, limit=20)
            
            for relation in outgoing:
                if relation.get("strength", 0) < min_strength:
                    continue
                
                relation_type = relation.get("relationType", "")
                is_causal = relation_type in [
                    "causes", "leads_to", "results_in", "enables", "prevents", "influences"
                ]
                
                if not is_causal:
                    continue
                
                next_entity = relation.get("targetEntity")
                new_path = path + [{
                    "relation": relation,
                    "from": current_entity,
                    "to": next_entity
                }]
                
                chains.append({
                    "path": new_path,
                    "length": len(new_path),
                    "totalStrength": sum(r["relation"].get("strength", 0) for r in new_path) / len(new_path),
                    "startEntity": start_entity,
                    "endEntity": next_entity
                })
                
                dfs(next_entity, new_path, depth + 1)
            
            visited.remove(current_entity)
        
        dfs(start_entity, [], 0)
        
        chains.sort(key=lambda x: x["totalStrength"], reverse=True)
        return chains


knowledge_graph_manager = KnowledgeGraphManager()
