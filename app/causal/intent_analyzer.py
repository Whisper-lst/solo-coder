from typing import Any, Dict, List, Optional, Tuple
import re
from app.causal.knowledge_graph import knowledge_graph_manager
from app.causal.causal_engine import causal_reasoning_engine
from app.models import UserIntent


class IntentAnalyzer:
    def __init__(self):
        self.kg = knowledge_graph_manager
        self.causal_engine = causal_reasoning_engine
        
        self.intent_patterns = {
            "informational": {
                "keywords": ["什么是", "如何", "怎样", "怎么", "了解", "学习", "教程", "指南",
                            "what is", "how to", "learn", "guide", "tutorial", "explain", "what"],
                "description": "信息查询意图 - 用户希望获取知识或信息"
            },
            "navigational": {
                "keywords": ["找", "搜索", "查找", "哪里有", "在哪里",
                            "find", "search", "where", "look for"],
                "description": "导航意图 - 用户希望找到特定内容"
            },
            "transactional": {
                "keywords": ["买", "购买", "预订", "预约", "下载", "注册",
                            "buy", "purchase", "download", "register", "book"],
                "description": "交易意图 - 用户希望执行某种操作"
            },
            "causal": {
                "keywords": ["为什么", "原因", "导致", "影响", "结果", "因为", "所以",
                            "why", "cause", "effect", "result", "because", "reason", "how come"],
                "description": "因果查询意图 - 用户希望理解因果关系"
            },
            "counterfactual": {
                "keywords": ["如果", "假设", "要是", "假如", "如果不", "如果没有",
                            "what if", "if", "suppose", "imagine", "what would happen"],
                "description": "反事实推理意图 - 用户希望探索假设情景"
            },
            "comparative": {
                "keywords": ["对比", "比较", "区别", "哪个好", "哪个更好", "vs",
                            "compare", "difference", "better", "vs", "versus"],
                "description": "比较意图 - 用户希望对比不同选项"
            },
            "troubleshooting": {
                "keywords": ["问题", "错误", "失败", "不工作", "怎么办", "解决",
                            "problem", "error", "fail", "not working", "fix", "solve"],
                "description": "问题排查意图 - 用户希望解决问题"
            },
            "exploratory": {
                "keywords": ["还有什么", "相关", "类似", "推荐", "建议",
                            "related", "similar", "recommend", "suggest", "what else"],
                "description": "探索意图 - 用户希望发现相关内容"
            }
        }
        
        self.question_words = {
            "zh": ["什么", "谁", "哪里", "何时", "为什么", "如何", "怎样", "多少", "几"],
            "en": ["what", "who", "where", "when", "why", "how", "how many", "how much"]
        }
        
        self.causal_indicators = {
            "cause_effect": ["导致", "造成", "引起", "产生", "带来", "使得",
                            "cause", "result in", "lead to", "bring about", "give rise to"],
            "effect_cause": ["因为", "由于", "原因是", "归因于",
                            "because", "due to", "caused by", "result of"],
            "preventive": ["阻止", "防止", "避免", "减少", "降低",
                          "prevent", "avoid", "reduce", "decrease", "lower"],
            "enable": ["使得", "让", "允许", "使能够",
                      "enable", "allow", "make possible", "permit"]
        }
    
    def analyze(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> UserIntent:
        query_lower = query.lower()
        
        intent_type = self._detect_intent_type(query_lower)
        query_entities = self._extract_query_entities(query)
        inferred_goal = self._infer_goal(query_lower, intent_type, query_entities)
        potential_needs = self._identify_potential_needs(
            query_lower, intent_type, query_entities, inferred_goal
        )
        confidence = self._calculate_confidence(query_lower, intent_type, query_entities)
        
        return UserIntent(
            intent_type=intent_type,
            query_entities=query_entities,
            inferred_goal=inferred_goal,
            potential_needs=potential_needs,
            confidence=confidence,
            context=context
        )
    
    def _detect_intent_type(self, query_lower: str) -> str:
        intent_scores = {}
        
        for intent_type, pattern in self.intent_patterns.items():
            score = 0
            for keyword in pattern["keywords"]:
                keyword_lower = keyword.lower()
                if keyword_lower in query_lower:
                    score += len(keyword_lower) / 10.0
            
            intent_scores[intent_type] = score
        
        is_question = self._is_question(query_lower)
        if is_question:
            if "why" in query_lower or "为什么" in query_lower:
                intent_scores["causal"] = max(intent_scores.get("causal", 0), 2.0)
            elif "what if" in query_lower or "如果" in query_lower:
                intent_scores["counterfactual"] = max(intent_scores.get("counterfactual", 0), 2.0)
            else:
                intent_scores["informational"] = max(intent_scores.get("informational", 0), 1.0)
        
        if self._has_causal_indicators(query_lower):
            intent_scores["causal"] = max(intent_scores.get("causal", 0), 1.5)
        
        max_score = max(intent_scores.values()) if intent_scores else 0
        
        if max_score < 0.3:
            return "navigational"
        
        for intent_type, score in sorted(intent_scores.items(), key=lambda x: x[1], reverse=True):
            if score >= max_score * 0.8:
                return intent_type
        
        return "navigational"
    
    def _is_question(self, query_lower: str) -> bool:
        if "?" in query_lower or "？" in query_lower:
            return True
        
        for lang, words in self.question_words.items():
            for word in words:
                if word.lower() in query_lower:
                    return True
        
        return False
    
    def _has_causal_indicators(self, query_lower: str) -> bool:
        for category, indicators in self.causal_indicators.items():
            for indicator in indicators:
                if indicator.lower() in query_lower:
                    return True
        return False
    
    def _extract_query_entities(self, query: str) -> List[str]:
        entities = []
        
        search_results = self.kg.search_entities(query, limit=10)
        for hit in search_results.get("hits", []):
            entity_id = hit.get("id")
            if entity_id and entity_id not in entities:
                entities.append(entity_id)
        
        if not entities:
            words = re.findall(r'\b\w{3,}\b', query.lower())
            stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
                         "的", "是", "在", "有", "和", "与", "或", "及", "了"}
            entities = [w for w in words if w not in stop_words]
        
        return entities[:5]
    
    def _infer_goal(
        self,
        query_lower: str,
        intent_type: str,
        query_entities: List[str]
    ) -> Optional[str]:
        goal_templates = {
            "informational": "用户希望了解关于 {entities} 的信息",
            "navigational": "用户希望找到与 {entities} 相关的内容",
            "transactional": "用户希望执行与 {entities} 相关的操作",
            "causal": "用户希望理解与 {entities} 相关的因果关系",
            "counterfactual": "用户希望探索关于 {entities} 的假设情景",
            "comparative": "用户希望比较与 {entities} 相关的不同选项",
            "troubleshooting": "用户希望解决与 {entities} 相关的问题",
            "exploratory": "用户希望发现与 {entities} 相关的更多内容"
        }
        
        template = goal_templates.get(intent_type, "用户希望获取与 {entities} 相关的信息")
        
        if query_entities:
            entities_str = "、".join(query_entities[:3])
            return template.format(entities=entities_str)
        else:
            return template.replace("{entities}", "查询内容")
    
    def _identify_potential_needs(
        self,
        query_lower: str,
        intent_type: str,
        query_entities: List[str],
        inferred_goal: str
    ) -> List[str]:
        needs = []
        
        if intent_type == "causal":
            needs.append("探索因果关系路径")
            needs.append("识别影响因素")
            needs.append("理解结果成因")
        
        if intent_type == "counterfactual":
            needs.append("分析假设情景的影响")
            needs.append("探索替代方案")
            needs.append("评估不同条件下的结果概率")
        
        if intent_type == "informational":
            needs.append("获取详细信息")
            needs.append("相关推荐")
            needs.append("背景知识")
        
        if intent_type == "exploratory":
            needs.append("发现相关实体")
            needs.append("探索关联内容")
            needs.append("扩展知识边界")
        
        if intent_type == "troubleshooting":
            needs.append("识别问题原因")
            needs.append("查找解决方案")
            needs.append("预防措施")
        
        if intent_type == "comparative":
            needs.append("对比分析")
            needs.append("优缺点评估")
            needs.append("推荐最佳选择")
        
        if query_entities:
            related = self.causal_engine.find_related_entities(query_entities, max_depth=1)
            if related:
                top_related = related[:3]
                needs.append(f"探索相关实体：{', '.join(r['entityName'] for r in top_related)}")
        
        return needs
    
    def _calculate_confidence(
        self,
        query_lower: str,
        intent_type: str,
        query_entities: List[str]
    ) -> float:
        confidence = 0.5
        
        pattern = self.intent_patterns.get(intent_type, {})
        keywords = pattern.get("keywords", [])
        
        keyword_match_count = sum(1 for k in keywords if k.lower() in query_lower)
        if keyword_match_count > 0:
            confidence += min(keyword_match_count * 0.1, 0.3)
        
        if query_entities:
            confidence += 0.1
        
        if self._is_question(query_lower):
            confidence += 0.1
        
        if len(query_lower.split()) >= 3:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def generate_intent_summary(self, intent: UserIntent) -> Dict[str, Any]:
        summary = {
            "intentType": intent.intent_type,
            "description": self.intent_patterns.get(intent.intent_type, {}).get("description", ""),
            "confidence": intent.confidence,
            "queryEntities": intent.query_entities,
            "inferredGoal": intent.inferred_goal,
            "potentialNeeds": intent.potential_needs,
            "actionableInsights": []
        }
        
        insights = []
        
        if intent.intent_type == "causal":
            insights.append({
                "type": "recommendation",
                "text": "建议查看因果路径分析，了解实体间的影响关系"
            })
            insights.append({
                "type": "action",
                "text": "可以使用反事实推理探索不同假设情景"
            })
        
        if intent.intent_type == "counterfactual":
            insights.append({
                "type": "recommendation",
                "text": "系统将分析假设事实对目标结果的影响"
            })
            insights.append({
                "type": "action",
                "text": "尝试调整假设条件，观察结果变化"
            })
        
        if intent.query_entities:
            insights.append({
                "type": "info",
                "text": f"识别到 {len(intent.query_entities)} 个关键实体，将用于扩展搜索范围"
            })
        
        summary["actionableInsights"] = insights
        
        return summary


intent_analyzer = IntentAnalyzer()
