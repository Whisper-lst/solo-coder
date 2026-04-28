from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class Document(BaseModel):
    id: Union[str, int]
    content: Optional[str] = None
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        extra = "allow"


class SearchRequest(BaseModel):
    query: str = ""
    index: str = "default"
    limit: int = 20
    offset: int = 0
    filter: Optional[str] = None
    sort: Optional[List[str]] = None
    attributes_to_retrieve: Optional[List[str]] = None
    attributes_to_highlight: Optional[List[str]] = None
    attributes_to_crop: Optional[List[str]] = None
    crop_length: int = 200
    show_matches_position: bool = False
    highlight_pre_tag: str = "<em>"
    highlight_post_tag: str = "</em>"
    hybrid: Optional[bool] = False
    semantic_ratio: float = 0.5
    embedder: str = "default"
    facets: Optional[List[str]] = None


class SearchResult(BaseModel):
    id: Union[str, int]
    title: Optional[str] = None
    content: Optional[str] = None
    score: Optional[float] = None
    _formatted: Optional[Dict[str, Any]] = None
    _matchesPosition: Optional[Dict[str, Any]] = None
    
    class Config:
        extra = "allow"


class SearchResponse(BaseModel):
    hits: List[SearchResult]
    query: str
    processing_time_ms: int = Field(alias="processingTimeMs")
    limit: int
    offset: int
    estimated_total_hits: Optional[int] = Field(default=None, alias="estimatedTotalHits")
    facet_distribution: Optional[Dict[str, Any]] = Field(default=None, alias="facetDistribution")
    facet_stats: Optional[Dict[str, Any]] = Field(default=None, alias="facetStats")


class IndexInfo(BaseModel):
    uid: str
    primary_key: Optional[str] = Field(default=None, alias="primaryKey")
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")


class IndexSettings(BaseModel):
    displayed_attributes: Optional[List[str]] = Field(default=None, alias="displayedAttributes")
    searchable_attributes: Optional[List[str]] = Field(default=None, alias="searchableAttributes")
    filterable_attributes: Optional[List[str]] = Field(default=None, alias="filterableAttributes")
    sortable_attributes: Optional[List[str]] = Field(default=None, alias="sortableAttributes")
    ranking_rules: Optional[List[str]] = Field(default=None, alias="rankingRules")
    stop_words: Optional[List[str]] = Field(default=None, alias="stopWords")
    synonyms: Optional[Dict[str, List[str]]] = None
    distinct_attribute: Optional[str] = Field(default=None, alias="distinctAttribute")
    typo_tolerance: Optional[Dict[str, Any]] = Field(default=None, alias="typoTolerance")
    faceting: Optional[Dict[str, Any]] = None
    pagination: Optional[Dict[str, Any]] = None
    embedders: Optional[Dict[str, Any]] = None


class TaskInfo(BaseModel):
    task_uid: int = Field(alias="taskUid")
    index_uid: str = Field(alias="indexUid")
    status: str
    task_type: str = Field(alias="type")
    enqueued_at: str = Field(alias="enqueuedAt")


class BatchDocumentRequest(BaseModel):
    documents: List[Dict[str, Any]]
    index: str = "default"


class MultiSearchRequest(BaseModel):
    queries: List[SearchRequest]


class MultiSearchResponse(BaseModel):
    results: List[SearchResponse]


class Entity(BaseModel):
    id: str
    name: str
    entity_type: str = Field(alias="entityType")
    description: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    aliases: Optional[List[str]] = None
    confidence: float = 1.0
    
    class Config:
        extra = "allow"
        populate_by_name = True


class CausalRelation(BaseModel):
    id: str
    source_entity: str = Field(alias="sourceEntity")
    target_entity: str = Field(alias="targetEntity")
    relation_type: str = Field(alias="relationType")
    causal_direction: str = Field(alias="causalDirection", default="forward")
    strength: float = 0.5
    evidence: Optional[List[str]] = None
    context: Optional[Dict[str, Any]] = None
    is_direct: bool = Field(alias="isDirect", default=True)
    
    class Config:
        extra = "allow"
        populate_by_name = True


class CausalPath(BaseModel):
    path_id: str = Field(alias="pathId")
    entities: List[str]
    relations: List[str]
    total_strength: float = Field(alias="totalStrength")
    explanation: str
    path_type: str = Field(alias="pathType", default="direct")
    confidence: float = 1.0


class UserIntent(BaseModel):
    intent_type: str = Field(alias="intentType")
    query_entities: List[str] = Field(alias="queryEntities")
    inferred_goal: Optional[str] = Field(default=None, alias="inferredGoal")
    potential_needs: List[str] = Field(alias="potentialNeeds")
    confidence: float
    context: Optional[Dict[str, Any]] = None


class CounterfactualRequest(BaseModel):
    query: str
    index: str = "default"
    assume_fact: str = Field(alias="assumeFact")
    target_outcome: str = Field(alias="targetOutcome")
    explore_paths: bool = Field(alias="explorePaths", default=True)
    max_paths: int = Field(alias="maxPaths", default=5)


class CounterfactualResult(BaseModel):
    result_id: str = Field(alias="resultId")
    original_fact: str = Field(alias="originalFact")
    assumed_fact: str = Field(alias="assumedFact")
    target_outcome: str = Field(alias="targetOutcome")
    outcome_probability: float = Field(alias="outcomeProbability")
    explanation: str
    causal_paths: List[CausalPath] = Field(alias="causalPaths")
    alternative_scenarios: Optional[List[Dict[str, Any]]] = Field(default=None, alias="alternativeScenarios")


class CausalSearchRequest(BaseModel):
    query: str
    index: str = "default"
    limit: int = 20
    offset: int = 0
    include_causal_paths: bool = Field(alias="includeCausalPaths", default=True)
    max_causal_depth: int = Field(alias="maxCausalDepth", default=3)
    explore_related_entities: bool = Field(alias="exploreRelatedEntities", default=True)
    intent_analysis: bool = Field(alias="intentAnalysis", default=True)
    filter: Optional[str] = None
    sort: Optional[List[str]] = None


class CausalSearchResult(BaseModel):
    document: SearchResult
    causal_relevance: float = Field(alias="causalRelevance")
    related_entities: List[str] = Field(alias="relatedEntities")
    causal_paths: Optional[List[CausalPath]] = Field(default=None, alias="causalPaths")
    explanation: Optional[str] = None


class CausalSearchResponse(BaseModel):
    query: str
    user_intent: Optional[UserIntent] = Field(default=None, alias="userIntent")
    hits: List[CausalSearchResult]
    related_entities: List[Dict[str, Any]] = Field(alias="relatedEntities")
    causal_insights: List[Dict[str, Any]] = Field(alias="causalInsights")
    processing_time_ms: int = Field(alias="processingTimeMs")
    limit: int
    offset: int


class KnowledgeGraphInfo(BaseModel):
    entity_count: int = Field(alias="entityCount")
    relation_count: int = Field(alias="relationCount")
    causal_relation_count: int = Field(alias="causalRelationCount")
    domain_types: List[str] = Field(alias="domainTypes")


class EntitySearchRequest(BaseModel):
    query: str
    entity_types: Optional[List[str]] = Field(default=None, alias="entityTypes")
    limit: int = 10
    offset: int = 0


class RelationSearchRequest(BaseModel):
    source_entity: Optional[str] = Field(default=None, alias="sourceEntity")
    target_entity: Optional[str] = Field(default=None, alias="targetEntity")
    relation_types: Optional[List[str]] = Field(default=None, alias="relationTypes")
    causal_only: bool = Field(default=False, alias="causalOnly")
    limit: int = 20
    offset: int = 0
