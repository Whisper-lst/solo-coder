from typing import Any, Dict, List, Optional, Tuple
import uuid
from app.causal.knowledge_graph import knowledge_graph_manager
from app.models import CausalPath, CounterfactualResult


class CausalReasoningEngine:
    def __init__(self):
        self.kg = knowledge_graph_manager
        
        self.causal_relation_types = {
            "causes": {"strength_multiplier": 1.0, "direction": "forward"},
            "leads_to": {"strength_multiplier": 0.9, "direction": "forward"},
            "results_in": {"strength_multiplier": 0.85, "direction": "forward"},
            "enables": {"strength_multiplier": 0.7, "direction": "forward"},
            "prevents": {"strength_multiplier": 0.9, "direction": "reverse"},
            "influences": {"strength_multiplier": 0.6, "direction": "bidirectional"},
            "correlates_with": {"strength_multiplier": 0.3, "direction": "bidirectional"},
            "requires": {"strength_multiplier": 0.8, "direction": "reverse"},
            "depends_on": {"strength_multiplier": 0.75, "direction": "reverse"},
        }
        
        self.counterfactual_templates = {
            "what_if": "如果 {assumed_fact} 发生，那么 {target_outcome} 的概率会如何变化？",
            "why": "为什么 {target_outcome} 会发生？可能的因果路径是什么？",
            "how_to": "如何才能使 {target_outcome} 发生？需要哪些条件？",
            "alternative": "除了 {original_fact} 之外，还有哪些因素可能导致 {target_outcome}？",
        }
    
    def find_causal_paths(
        self,
        source_entity: str,
        target_entity: str,
        max_depth: int = 3,
        min_strength: float = 0.3
    ) -> List[CausalPath]:
        paths = []
        
        def dfs(
            current: str,
            target: str,
            visited: set,
            path_entities: List[str],
            path_relations: List[str],
            total_strength: float,
            depth: int
        ):
            if depth > max_depth:
                return
            
            if current == target and len(path_entities) > 1:
                path_id = f"path_{uuid.uuid4().hex[:8]}"
                avg_strength = total_strength / len(path_relations) if path_relations else 0
                
                explanation = self._generate_path_explanation(
                    path_entities, path_relations
                )
                
                path_type = "direct" if len(path_entities) == 2 else "indirect"
                
                paths.append(CausalPath(
                    path_id=path_id,
                    entities=path_entities.copy(),
                    relations=path_relations.copy(),
                    total_strength=avg_strength,
                    explanation=explanation,
                    path_type=path_type,
                    confidence=min(avg_strength + 0.2, 1.0)
                ))
                return
            
            if current in visited:
                return
            
            visited.add(current)
            
            outgoing = self.kg.get_outgoing_relations(current, limit=20)
            
            for relation in outgoing:
                relation_type = relation.get("relationType", "")
                if relation_type not in self.causal_relation_types:
                    continue
                
                config = self.causal_relation_types[relation_type]
                relation_strength = relation.get("strength", 0.5) * config["strength_multiplier"]
                
                if relation_strength < min_strength:
                    continue
                
                next_entity = relation.get("targetEntity")
                
                path_entities.append(next_entity)
                path_relations.append(relation.get("id", ""))
                
                dfs(
                    next_entity,
                    target,
                    visited,
                    path_entities,
                    path_relations,
                    total_strength + relation_strength,
                    depth + 1
                )
                
                path_entities.pop()
                path_relations.pop()
            
            visited.remove(current)
        
        dfs(source_entity, target_entity, set(), [source_entity], [], 0.0, 0)
        
        paths.sort(key=lambda p: (p.total_strength, -len(p.entities)), reverse=True)
        return paths
    
    def _generate_path_explanation(
        self,
        entities: List[str],
        relations: List[str]
    ) -> str:
        if len(entities) < 2:
            return ""
        
        relation_details = []
        for rel_id in relations:
            rel = self.kg.get_relation(rel_id)
            if rel:
                relation_details.append(rel)
        
        if len(entities) == 2:
            rel = relation_details[0] if relation_details else {}
            rel_type = rel.get("relationType", "relates to")
            return f"{entities[0]} {self._translate_relation(rel_type)} {entities[1]}。"
        
        explanation_parts = []
        for i in range(len(entities) - 1):
            rel = relation_details[i] if i < len(relation_details) else {}
            rel_type = rel.get("relationType", "relates to")
            explanation_parts.append(
                f"{entities[i]} {self._translate_relation(rel_type)} {entities[i+1]}"
            )
        
        return " → ".join(explanation_parts) + "。"
    
    def _translate_relation(self, relation_type: str) -> str:
        translations = {
            "causes": "导致",
            "leads_to": "导致",
            "results_in": "结果是",
            "enables": "使能够",
            "prevents": "阻止",
            "influences": "影响",
            "correlates_with": "与...相关",
            "requires": "需要",
            "depends_on": "依赖于",
        }
        return translations.get(relation_type, relation_type)
    
    def counterfactual_reasoning(
        self,
        original_fact: str,
        assumed_fact: str,
        target_outcome: str,
        explore_paths: bool = True,
        max_paths: int = 5
    ) -> CounterfactualResult:
        original_entities = self._extract_entities(original_fact)
        assumed_entities = self._extract_entities(assumed_fact)
        outcome_entities = self._extract_entities(target_outcome)
        
        outcome_probability = 0.5
        causal_paths = []
        alternative_scenarios = []
        
        if outcome_entities and original_entities:
            for orig_entity in original_entities[:3]:
                for outcome_entity in outcome_entities[:3]:
                    paths = self.find_causal_paths(
                        orig_entity,
                        outcome_entity,
                        max_depth=3,
                        min_strength=0.3
                    )
                    causal_paths.extend(paths[:max_paths // len(original_entities)])
            
            if causal_paths:
                avg_strength = sum(p.total_strength for p in causal_paths) / len(causal_paths)
                outcome_probability = avg_strength
        
        explanation = self._generate_counterfactual_explanation(
            original_fact,
            assumed_fact,
            target_outcome,
            causal_paths,
            outcome_probability
        )
        
        if assumed_entities and outcome_entities:
            for assumed_entity in assumed_entities[:2]:
                for outcome_entity in outcome_entities[:2]:
                    alt_paths = self.find_causal_paths(
                        assumed_entity,
                        outcome_entity,
                        max_depth=3,
                        min_strength=0.3
                    )
                    if alt_paths:
                        alt_strength = sum(p.total_strength for p in alt_paths) / len(alt_paths)
                        alternative_scenarios.append({
                            "assumedEntity": assumed_entity,
                            "outcomeEntity": outcome_entity,
                            "probability": alt_strength,
                            "paths": [p.model_dump() for p in alt_paths[:2]]
                        })
        
        return CounterfactualResult(
            result_id=f"cf_{uuid.uuid4().hex[:12]}",
            original_fact=original_fact,
            assumed_fact=assumed_fact,
            target_outcome=target_outcome,
            outcome_probability=outcome_probability,
            explanation=explanation,
            causal_paths=causal_paths,
            alternative_scenarios=alternative_scenarios if alternative_scenarios else None
        )
    
    def _generate_counterfactual_explanation(
        self,
        original_fact: str,
        assumed_fact: str,
        target_outcome: str,
        causal_paths: List[CausalPath],
        outcome_probability: float
    ) -> str:
        probability_desc = ""
        if outcome_probability >= 0.7:
            probability_desc = "很可能"
        elif outcome_probability >= 0.5:
            probability_desc = "有可能"
        elif outcome_probability >= 0.3:
            probability_desc = "可能性较低"
        else:
            probability_desc = "不太可能"
        
        explanation_parts = [
            f"反事实推理分析：",
            f"原始事实：{original_fact}",
            f"假设事实：{assumed_fact}",
            f"目标结果：{target_outcome}",
            f"",
            f"分析结果：",
            f"在假设 '{assumed_fact}' 的情况下，'{target_outcome}' {probability_desc}发生。",
        ]
        
        if causal_paths:
            explanation_parts.append("")
            explanation_parts.append("发现的因果路径：")
            for i, path in enumerate(causal_paths[:3], 1):
                explanation_parts.append(f"{i}. {path.explanation}")
                explanation_parts.append(f"   强度：{path.total_strength:.2f}")
        
        return "\n".join(explanation_parts)
    
    def _extract_entities(self, text: str) -> List[str]:
        stop_words = {
            "的", "是", "在", "有", "和", "与", "或", "及",
            "the", "is", "are", "was", "were", "be", "been", "being",
            "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of"
        }
        
        words = text.replace(",", " ").replace(".", " ").replace("?", " ").split()
        entities = []
        
        for word in words:
            word_lower = word.lower().strip()
            if word_lower and word_lower not in stop_words and len(word_lower) > 2:
                search_results = self.kg.search_entities(word, limit=3)
                for hit in search_results.get("hits", []):
                    if hit.get("id") not in entities:
                        entities.append(hit.get("id"))
        
        if not entities:
            entities = [w.strip() for w in words if len(w.strip()) > 2]
        
        return entities[:5]
    
    def find_related_entities(
        self,
        query_entities: List[str],
        max_depth: int = 2,
        min_strength: float = 0.4
    ) -> List[Dict[str, Any]]:
        related = {}
        
        for entity in query_entities:
            chains = self.kg.build_causal_chain(
                entity,
                max_depth=max_depth,
                min_strength=min_strength
            )
            
            for chain in chains:
                end_entity = chain["endEntity"]
                if end_entity not in related:
                    related[end_entity] = {
                        "entity_id": end_entity,
                        "strength": 0,
                        "paths": [],
                        "source_entities": set()
                    }
                
                related[end_entity]["strength"] = max(
                    related[end_entity]["strength"],
                    chain["totalStrength"]
                )
                related[end_entity]["paths"].append(chain)
                related[end_entity]["source_entities"].add(entity)
        
        result = []
        for entity_id, data in related.items():
            entity_info = self.kg.get_entity(entity_id)
            result.append({
                "entityId": entity_id,
                "entityName": entity_info.get("name", entity_id) if entity_info else entity_id,
                "entityType": entity_info.get("entityType", "unknown") if entity_info else "unknown",
                "strength": data["strength"],
                "pathCount": len(data["paths"]),
                "sourceEntities": list(data["source_entities"])
            })
        
        result.sort(key=lambda x: x["strength"], reverse=True)
        return result
    
    def generate_causal_insights(
        self,
        query: str,
        query_entities: List[str]
    ) -> List[Dict[str, Any]]:
        insights = []
        
        related_entities = self.find_related_entities(query_entities, max_depth=2)
        
        if related_entities:
            top_related = related_entities[:5]
            insights.append({
                "type": "related_entities",
                "title": "相关实体发现",
                "description": f"发现与查询相关的 {len(top_related)} 个实体",
                "entities": [
                    {
                        "name": e["entityName"],
                        "type": e["entityType"],
                        "strength": e["strength"]
                    }
                    for e in top_related
                ]
            })
        
        for entity in query_entities[:2]:
            outgoing = self.kg.get_outgoing_relations(entity, limit=10)
            causal_outgoing = [
                r for r in outgoing 
                if r.get("relationType") in self.causal_relation_types
            ]
            
            if causal_outgoing:
                insights.append({
                    "type": "causal_outgoing",
                    "title": f"实体 '{entity}' 的因果影响",
                    "description": f"该实体可能影响以下结果",
                    "relations": [
                        {
                            "target": r.get("targetEntity"),
                            "relationType": r.get("relationType"),
                            "strength": r.get("strength")
                        }
                        for r in causal_outgoing[:5]
                    ]
                })
            
            incoming = self.kg.get_incoming_relations(entity, limit=10)
            causal_incoming = [
                r for r in incoming 
                if r.get("relationType") in self.causal_relation_types
            ]
            
            if causal_incoming:
                insights.append({
                    "type": "causal_incoming",
                    "title": f"影响实体 '{entity}' 的因素",
                    "description": f"以下实体可能影响该实体",
                    "relations": [
                        {
                            "source": r.get("sourceEntity"),
                            "relationType": r.get("relationType"),
                            "strength": r.get("strength")
                        }
                        for r in causal_incoming[:5]
                    ]
                })
        
        return insights


causal_reasoning_engine = CausalReasoningEngine()
