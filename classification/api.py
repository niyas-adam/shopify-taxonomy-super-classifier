from django.db import models
from django.utils import timezone
from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Product, TaxonomyCategory, Classification, ClassificationBatch


class ProductSerializer(serializers.ModelSerializer):
    has_image = serializers.ReadOnlyField()
    has_description = serializers.ReadOnlyField()
    class Meta:
        model = Product
        fields = '__all__'


class TaxonomyCategorySerializer(serializers.ModelSerializer):
    children_count = serializers.SerializerMethodField()
    class Meta:
        model = TaxonomyCategory
        fields = ['id', 'shopify_id', 'name', 'full_path', 'parent', 'level', 'keywords', 'product_type_hint', 'is_active', 'children_count']
    def get_children_count(self, obj):
        return obj.children.count()


class ClassificationSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True)
    taxonomy_path = serializers.SerializerMethodField()
    taxonomy_name = serializers.SerializerMethodField()
    class Meta:
        model = Classification
        fields = '__all__'
    def get_taxonomy_path(self, obj):
        return obj.taxonomy_node.full_path if obj.taxonomy_node else None
    def get_taxonomy_name(self, obj):
        return obj.taxonomy_node.name if obj.taxonomy_node else None


class ClassificationListSerializer(serializers.ModelSerializer):
    product_number = serializers.CharField(source='product.product_number', read_only=True)
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_image = serializers.CharField(source='product.image_url', read_only=True)
    taxonomy_path = serializers.SerializerMethodField()
    status_badge = serializers.ReadOnlyField()
    class Meta:
        model = Classification
        fields = ['id', 'product', 'product_number', 'product_name', 'product_image', 'taxonomy_node', 'taxonomy_path', 'confidence', 'status', 'classification_method', 'requires_manual_review', 'review_reason', 'alternatives', 'detected_attributes', 'status_badge', 'classified_at', 'reviewed_at']
    def get_taxonomy_path(self, obj):
        return obj.taxonomy_node.full_path if obj.taxonomy_node else None


class ClassificationBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassificationBatch
        fields = '__all__'


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = ['status', 'source_category']
    search_fields = ['product_number', 'product_name', 'product_description']
    ordering_fields = ['product_number', 'imported_at']

    @action(detail=False, methods=['get'])
    def stats(self, request):
        total = Product.objects.count()
        return Response({
            'total': total,
            'with_image': Product.objects.exclude(image_url='').count(),
            'without_image': total - Product.objects.exclude(image_url='').count(),
            'with_description': Product.objects.exclude(product_description='').count(),
        })

    @action(detail=False, methods=['post'])
    def import_products(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=400)
        return Response({'message': 'Import started', 'imported': 0})

    @action(detail=False, methods=['get'])
    def export(self, request):
        return Response({'message': 'Export endpoint'})


class TaxonomyCategoryViewSet(viewsets.ModelViewSet):
    queryset = TaxonomyCategory.objects.all()
    serializer_class = TaxonomyCategorySerializer
    filterset_fields = ['level', 'is_active']
    search_fields = ['name', 'full_path']

    @action(detail=False, methods=['get'])
    def tree(self, request):
        roots = TaxonomyCategory.objects.filter(parent=None)
        serializer = self.get_serializer(roots, many=True)
        return Response(serializer.data)


class ClassificationViewSet(viewsets.ModelViewSet):
    queryset = Classification.objects.select_related('product', 'taxonomy_node').all()
    serializer_class = ClassificationSerializer
    filterset_fields = ['status', 'requires_manual_review', 'classification_method']
    search_fields = ['product__product_number', 'product__product_name']

    def get_serializer_class(self):
        if self.action == 'list':
            return ClassificationListSerializer
        return ClassificationSerializer

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        cls = self.get_object()
        cls.status = 'approved'
        cls.reviewed_at = timezone.now()
        cls.reviewer_notes = request.data.get('notes', '')
        cls.save(update_fields=['status', 'reviewed_at', 'reviewer_notes'])
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        cls = self.get_object()
        cls.status = 'rejected'
        cls.reviewed_at = timezone.now()
        cls.reviewer_notes = request.data.get('notes', '')
        cls.save(update_fields=['status', 'reviewed_at', 'reviewer_notes'])
        return Response({'status': 'rejected'})

    @action(detail=False, methods=['post'])
    def batch_approve(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': 'ids required'}, status=400)
        updated = Classification.objects.filter(id__in=ids).update(
            status='approved', reviewed_at=timezone.now()
        )
        return Response({'approved': updated})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        from django.db.models import Count, Avg
        qs = Classification.objects.all()
        return Response({
            'total': qs.count(),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id')).values_list('status', 'c')),
            'avg_confidence': round(qs.aggregate(a=Avg('confidence'))['a'] or 0, 3),
            'needs_review': qs.filter(requires_manual_review=True).count(),
        })