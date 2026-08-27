from dataclasses import dataclass
from typing import Dict, List, Tuple
from django.conf import settings


@dataclass
class ConfidenceResult:
    score: float
    requires_review: bool
    review_reason: str
    confidence_level: str


class ConfidenceEngine:
    def __init__(self, config=None):
        cfg = config or {}
        if not cfg:
            cfg = getattr(settings, 'CLASSIFICATION_CONFIG', {})
        self.min_confidence = cfg.get('min_confidence', 0.3)
        self.review_threshold = cfg.get('review_threshold', 0.7)
        self.max_alternatives = cfg.get('max_alternatives', 3)

    def calculate_confidence(self, scores: Dict[str, float], signals: Dict) -> ConfidenceResult:
        weighted_score = 0.0
        weights = {'lexical': 0.3, 'semantic': 0.4, 'image': 0.2, 'hint': 0.1}
        for signal_type, weight in weights.items():
            if signal_type in scores:
                weighted_score += scores[signal_type] * weight
        penalty = self._calculate_penalty(signals)
        final_score = weighted_score * penalty
        final_score = max(0.0, min(1.0, final_score))
        requires_review, reason = self._determine_review(final_score, signals)
        confidence_level = self._get_confidence_level(final_score)
        return ConfidenceResult(
            score=final_score,
            requires_review=requires_review,
            review_reason=reason,
            confidence_level=confidence_level,
        )

    def _get_confidence_level(self, score: float) -> str:
        if score >= 0.8:
            return 'high'
        if score >= 0.5:
            return 'medium'
        if score >= 0.3:
            return 'low'
        return 'very_low'

    def _calculate_penalty(self, signals: Dict) -> float:
        penalty = 1.0
        if signals.get('vertical_mismatch', False):
            penalty *= 0.5
        if signals.get('accessory_penalty', False):
            penalty *= 0.7
        return penalty

    def _determine_review(self, score: float, signals: Dict) -> Tuple[bool, str]:
        if score < self.min_confidence:
            return True, 'Low confidence score'
        if score < self.review_threshold:
            return True, 'Below review threshold'
        if signals.get('missing_description', False) and signals.get('missing_image', False):
            return True, 'Missing description and image'
        return False, ''

    def get_alternatives(self, all_scores: List[Dict], exclude_id: int = None) -> List[Dict]:
        sorted_scores = sorted(all_scores, key=lambda x: x['score'], reverse=True)
        alternatives = []
        for item in sorted_scores:
            if len(alternatives) >= self.max_alternatives:
                break
            if item.get('node_id') != exclude_id:
                alternatives.append({
                    'node_id': item.get('node_id'),
                    'category_path': item.get('category_path', ''),
                    'confidence': round(item.get('score', 0), 3),
                })
        return alternatives