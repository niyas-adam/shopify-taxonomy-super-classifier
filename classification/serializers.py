from rest_framework import serializers
from .models import Product, TaxonomyCategory, Classification


class ProductSerializer(serializers.ModelSerializer):
    has_image = serializers.ReadOnlyField()
    has_description = serializers.ReadOnlyField()
    class Meta:
        model = Product
        fields = '__all__'