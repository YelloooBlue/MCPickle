import os
import json
import faiss
import requests
import numpy as np
from typing import Any, List, Dict

class VectorDatabase:
    def __init__(self):
        self.dimension = int(os.getenv("LLM_RERANK_DIMENSION"))
        self.index = faiss.IndexFlatL2(self.dimension)
        self.objects: List[Any] = []
        
        self.embeddingModel = os.getenv("LLM_EMBEDDING_MODEL_NAME")
        self.rerankModel = os.getenv("LLM_RERANK_MODEL_NAME")
        self.token = os.getenv("LLM_TOKEN")
        self.embeddingApi = os.getenv("LLM_EMBEDDING_MODEL_ADDR")
        self.rerankApi = os.getenv("LLM_RERANK_MODEL_ADDR")
        self.headers = {
            "Authorization": "Bearer "+self.token,
            "Content-Type": "application/json"
        }

    def add_vector(self, embeddingObject: Dict):
        self.objects.append(embeddingObject)
        vector = self.embedding_str(json.dumps(embeddingObject))
        self.index.add(np.array([vector]).astype('float32'))
    
    def delete_vector(self, embeddingObject: Dict):
        # TODO: 这里不对!
        index = self.objects.index(embeddingObject)
        vector = self.embedding_str(json.dumps(embeddingObject))
        self.index.remove(np.array([vector]).astype('float32'))
        self.objects.remove(embeddingObject)
    
    def search_object(self, keyword: str, topK: int = 10, topN: int = 5) -> List[Dict]:
        distances, indices = self.index.search(
            np.array([self.embedding_str(keyword)]).astype('float32'),
            topK
        )
        vdbSearchResult = [self.objects[i] for i in indices[0]]
        rerankObjs = self.rerankObjects(vdbSearchResult, keyword, topN)
        return rerankObjs


    def rerankObjects(self, objects: List[Dict], query: str, topN: int) -> List[Dict]:
        playload = {
            "model" : self.rerankModel,
            "query" : query,
            "top_n" : topN,
            "documents" : [json.dumps(embeddingObject) for embeddingObject in objects]
        }
        response = requests.request("POST", self.rerankApi, json=playload, headers=self.headers)
        return [objects[result['index']] for result in response.json()['results']]

    def embedding_str(self, text: str, encodeFormat: str = "float") -> List[float]:
        playload = {
            "model" : self.embeddingModel,
            "input" : text,
            "encode_format" : encodeFormat
        }
        response = requests.request("POST", self.embeddingApi, json=playload, headers=self.headers)
        return response.json()["data"][0]["embedding"]




