from django.db import models
import hashlib


class Product(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('classified', 'Classified'),
        ('failed', 'Failed'),
    ]
    product_number = models.CharField(max_length=100, unique=True)
    product_name = models.CharField(max_length=500)
    product_description = models.TextField(blank=True, default='')
    source_category = models.CharField(max_length=255, blank=True, default='')
    source_subcategory = models.CharField(max_length=255, blank=True, default='')
    collection_name = models.CharField(max_length=255, blank=True, default='')
    materials = models.CharField(max_length=255, blank=True, default='')
    product_weight = models.FloatField(null=True, blank=True)
    country_of_origin = models.CharField(max_length=100, blank=True, default='')
    image_url = models.URLField(max_length=1024, blank=True, default='')
    all_image_urls = models.JSONField(default=list, blank=True)
    product_url = models.URLField(max_length=1024, blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    data_hash = models.CharField(max_length=64, blank=True, default='')
    imported_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['product_number']

    def __str__(self):
        return f"{self.product_number} - {self.product_name[:50]}"

    def save(self, *args, **kwargs):
        if not self.data_hash:
            data = f"{self.product_number}{self.product_name}{self.product_description}"
            self.data_hash = hashlib.sha256(data.encode()).hexdigest()
        super().save(*args, **kwargs)

    @property
    def has_image(self):
        return bool(self.image_url)

    @property
    def has_description(self):
        return bool(self.product_description.strip())


class TaxonomyCategory(models.Model):
    shopify_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    full_path = models.CharField(max_length=500)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    level = models.PositiveIntegerField(default=0)
    keywords = models.TextField(blank=True, default='')
    product_type_hint = models.CharField(max_length=255, blank=True, default='')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['level', 'name']

    def __str__(self):
        return self.full_path


class Classification(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('auto_classified', 'Auto Classified'),
        ('needs_review', 'Needs Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    METHOD_CHOICES = [
        ('hybrid', 'Hybrid'),
        ('lexical', 'Lexical'),
        ('semantic', 'Semantic'),
        ('image', 'Image'),
        ('llm', 'LLM'),
        ('manual', 'Manual'),
    ]
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='classification')
    taxonomy_node = models.ForeignKey(TaxonomyCategory, null=True, blank=True, on_delete=models.SET_NULL, related_name='classifications')
    confidence = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    classification_method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='hybrid')
    requires_manual_review = models.BooleanField(default=False)
    review_reason = models.CharField(max_length=255, blank=True, default='')
    alternatives = models.JSONField(default=list, blank=True)
    detected_attributes = models.JSONField(default=dict, blank=True)
    classified_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewer_notes = models.TextField(blank=True, default='')
    batch = models.ForeignKey('ClassificationBatch', null=True, blank=True, on_delete=models.SET_NULL, related_name='classifications')

    class Meta:
        ordering = ['-classified_at']

    def __str__(self):
        node_name = self.taxonomy_node.name if self.taxonomy_node else 'Unclassified'
        return f"{self.product.product_number} -> {node_name} ({self.confidence:.0%})"

    @property
    def predicted_category_path(self):
        return self.taxonomy_node.full_path if self.taxonomy_node else None

    @property
    def status_badge(self):
        colors = {
            'pending': 'secondary', 'auto_classified': 'info',
            'needs_review': 'warning', 'approved': 'success', 'rejected': 'danger',
        }
        return colors.get(self.status, 'secondary')


class ClassificationBatch(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_products = models.IntegerField(default=0)
    processed_products = models.IntegerField(default=0)
    successful_classifications = models.IntegerField(default=0)
    failed_classifications = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.status})"

    @property
    def progress_percent(self):
        if self.total_products == 0:
            return 0
        return (self.processed_products / self.total_products) * 100