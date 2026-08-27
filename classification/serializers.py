"""
Serializers for the classification API.
"""
from rest_framework import serializers
from .models import (
    TaxonomyCategory, Product, Classification,
    ClassificationAttribute, AlternativeCategory, ClassificationBatch
)


class TaxonomyCategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = TaxonomyCategory
        fields = [
            'id', 'shopify_id', 'name', 'full_path', 'parent',
            'level', 'keywords', 'product_type_hint', 'top_level_category',
            'children', 'created_at', 'updated_at'
        ]
    
    def get_children(self, obj):
        children = obj.children.all()
        return TaxonomyCategorySerializer(children, many=True).data


class ProductSerializer(serializers.ModelSerializer):
    classification = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'product_number', 'product_name', 'product_description',
            'image_url', 'image', 'source_category', 'source_subcategory',
            'materials', 'product_weight', 'country_of_origin', 'product_type',
            'brand', 'status', 'classification_status', 'classification',
            'created_at', 'updated_at'
        ]
    
    def get_classification(self, obj):
        try:
            classification = obj.classification
            return ClassificationSerializer(classification).data
        except Classification.DoesNotExist:
            return None


class ClassificationAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassificationAttribute
        fields = ['id', 'attribute_name', 'attribute_value', 'confidence']


class AlternativeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AlternativeCategory
        fields = ['id', 'category_path', 'confidence', 'rank']


class ClassificationSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_number = serializers.CharField(source='product.product_number', read_only=True)
    
    class Meta:
        model = Classification
        fields = [
            'id', 'product', 'product_name', 'product_number',
            'taxonomy_node', 'predicted_category_path', 'confidence',
            'status', 'requires_manual_review', 'review_reason',
            'failure_reason', 'classification_method',
            'lexical_score', 'semantic_score', 'image_score', 'hint_score',
            'reviewed_by', 'reviewed_at', 'review_notes',
            'created_at', 'updated_at'
        ]


class ClassificationDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    attributes = ClassificationAttributeSerializer(many=True, read_only=True)
    alternative_categories = AlternativeCategorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Classification
        fields = [
            'id', 'product', 'taxonomy_node', 'predicted_category_path',
            'confidence', 'status', 'requires_manual_review', 'review_reason',
            'failure_reason', 'classification_method',
            'lexical_score', 'semantic_score', 'image_score', 'hint_score',
            'attributes', 'alternative_categories',
            'reviewed_by', 'reviewed_at', 'review_notes',
            'created_at', 'updated_at'
        ]


class ClassificationBatchSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.FloatField(read_only=True)
    
    class Meta:
        model = ClassificationBatch
        fields = [
            'id', 'name', 'description', 'status',
            'total_products', 'processed_products',
            'successful_classifications', 'failed_classifications',
            'reviews_needed', 'use_llm', 'batch_size',
            'progress_percentage', 'started_at', 'completed_at',
            'created_by', 'created_at', 'updated_at'
        ]


class ClassificationStatsSerializer(serializers.Serializer):
    total_products = serializers.IntegerField()
    classified = serializers.IntegerField()
    needs_review = serializers.IntegerField()
    approved = serializers.IntegerField()
    average_confidence = serializers.FloatField()
    status_counts = serializers.DictField()