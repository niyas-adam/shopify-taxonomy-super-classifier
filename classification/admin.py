"""
Django admin configuration for classification app.
"""
from django.contrib import admin
from .models import (
    TaxonomyCategory, Product, Classification,
    ClassificationAttribute, AlternativeCategory, ClassificationBatch
)


@admin.register(TaxonomyCategory)
class TaxonomyCategoryAdmin(admin.ModelAdmin):
    list_display = ['shopify_id', 'name', 'full_path', 'level', 'top_level_category']
    search_fields = ['name', 'full_path', 'keywords']
    list_filter = ['level', 'top_level_category']
    ordering = ['full_path']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_number', 'product_name', 'source_category', 'status']
    search_fields = ['product_number', 'product_name', 'source_category']
    list_filter = ['status', 'classification_status']
    ordering = ['-created_at']


@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    list_display = [
        'get_product_number', 'predicted_category_path', 'confidence',
        'status', 'requires_manual_review', 'classification_method'
    ]
    search_fields = ['predicted_category_path']
    list_filter = ['status', 'requires_manual_review', 'classification_method']
    ordering = ['-created_at']
    
    def get_product_number(self, obj):
        return obj.product.product_number
    get_product_number.short_description = 'Product Number'


@admin.register(ClassificationAttribute)
class ClassificationAttributeAdmin(admin.ModelAdmin):
    list_display = ['classification', 'attribute_name', 'attribute_value', 'confidence']
    search_fields = ['attribute_name', 'attribute_value']


@admin.register(AlternativeCategory)
class AlternativeCategoryAdmin(admin.ModelAdmin):
    list_display = ['classification', 'category_path', 'confidence', 'rank']
    ordering = ['rank']


@admin.register(ClassificationBatch)
class ClassificationBatchAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'status', 'total_products', 'processed_products',
        'progress_percentage', 'use_llm'
    ]
    search_fields = ['name']
    list_filter = ['status', 'use_llm']
    ordering = ['-created_at']
