import meilisearch
from typing import Any, Dict, List, Optional, Union
from app.config import settings


class SearchClient:
    def __init__(self):
        self._client: Optional[meilisearch.Client] = None
    
    @property
    def client(self) -> meilisearch.Client:
        if self._client is None:
            self._client = meilisearch.Client(
                settings.meili_url,
                settings.meili_api_key
            )
        return self._client
    
    def get_index(self, index_uid: str):
        return self.client.index(index_uid)
    
    def create_index(self, uid: str, primary_key: Optional[str] = None) -> Dict[str, Any]:
        options = {}
        if primary_key:
            options["primaryKey"] = primary_key
        task = self.client.create_index(uid, options)
        return task
    
    def delete_index(self, uid: str) -> Dict[str, Any]:
        task = self.client.delete_index(uid)
        return task
    
    def get_indexes(self) -> Dict[str, Any]:
        return self.client.get_indexes()
    
    def get_index_info(self, uid: str) -> Dict[str, Any]:
        index = self.client.get_index(uid)
        return {
            "uid": index.uid,
            "primaryKey": index.primary_key,
            "createdAt": index.created_at,
            "updatedAt": index.updated_at
        }
    
    def get_task(self, task_uid: int) -> Dict[str, Any]:
        task = self.client.get_task(task_uid)
        return task
    
    def get_tasks(self) -> Dict[str, Any]:
        return self.client.get_tasks()
    
    def wait_for_task(self, task_uid: int, timeout_in_ms: int = 5000) -> Dict[str, Any]:
        task = self.client.wait_for_task(task_uid, timeout_in_ms)
        return task


search_client = SearchClient()
