from typing import Any, Dict, List, Optional, Union
from app.search.client import search_client


class DocumentManager:
    def __init__(self):
        self.client = search_client
    
    def add_documents(
        self,
        index_uid: str,
        documents: List[Dict[str, Any]],
        primary_key: Optional[str] = None
    ) -> Dict[str, Any]:
        index = self.client.get_index(index_uid)
        if primary_key:
            task = index.add_documents(documents, primary_key=primary_key)
        else:
            task = index.add_documents(documents)
        return task
    
    def update_documents(
        self,
        index_uid: str,
        documents: List[Dict[str, Any]],
        primary_key: Optional[str] = None
    ) -> Dict[str, Any]:
        index = self.client.get_index(index_uid)
        if primary_key:
            task = index.update_documents(documents, primary_key=primary_key)
        else:
            task = index.update_documents(documents)
        return task
    
    def delete_document(self, index_uid: str, document_id: Union[str, int]) -> Dict[str, Any]:
        index = self.client.get_index(index_uid)
        task = index.delete_document(document_id)
        return task
    
    def delete_documents(self, index_uid: str, document_ids: List[Union[str, int]]) -> Dict[str, Any]:
        index = self.client.get_index(index_uid)
        task = index.delete_documents(document_ids)
        return task
    
    def delete_all_documents(self, index_uid: str) -> Dict[str, Any]:
        index = self.client.get_index(index_uid)
        task = index.delete_all_documents()
        return task
    
    def get_document(
        self,
        index_uid: str,
        document_id: Union[str, int],
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        index = self.client.get_index(index_uid)
        params = {}
        if fields:
            params["fields"] = fields
        document = index.get_document(document_id, params)
        return document
    
    def get_documents(
        self,
        index_uid: str,
        limit: int = 20,
        offset: int = 0,
        fields: Optional[List[str]] = None,
        filter: Optional[str] = None
    ) -> Dict[str, Any]:
        index = self.client.get_index(index_uid)
        params = {"limit": limit, "offset": offset}
        if fields:
            params["fields"] = fields
        if filter:
            params["filter"] = filter
        documents = index.get_documents(params)
        return documents


document_manager = DocumentManager()
