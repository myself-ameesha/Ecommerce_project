from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class category(models.Model):
    category_name = models.CharField(max_length=255,unique=True, blank=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(max_length=255, blank=True)
    category_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    cat_image = models.ImageField(upload_to='photos/categories', blank=True)
    is_active = models.BooleanField(default=True)# Soft delete flag

    class Meta:
        verbose_name='category'
        verbose_name_plural = 'categories'

    def get_url(self):
            return reverse('products_by_category', args=[self.slug])
        
    def __str__(self):
        return self.category_name