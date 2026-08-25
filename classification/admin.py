from django.contrib import admin
from .models import Product, TaxonomyCategory, Classification, ClassificationBatch

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_number', 'product_name', 'source_category', 'status', 'imported_at']
    search_fields = ['product_number', 'product_name']
    list_filter = ['status', 'source_category']

@admin.register(TaxonomyCategory)
class TaxonomyCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'full_path', 'level', 'parent']
    search_fields = ['name', 'full_path']
    list_filter = ['level']

@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    list_display = ['product', 'taxonomy_node', 'confidence', 'status', 'requires_manual_review']
    list_filter = ['status', 'requires_manual_review']
    search_fields = ['product__product_number', 'product__product_name']

@admin.register(ClassificationBatch)
class ClassificationBatchAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'total_products', 'processed_products', 'created_at']
    list_filter = ['status']