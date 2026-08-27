"""
Classification services - lazily imported to avoid loading heavy ML libs at startup.
"""
import logging

logger = logging.getLogger(__name__)

# Lazy loading pattern - don't import torch/sentence-transformers at module level
ClassificationService = None
ClassificationResponse = None


def _ensure_loaded():
    global ClassificationService, ClassificationResponse
    if ClassificationService is None:
        from .service_impl import ClassificationService as _CS, ClassificationResponse as _CR
        ClassificationService = _CS
        ClassificationResponse = _CR


def __getattr__(name):
    if name in ('ClassificationService', 'ClassificationResponse'):
        _ensure_loaded()
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
