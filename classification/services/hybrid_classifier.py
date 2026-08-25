import re
from typing import Dict, List, Tuple
from django.conf import settings
from .semantic_retriever import SemanticRetriever
from .image_analyzer import ImageAnalyzer
from .confidence_engine import ConfidenceEngine
from .llm_classifier import LLMClassifier


STOP_WORDS = set('a an the is are was were be been being have has had do does did will would shall should may might can could of in to for on with at by from as into through during before after above below between out off over under again further then once here there when where why how all both each few more most other some such no nor not only own same so than too very and but or if'.split())


def tokenize(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return [w for w in text.split() if len(w) > 1 and w not in STOP_WORDS]


def keyword_score(text, keywords_str):
    if not keywords_str:
        return 0.0
    text_tokens = set(tokenize(text))
    kw_tokens = set(tokenize(keywords_str))
    if not kw_tokens:
        return 0.0
    matches = text_tokens & kw_tokens
    return len(matches) / len(kw_tokens)


def build_product_text(product):
    parts = [
        product.product_name or '',
        product.product_description or '',
        product.source_category or '',
        product.source_subcategory or '',
        product.collection_name or '',
        product.materials or '',
    ]
    return ' '.join(p for p in parts if p)


class HybridClassifier:
    def __init__(self):
        config = getattr(settings, 'CLASSIFICATION_CONFIG', {})
        self.semantic_retriever = SemanticRetriever()
        self.image_analyzer = ImageAnalyzer()
        self.confidence_engine = ConfidenceEngine()
        self.llm_classifier = LLMClassifier()

    def classify(self, product) -> Dict:
        from .models import TaxonomyCategory, Classification
        product_text = build_product_text(product)
        taxonomy_nodes = list(TaxonomyCategory.objects.filter(is_active=True))
        lexical_scores = self._lexical_scoring(product_text, taxonomy_nodes)
        semantic_candidates = self.semantic_retriever.get_candidates(product_text, taxonomy_nodes)
        image_signals = {}
        if product.image_url:
            image_signals = self.image_analyzer.analyze_image(product.image_url)
        all_scores = []
        for node in taxonomy_nodes:
            score_data = {'node_id': node.id, 'category_path': node.full_path, 'name': node.name}
            lexical = next((s['score'] for s in lexical_scores if s['node_id'] == node.id), 0.0)
            semantic = next((c['score'] for c in semantic_candidates if c['node'].id == node.id), 0.0)
            hint = self._hint_score(product_text, node)
            score_data['scores'] = {'lexical': lexical, 'semantic': semantic, 'hint': hint}
            all_scores.append(score_data)
        if not all_scores:
            return self._create_result(product, None, 0.0, [], True, 'No taxonomy nodes found')
        best = max(all_scores, key=lambda x: sum(x['scores'].values()))
        signals = {
            'missing_description': not product.has_description,
            'missing_image': not product.has_image,
        }
        confidence, requires_review, reason = self.confidence_engine.calculate_confidence(best['scores'], signals)
        alternatives = self.confidence_engine.get_alternatives(all_scores, exclude_id=best['node_id'])
        try:
            node = TaxonomyCategory.objects.get(id=best['node_id'])
        except TaxonomyCategory.DoesNotExist:
            return self._create_result(product, None, confidence, alternatives, True, 'Category not found')
        return self._create_result(product, node, confidence, alternatives, requires_review, reason)

    def _lexical_scoring(self, product_text: str, taxonomy_nodes: list) -> List[Dict]:
        scores = []
        for node in taxonomy_nodes:
            score = 0.0
            kw_score = keyword_score(product_text, node.keywords)
            if kw_score > 0:
                score += kw_score * 0.6
            if node.product_type_hint and node.product_type_hint.lower() in product_text.lower():
                score += 0.3
            if node.name.lower() in product_text.lower():
                score += 0.2
            if node.parent:
                ps = keyword_score(product_text, node.parent.keywords)
                if ps > 0:
                    score += ps * 0.15
            scores.append({'node_id': node.id, 'score': min(score, 1.0)})
        return scores

    def _hint_score(self, product_text: str, node) -> float:
        if node.product_type_hint and node.product_type_hint.lower() in product_text.lower():
            return 1.0
        return 0.0

    def _create_result(self, product, node, confidence, alternatives, requires_review, reason):
        from .models import Classification
        from django.utils import timezone
        classification, _ = Classification.objects.update_or_create(
            product=product,
            defaults={
                'taxonomy_node': node,
                'confidence': confidence,
                'alternatives': alternatives,
                'requires_manual_review': requires_review,
                'review_reason': reason,
                'status': 'needs_review' if requires_review else 'auto_classified',
                'classified_at': timezone.now(),
            }
        )
        product.status = 'classified'
        product.save(update_fields=['status'])
        return {
            'classification_id': classification.id,
            'category': node.full_path if node else None,
            'confidence': confidence,
            'requires_review': requires_review,
        }