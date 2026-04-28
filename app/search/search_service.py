from typing import Any, Dict, List, Optional, Union
from app.search.client import search_client
from app.models import SearchRequest


class SearchService:
    def __init__(self):
        self.client = search_client
    
    def search(self, request: SearchRequest) -> Dict[str, Any]:
        index = self.client.get_index(request.index)
        
        search_params: Dict[str, Any] = {
            "limit": request.limit,
            "offset": request.offset,
        }
        
        if request.filter:
            search_params["filter"] = request.filter
        
        if request.sort:
            search_params["sort"] = request.sort
        
        if request.attributes_to_retrieve:
            search_params["attributesToRetrieve"] = request.attributes_to_retrieve
        
        if request.attributes_to_highlight:
            search_params["attributesToHighlight"] = request.attributes_to_highlight
        
        if request.attributes_to_crop:
            search_params["attributesToCrop"] = request.attributes_to_crop
            search_params["cropLength"] = request.crop_length
        
        if request.show_matches_position:
            search_params["showMatchesPosition"] = request.show_matches_position
        
        if request.highlight_pre_tag != "<em>" or request.highlight_post_tag != "</em>":
            search_params["highlightPreTag"] = request.highlight_pre_tag
            search_params["highlightPostTag"] = request.highlight_post_tag
        
        if request.hybrid:
            search_params["hybrid"] = {
                "semanticRatio": request.semantic_ratio,
                "embedder": request.embedder
            }
        
        if request.facets:
            search_params["facets"] = request.facets
        
        results = index.search(request.query, search_params)
        return results
    
    def multi_search(self, requests: List[SearchRequest]) -> Dict[str, Any]:
        search_queries = []
        for req in requests:
            query: Dict[str, Any] = {
                "indexUid": req.index,
                "q": req.query,
                "limit": req.limit,
                "offset": req.offset,
            }
            
            if req.filter:
                query["filter"] = req.filter
            if req.sort:
                query["sort"] = req.sort
            if req.attributes_to_retrieve:
                query["attributesToRetrieve"] = req.attributes_to_retrieve
            if req.attributes_to_highlight:
                query["attributesToHighlight"] = req.attributes_to_highlight
            if req.facets:
                query["facets"] = req.facets
            if req.hybrid:
                query["hybrid"] = {
                    "semanticRatio": req.semantic_ratio,
                    "embedder": req.embedder
                }
            
            search_queries.append(query)
        
        results = self.client.client.multi_search(search_queries)
        return results
    
    def search_with_facets(
        self,
        index_uid: str,
        query: str,
        facets: List[str],
        filter: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        index = self.client.get_index(index_uid)
        
        search_params: Dict[str, Any] = {
            "facets": facets,
            "limit": limit,
            "offset": offset,
        }
        
        if filter:
            search_params["filter"] = filter
        
        results = index.search(query, search_params)
        return results


search_service = SearchService()
