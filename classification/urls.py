from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import (
    TaxonomyCategoryViewSet, ProductViewSet,
    ClassificationViewSet, ClassificationBatchViewSet, StatsViewSet,
    stats_view
)

router = DefaultRouter()
router.register(r'taxonomy', TaxonomyCategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'classifications', ClassificationViewSet)
router.register(r'batches', ClassificationBatchViewSet)

urlpatterns = [
    path('stats/', stats_view, name='stats'),
    path('', include(router.urls)),
]
