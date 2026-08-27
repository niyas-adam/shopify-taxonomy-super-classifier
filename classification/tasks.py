"""
Celery tasks for the classification system.
"""
import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def classify_product_task(self, product_id: int, use_llm: bool = False):
    """
    Classify a single product asynchronously.
    
    Args:
        product_id: Product ID to classify
        use_llm: Whether to use LLM for classification
    """
    from classification.models import Product, TaxonomyCategory, Classification
    from classification.services import ClassificationService
    
    try:
        product = Product.objects.get(id=product_id)
        product.status = 'processing'
        product.save()
        
        categories = list(TaxonomyCategory.objects.values(
            'id', 'shopify_id', 'name', 'full_path',
            'keywords', 'product_type_hint', 'top_level_category'
        ))
        
        service = ClassificationService(config={'taxonomy': categories})
        service.initialize(categories)
        
        product_data = {
            'id': product.id,
            'product_name': product.product_name,
            'product_description': product.product_description,
            'image_url': product.image_url,
            'source_category': product.source_category,
            'materials': product.materials,
            'product_weight': product.product_weight,
            'product_type': product.product_type
        }
        
        result = service.classify_product(product_data, use_llm=use_llm)
        
        classification, created = Classification.objects.update_or_create(
            product=product,
            defaults={
                'predicted_category_path': result.category_path,
                'confidence': result.confidence,
                'status': 'auto_classified' if not result.requires_review else 'needs_review',
                'requires_manual_review': result.requires_review,
                'review_reason': result.review_reason or '',
                'classification_method': result.classification_method,
            }
        )
        
        product.status = 'completed'
        product.classification_status = classification.status
        product.save()
        
        return {
            'product_id': product_id,
            'category_path': result.category_path,
            'confidence': result.confidence,
            'requires_review': result.requires_review
        }
        
    except Product.DoesNotExist:
        return {'error': 'Product not found'}
    except Exception as e:
        try:
            product = Product.objects.get(id=product_id)
            product.status = 'failed'
            product.save()
        except:
            pass
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def batch_classify_task(self, product_ids: list, use_llm: bool = False):
    """
    Classify multiple products in batch.
    """
    from classification.models import Product, TaxonomyCategory, Classification
    from classification.services import ClassificationService
    
    try:
        products = Product.objects.filter(id__in=product_ids)
        
        categories = list(TaxonomyCategory.objects.values(
            'id', 'shopify_id', 'name', 'full_path',
            'keywords', 'product_type_hint', 'top_level_category'
        ))
        
        service = ClassificationService(config={'taxonomy': categories})
        service.initialize(categories)
        
        results = []
        for product in products:
            try:
                product.status = 'processing'
                product.save()
                
                product_data = {
                    'id': product.id,
                    'product_name': product.product_name,
                    'product_description': product.product_description,
                    'image_url': product.image_url,
                    'source_category': product.source_category,
                    'materials': product.materials,
                    'product_weight': product.product_weight,
                    'product_type': product.product_type
                }
                
                result = service.classify_product(product_data, use_llm=use_llm)
                
                classification, created = Classification.objects.update_or_create(
                    product=product,
                    defaults={
                        'predicted_category_path': result.category_path,
                        'confidence': result.confidence,
                        'status': 'auto_classified' if not result.requires_review else 'needs_review',
                        'requires_manual_review': result.requires_review,
                        'review_reason': result.review_reason or '',
                        'classification_method': result.classification_method,
                    }
                )
                
                product.status = 'completed'
                product.classification_status = classification.status
                product.save()
                
                results.append({
                    'product_id': product.id,
                    'success': True,
                    'category_path': result.category_path
                })
                
            except Exception as e:
                product.status = 'failed'
                product.save()
                results.append({
                    'product_id': product.id,
                    'success': False,
                    'error': str(e)
                })
        
        return {
            'total': len(results),
            'successful': sum(1 for r in results if r['success']),
            'failed': sum(1 for r in results if not r['success']),
            'results': results
        }
        
    except Exception as e:
        raise self.retry(exc=e, countdown=60)


@shared_task
def cleanup_failed_classifications():
    """Clean up failed classifications older than 24 hours."""
    from classification.models import Product
    
    threshold = timezone.now() - timezone.timedelta(hours=24)
    count = Product.objects.filter(
        status='failed',
        updated_at__lt=threshold
    ).update(status='pending')
    
    return f'Cleaned up {count} failed classifications'


@shared_task
def update_classification_stats():
    """Update classification statistics."""
    from classification.models import Product, Classification
    
    stats = {
        'total_products': Product.objects.count(),
        'classified': Classification.objects.exclude(status='pending').count(),
        'needs_review': Classification.objects.filter(requires_manual_review=True).count(),
        'approved': Classification.objects.filter(status='approved').count(),
    }
    return stats
