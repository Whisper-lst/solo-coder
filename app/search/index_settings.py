from typing import Any, Dict, List, Optional
from app.search.client import search_client


class IndexSettingsManager:
    def __init__(self):
        self.client = search_client
    
    def get_settings(self, index_uid: str) -> Dict[str, Any]:
        index = self.client.get_index(index_uid)
        settings = index.get_settings()
        return settings
    
    def update_settings(self, index_uid: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        index = self.client.get_index(index_uid)
        task = index.update_settings(settings)
        return task
    
    def reset_settings(self, index_uid: str) -> Dict[str, Any]:
        index = self.client.get_index(index_uid)
        task = index.reset_settings()
        return task
    
    def update_filterable_attributes(self, index_uid: str, attributes: List[str]) -> Dict[str, Any]:
        index = self.client.get_index(index_uid)
        task = index.update_filterable_attributes(attributes)
        return task
    
    def update_sortable_attributes(self, index_uid: str, attributes: List[str]) -> Dict[str, Any]:
        index = self.client.get_index(index_uid)
        task = index.update_sortable_attributes(attributes)
        return task
    
    def update_searchable_attributes(self, index_uid: str, attributes: List[str]) -> Dict[str, Any]:
        index = self.client.get_index(index_uid)
        task = index.update_searchable_attributes(attributes)
        return task
    
    def update_displayed_attributes(self, index_uid: str, attributes: List[str]) -> Dict[str, Any]:
        index = self.client.get_index(index_uid)
        task = index.update_displayed_attributes(attributes)
        return task
    
    def update_ranking_rules(self, index_uid: str, rules: List[str]) -> Dict[str, Any]:
        index = self.client.get_index(index_uid)
        task = index.update_ranking_rules(rules)
        return task
    
    def update_synonyms(self, index_uid: str, synonyms: Dict[str, List[str]]) -> Dict[str, Any]:
        index = self.client.get_index(index_uid)
        task = index.update_synonyms(synonyms)
        return task
    
    def update_stop_words(self, index_uid: str, stop_words: List[str]) -> Dict[str, Any]:
        index = self.client.get_index(index_uid)
        task = index.update_stop_words(stop_words)
        return task
    
    def update_typo_tolerance(self, index_uid: str, typo_tolerance: Dict[str, Any]) -> Dict[str, Any]:
        index = self.client.get_index(index_uid)
        task = index.update_typo_tolerance(typo_tolerance)
        return task
    
    def update_distinct_attribute(self, index_uid: str, distinct_attribute: str) -> Dict[str, Any]:
        index = self.client.get_index(index_uid)
        task = index.update_distinct_attribute(distinct_attribute)
        return task
    
    def update_embedders(self, index_uid: str, embedders: Dict[str, Any]) -> Dict[str, Any]:
        index = self.client.get_index(index_uid)
        task = index.update_embedders(embedders)
        return task


index_settings_manager = IndexSettingsManager()
