from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import ProductViewSet, TaxonomyCategoryViewSet, ClassificationViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'taxonomy', TaxonomyCategoryViewSet)
router.register(r'classifications', ClassificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]