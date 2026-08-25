from typing import Dict, List, Tuple
from django.conf import settings


class ConfidenceEngine:
    def __init__(self):
        config = getattr(settings, 'CLASSIFICATION_CONFIG', {})
        self.min_confidence = config.get('min_confidence', 0.3)
        self.review_threshold = config.get('review_threshold', 0.7)
        self.max_alternatives = config.get('max_alternatives', 3)

    def calculate_confidence(self, scores: Dict[str, float], signals: Dict) -> Tuple[float, bool, str]:
        weighted_score = 0.0
        weights = {'lexical': 0.3, 'semantic': 0.4, 'image': 0.2, 'hint': 0.1}
        for signal_type, weight in weights.items():
            if signal_type in scores:
                weighted_score += scores[signal_type] * weight
        penalty = self._calculate_penalty(signals)
        final_score = weighted_score * penalty
        final_score = max(0.0, min(1.0, final_score))
        requires_review, reason = self._determine_review(final_score, signals)
        return final_score, requires_review, reason

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