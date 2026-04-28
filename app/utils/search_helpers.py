from typing import Any, Dict, List, Optional, Tuple
from app.utils.synonyms import get_synonyms_for_language, merge_synonyms
from app.utils.multilingual import detect_language, get_stop_words_for_language


def build_filter_expression(filters: Dict[str, Any]) -> str:
    expressions = []
    
    for key, value in filters.items():
        if isinstance(value, list):
            if len(value) == 2 and all(isinstance(v, (int, float)) for v in value):
                expressions.append(f"{key} {value[0]} TO {value[1]}")
            else:
                or_conditions = " OR ".join([f"{key} = '{v}'" if isinstance(v, str) else f"{key} = {v}" for v in value])
                expressions.append(f"({or_conditions})")
        elif isinstance(value, str):
            expressions.append(f"{key} = '{value}'")
        elif isinstance(value, bool):
            expressions.append(f"{key} = {str(value).lower()}")
        else:
            expressions.append(f"{key} = {value}")
    
    return " AND ".join(expressions)


def parse_sort_string(sort_str: str) -> List[str]:
    sort_items = sort_str.split(",")
    result = []
    
    for item in sort_items:
        item = item.strip()
        if item.startswith("-"):
            result.append(f"{item[1:]}:desc")
        elif item.startswith("+"):
            result.append(f"{item[1:]}:asc")
        else:
            result.append(f"{item}:asc")
    
    return result


def enhance_search_query(query: str, language: Optional[str] = None) -> Tuple[str, str]:
    if language is None:
        language = detect_language(query)
    
    return query, language


def get_search_suggestions(
    query: str,
    documents: List[Dict[str, Any]],
    max_suggestions: int = 5,
    language: Optional[str] = None
) -> List[Dict[str, Any]]:
    if language is None:
        language = detect_language(query)
    
    synonyms = get_synonyms_for_language(language)
    
    suggestions = []
    query_lower = query.lower()
    
    for doc in documents[:max_suggestions * 2]:
        title = doc.get("title", "")
        content = doc.get("content", "")
        
        score = 0
        matched_text = ""
        
        if title:
            title_lower = title.lower()
            if query_lower in title_lower:
                score += 10
                matched_text = title
            else:
                for word, syn_list in synonyms.items():
                    if query_lower in syn_list and word in title_lower:
                        score += 5
                        matched_text = title
                        break
        
        if not matched_text and content:
            content_lower = content.lower()
            if query_lower in content_lower:
                score += 3
                matched_text = content[:100] + "..." if len(content) > 100 else content
        
        if score > 0:
            suggestions.append({
                "id": doc.get("id"),
                "text": matched_text,
                "score": score,
                "title": title
            })
    
    suggestions.sort(key=lambda x: x["score"], reverse=True)
    return suggestions[:max_suggestions]


def format_search_results(
    results: Dict[str, Any],
    include_formatted: bool = True,
    include_score: bool = True
) -> Dict[str, Any]:
    formatted_hits = []
    
    for hit in results.get("hits", []):
        formatted_hit = {}
        
        for key, value in hit.items():
            if key == "_formatted":
                if include_formatted:
                    formatted_hit["_formatted"] = value
            elif key == "_rankingScore":
                if include_score:
                    formatted_hit["score"] = value
            else:
                formatted_hit[key] = value
        
        formatted_hits.append(formatted_hit)
    
    return {
        "hits": formatted_hits,
        "query": results.get("query", ""),
        "processing_time_ms": results.get("processingTimeMs", 0),
        "limit": results.get("limit", 20),
        "offset": results.get("offset", 0),
        "estimated_total_hits": results.get("estimatedTotalHits"),
        "facet_distribution": results.get("facetDistribution"),
        "facet_stats": results.get("facetStats")
    }


def create_hybrid_search_config(
    semantic_ratio: float = 0.5,
    embedder: str = "default",
    openai_model: Optional[str] = None
) -> Dict[str, Any]:
    config = {
        "semanticRatio": semantic_ratio,
        "embedder": embedder
    }
    
    if openai_model:
        config["openaiModel"] = openai_model
    
    return config


def create_embedder_config(
    embedder_type: str = "openai",
    api_key: Optional[str] = None,
    model: str = "text-embedding-ada-002",
    dimensions: int = 1536,
    document_template: Optional[str] = None
) -> Dict[str, Any]:
    if embedder_type == "openai":
        config = {
            "source": "openAi",
            "model": model,
            "dimensions": dimensions
        }
        if api_key:
            config["apiKey"] = api_key
        if document_template:
            config["documentTemplate"] = document_template
        return {"default": config}
    
    elif embedder_type == "userProvided":
        return {
            "default": {
                "source": "userProvided",
                "dimensions": dimensions
            }
        }
    
    return {}


def create_typo_tolerance_config(
    enabled: bool = True,
    min_word_size_for_typo: Tuple[int, int] = (5, 9),
    disable_on_words: Optional[List[str]] = None,
    disable_on_attributes: Optional[List[str]] = None
) -> Dict[str, Any]:
    config = {
        "enabled": enabled,
        "minWordSizeForTypos": {
            "oneTypo": min_word_size_for_typo[0],
            "twoTypos": min_word_size_for_typo[1]
        }
    }
    
    if disable_on_words:
        config["disableOnWords"] = disable_on_words
    
    if disable_on_attributes:
        config["disableOnAttributes"] = disable_on_attributes
    
    return config


def create_ranking_rules_config(
    custom_rules: Optional[List[str]] = None
) -> List[str]:
    default_rules = [
        "words",
        "typo",
        "proximity",
        "attribute",
        "sort",
        "exactness"
    ]
    
    if custom_rules:
        return custom_rules
    
    return default_rules
