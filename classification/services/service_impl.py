 """
Unified Classification Service
Combines hybrid classifier, semantic retriever, image analyzer, 
LLM classifier, and confidence engine into a single service.
"""
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


@dataclass
class ClassificationResponse:
    """Unified response from classification."""
    product_id: Any
    category_path: str
    confidence: float
    confidence_level: str
    requires_review: bool
    review_reason: Optional[str] = None
    extracted_attributes: Dict[str, str] = field(default_factory=dict)
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    classification_method: str = "hybrid"
    reasoning: Optional[str] = None


class ClassificationService:
    """
    Unified classification service that orchestrates all classification engines.
    Lazy-loads heavy ML dependencies (torch, sentence-transformers) only when needed.
    """

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self._hybrid = None
        self._retriever = None
        self._image_analyzer = None
        self._llm = None
        self._confidence = None
        self._initialized = False
        self._categories = []

    def initialize(self, categories: List[Dict]):
        """Initialize service with taxonomy categories."""
        self._categories = categories
        self._initialized = True

        # Lazy-load services that don't need heavy ML
        from .confidence_engine import ConfidenceEngine
        self._confidence = ConfidenceEngine(self.config)

        # Pre-build a lightweight keyword index (no torch needed)
        self._keyword_index = self._build_keyword_index(categories)

        logger.info(f"ClassificationService initialized with {len(categories)} categories")

    def classify_product(self, product_data: Dict, use_llm: bool = False) -> ClassificationResponse:
        """
        Classify a single product.

        Args:
            product_data: dict with product fields (id, product_name, product_description, etc.)
            use_llm: if True, also run LLM classification

        Returns:
            ClassificationResponse
        """
        product_id = product_data.get('id', 'unknown')

        # Step 1: Get candidates via keyword matching (always works, no ML needed)
        candidates = self._retrieve_candidates(product_data, top_k=20)

        # Step 2: Run hybrid classifier (may use sentence-transformers if available)
        hybrid_result = self._classify_hybrid(product_data, candidates)

        # Step 3: Optionally enhance with LLM
        llm_result = None
        if use_llm:
            llm_result = self._classify_with_llm(product_data, candidates)

        # Step 4: Merge results
        final = self._merge_results(product_id, hybrid_result, llm_result)

        # Step 5: Calculate confidence
        confidence_result = self._calculate_confidence(final, product_data)

        return ClassificationResponse(
            product_id=product_id,
            category_path=final['category_path'],
            confidence=confidence_result.score,
            confidence_level=confidence_result.confidence_level,
            requires_review=confidence_result.requires_review,
            review_reason=confidence_result.review_reason,
            extracted_attributes=final.get('extracted_attributes', {}),
            alternatives=final.get('alternatives', []),
            classification_method=final.get('classification_method', 'hybrid'),
            reasoning=final.get('reasoning')
        )

    def _build_keyword_index(self, categories: List[Dict]) -> Dict[str, List[Dict]]:
        """Build a simple keyword-to-category index (no ML needed)."""
        index = {}
        for cat in categories:
            keywords = cat.get('keywords', '') or ''
            name = cat.get('name', '') or ''
            full_path = cat.get('full_path', '') or ''

            # Index by individual words
            all_text = f"{name} {keywords} {full_path}".lower()
            for word in all_text.split():
                word = word.strip('.,;:()-/')
                if len(word) > 2:
                    if word not in index:
                        index[word] = []
                    index[word].append(cat)

            # Index by product_type_hint
            hint = cat.get('product_type_hint', '') or ''
            if hint:
                hint_lower = hint.lower()
                if hint_lower not in index:
                    index[hint_lower] = []
                index[hint_lower].append(cat)

        return index

    def _retrieve_candidates(self, product_data: Dict, top_k: int = 20) -> List[Dict]:
        """Retrieve candidate categories using keyword matching."""
        if not self._initialized or not self._categories:
            return []

        # Build product text
        product_text = self._build_product_text(product_data).lower()
        product_words = set(product_text.split())

        # Score categories by keyword overlap
        scored = []
        for cat in self._categories:
            score = 0
            cat_words = set()
            all_text = f"{cat.get('name', '')} {cat.get('keywords', '')} {cat.get('full_path', '')}".lower()
            cat_words = set(all_text.split())

            # Word overlap
            overlap = product_words & cat_words
            score += len(overlap) * 0.3

            # Product type hint match
            hint = (cat.get('product_type_hint', '') or '').lower()
            if hint and hint in product_text:
                score += 2.0

            # Top-level category boost
            top_cat = (cat.get('top_level_category', '') or '').lower()
            if top_cat and top_cat in product_text:
                score += 1.0

            if score > 0:
                scored.append((score, cat))

        # Sort by score, return top_k
        scored.sort(key=lambda x: x[0], reverse=True)
        return [cat for _, cat in scored[:top_k]]

    def _classify_hybrid(self, product_data: Dict, candidates: List[Dict]) -> Dict:
        """Classify using the hybrid classifier (lazy loads torch/sentence-transformers)."""
        if not candidates:
            return {
                'category_path': '',
                'confidence': 0.0,
                'extracted_attributes': {},
                'alternatives': [],
                'classification_method': 'keyword_fallback',
                'reasoning': 'No candidate categories found'
            }

        # Try to use the full hybrid classifier (with torch)
        try:
            from .hybrid_classifier import HybridClassifier
            hybrid = HybridClassifier(
                taxonomy_data={'categories': candidates},
                config=self.config
            )
            result = hybrid.classify(product_data, candidates)

            return {
                'category_path': result.category_path,
                'confidence': result.confidence,
                'extracted_attributes': result.extracted_attributes,
                'alternatives': result.alternatives,
                'classification_method': 'hybrid',
                'reasoning': None
            }
        except Exception as e:
            logger.warning(f"Hybrid classifier failed, using keyword fallback: {e}")
            # Fall back to keyword-based classification
            return self._classify_keyword(product_data, candidates)

    def _classify_keyword(self, product_data: Dict, candidates: List[Dict]) -> Dict:
        """Simple keyword-based classification fallback (no ML needed)."""
        if not candidates:
            return {
                'category_path': '',
                'confidence': 0.0,
                'extracted_attributes': {},
                'alternatives': [],
                'classification_method': 'keyword',
                'reasoning': 'No candidates'
            }

        product_text = self._build_product_text(product_data).lower()
        product_words = set(product_text.split())

        scored = []
        for cat in candidates:
            cat_text = f"{cat.get('name', '')} {cat.get('keywords', '')}".lower()
            cat_words = set(cat_text.split())
            if cat_words:
                score = len(product_words & cat_words) / len(cat_words)
            else:
                score = 0
            scored.append((score, cat))

        scored.sort(key=lambda x: x[0], reverse=True)
        best_score, best_cat = scored[0] if scored else (0, {})

        # Extract attributes
        attributes = self._extract_attributes(product_data, best_cat)

        # Build alternatives
        alternatives = [
            {
                'category': c.get('full_path', c.get('name', '')),
                'confidence': min(s, 1.0)
            }
            for s, c in scored[1:4]
        ]

        return {
            'category_path': best_cat.get('full_path', ''),
            'confidence': min(best_score, 1.0),
            'extracted_attributes': attributes,
            'alternatives': alternatives,
            'classification_method': 'keyword',
            'reasoning': f'Keyword match score: {best_score:.3f}'
        }

    def _classify_with_llm(self, product_data: Dict, candidates: List[Dict]) -> Optional[Dict]:
        """Classify using LLM (lazy loads provider SDK)."""
        try:
            from .llm_classifier import LLMClassifier

            llm_config = self.config.get('llm', {})
            provider = llm_config.get('provider', 'groq')
            api_key = llm_config.get('api_key')

            if not api_key:
                return None

            llm = LLMClassifier(provider=provider, api_key=api_key)
            result = llm.classify(product_data, candidates)

            return {
                'category_path': result.category_path,
                'confidence': result.confidence,
                'extracted_attributes': result.extracted_attributes,
                'alternatives': result.alternatives,
                'reasoning': result.reasoning
            }
        except Exception as e:
            logger.warning(f"LLM classification failed: {e}")
            return None

    def _merge_results(self, product_id, hybrid_result: Dict, llm_result: Optional[Dict]) -> Dict:
        """Merge hybrid and LLM results, preferring higher confidence."""
        if not llm_result:
            return hybrid_result

        hybrid_conf = hybrid_result.get('confidence', 0)
        llm_conf = llm_result.get('confidence', 0)

        if llm_conf > hybrid_conf and llm_result.get('category_path'):
            return {
                **llm_result,
                'classification_method': 'llm_enhanced',
            }
        return hybrid_result

    def _calculate_confidence(self, result: Dict, product_data: Dict):
        """Calculate confidence using the confidence engine."""
        if self._confidence is None:
            from .confidence_engine import ConfidenceEngine
            self._confidence = ConfidenceEngine(self.config)

        scores = {
            'lexical': result.get('confidence', 0),
            'semantic': result.get('confidence', 0),
        }

        return self._confidence.calculate_confidence(scores, product_data)

    def _build_product_text(self, product: Dict) -> str:
        """Build searchable text from product fields."""
        fields = [
            product.get('product_name', ''),
            product.get('product_description', ''),
            product.get('source_category', ''),
            product.get('materials', ''),
            product.get('product_type', '')
        ]
        return ' '.join(filter(None, fields))

    def _extract_attributes(self, product: Dict, category: Dict) -> Dict[str, str]:
        """Extract product attributes based on category."""
        attributes = {}

        materials = product.get('materials', '')
        if materials:
            attributes['Material'] = materials

        color_keywords = ['black', 'white', 'brown', 'gray', 'blue', 'red', 'green']
        product_text = self._build_product_text(product).lower()
        for color in color_keywords:
            if color in product_text:
                attributes['Color'] = color.title()
                break

        weight = product.get('product_weight')
        if weight:
            attributes['Weight'] = f"{weight} lbs"

        country = product.get('country_of_origin')
        if country:
            attributes['Country of Origin'] = country

        return attributes
