import re
from typing import List, Tuple
from django.conf import settings


try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class SemanticRetriever:
    def __init__(self):
        self.model = None
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            model_name = getattr(settings, 'CLASSIFICATION_CONFIG', {}).get('semantic_model', 'all-MiniLM-L6-v2')
            try:
                self.model = SentenceTransformer(model_name)
            except Exception:
                self.model = None

    def get_candidates(self, product_text: str, taxonomy_nodes: list, top_k: int = 10) -> List[dict]:
        if not self.model or not taxonomy_nodes:
            return []
        try:
            product_embedding = self.model.encode([product_text])
            node_texts = [f"{node.name} {node.full_path}" for node in taxonomy_nodes]
            node_embeddings = self.model.encode(node_texts)
            similarities = np.dot(node_embeddings, product_embedding.T).flatten()
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            candidates = []
            for idx in top_indices:
                candidates.append({
                    'node': taxonomy_nodes[idx],
                    'score': float(similarities[idx]),
                })
            return candidates
        except Exception:
            return []