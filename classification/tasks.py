from celery import shared_task
from django.utils import timezone


@shared_task
def classify_product_task(product_id):
    from .models import Product, Classification
    from .services.hybrid_classifier import HybridClassifier
    product = Product.objects.get(id=product_id)
    classifier = HybridClassifier()
    result = classifier.classify(product)
    return result


@shared_task
def batch_classify_task(product_ids):
    from .models import Product
    from .services.hybrid_classifier import HybridClassifier
    classifier = HybridClassifier()
    results = []
    for pid in product_ids:
        try:
            product = Product.objects.get(id=pid)
            result = classifier.classify(product)
            results.append({'product_id': pid, 'status': 'success', 'result': result})
        except Exception as e:
            results.append({'product_id': pid, 'status': 'failed', 'error': str(e)})
    return results


@shared_task
def cleanup_failed_classifications():
    from .models import Classification
    count = Classification.objects.filter(status='failed').delete()[0]
    return f'Cleaned up {count} failed classifications'


@shared_task
def update_classification_stats():
    from .models import Classification
    from django.db.models import Count, Avg
    stats = Classification.objects.aggregate(
        total=Count('id'),
        avg_confidence=Avg('confidence')
    )
    return stats