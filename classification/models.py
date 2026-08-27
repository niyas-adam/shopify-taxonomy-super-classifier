"""
Django models for the classification system.
"""
from django.db import models
from django.utils import timezone


class TaxonomyCategory(models.Model):
    """Shopify taxonomy category."""
    
    shopify_id = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    full_path = models.CharField(max_length=512)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    level = models.SmallIntegerField(default=0)
    keywords = models.TextField(blank=True, default='')
    product_type_hint = models.CharField(max_length=255, blank=True, default='')
    top_level_category = models.CharField(max_length=255, blank=True, default='')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['full_path']
        verbose_name = 'Taxonomy Category'
        verbose_name_plural = 'Taxonomy Categories'
    
    def __str__(self):
        return self.full_path


class Product(models.Model):
    """Product to be classified."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('needs_review', 'Needs Review'),
    ]
    
    product_number = models.CharField(max_length=64, unique=True)
    product_name = models.CharField(max_length=512)
    product_description = models.TextField(blank=True, default='')
    image_url = models.URLField(max_length=1024, blank=True, default='')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    source_category = models.CharField(max_length=255, blank=True, default='')
    source_subcategory = models.CharField(max_length=255, blank=True, default='')
    materials = models.CharField(max_length=255, blank=True, default='')
    product_weight = models.FloatField(null=True, blank=True)
    country_of_origin = models.CharField(max_length=64, blank=True, default='')
    product_type = models.CharField(max_length=255, blank=True, default='')
    brand = models.CharField(max_length=255, blank=True, default='')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    classification_status = models.CharField(max_length=20, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
    
    def __str__(self):
        return f"{self.product_number} - {self.product_name}"


class Classification(models.Model):
    """Classification result for a product."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('auto_classified', 'Auto Classified'),
        ('needs_review', 'Needs Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='classification'
    )
    taxonomy_node = models.ForeignKey(
        TaxonomyCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='classifications'
    )
    predicted_category_path = models.CharField(max_length=512, blank=True, default='')
    confidence = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requires_manual_review = models.BooleanField(default=False)
    review_reason = models.TextField(blank=True, default='')
    failure_reason = models.TextField(blank=True, default='')
    
    classification_method = models.CharField(max_length=50, default='hybrid')
    lexical_score = models.FloatField(default=0.0)
    semantic_score = models.FloatField(default=0.0)
    image_score = models.FloatField(default=0.0)
    hint_score = models.FloatField(default=0.0)
    
    reviewed_by = models.CharField(max_length=255, blank=True, default='')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True, default='')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Classification'
        verbose_name_plural = 'Classifications'
    
    def __str__(self):
        return f"{self.product.product_number} - {self.predicted_category_path}"
    
    def approve(self, reviewed_by: str, notes: str = ''):
        self.status = 'approved'
        self.reviewed_by = reviewed_by
        self.reviewed_at = timezone.now()
        self.review_notes = notes
        self.requires_manual_review = False
        self.save()
    
    def reject(self, reviewed_by: str, notes: str = ''):
        self.status = 'rejected'
        self.reviewed_by = reviewed_by
        self.reviewed_at = timezone.now()
        self.review_notes = notes
        self.save()


class ClassificationAttribute(models.Model):
    classification = models.ForeignKey(Classification, on_delete=models.CASCADE, related_name='attributes')
    attribute_name = models.CharField(max_length=255)
    attribute_value = models.CharField(max_length=512)
    confidence = models.FloatField(default=0.9)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['attribute_name']
    
    def __str__(self):
        return f"{self.attribute_name}: {self.attribute_value}"


class AlternativeCategory(models.Model):
    classification = models.ForeignKey(Classification, on_delete=models.CASCADE, related_name='alternative_categories')
    category_path = models.CharField(max_length=512)
    confidence = models.FloatField(default=0.0)
    rank = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['rank']
    
    def __str__(self):
        return f"{self.category_path} (Rank: {self.rank})"


class ClassificationBatch(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('paused', 'Paused'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_products = models.PositiveIntegerField(default=0)
    processed_products = models.PositiveIntegerField(default=0)
    successful_classifications = models.PositiveIntegerField(default=0)
    failed_classifications = models.PositiveIntegerField(default=0)
    reviews_needed = models.PositiveIntegerField(default=0)
    use_llm = models.BooleanField(default=False)
    batch_size = models.PositiveIntegerField(default=100)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.status})"
    
    @property
    def progress_percentage(self):
        if self.total_products == 0:
            return 0
        return (self.processed_products / self.total_products) * 100
    
    def start(self):
        self.status = 'processing'
        self.started_at = timezone.now()
        self.save()
    
    def complete(self):
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def fail(self):
        self.status = 'failed'
        self.completed_at = timezone.now()
        self.save()