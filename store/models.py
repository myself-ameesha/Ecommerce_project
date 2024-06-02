from django.db import models
from category.models import category
from django.urls import reverse
from ecommerceapp.models import Account
from django.db.models import Avg, Count
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


def validate_non_negative(self):
    pass


class Product(models.Model):
    product_name = models.CharField(max_length=255,blank=True)
    slug = models.SlugField(max_length=200, unique=True,blank=True)
    description = models.TextField(blank=True)
    price = models.IntegerField(validators=[validate_non_negative, MinValueValidator(0)])
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[ MinValueValidator(0), MaxValueValidator(100)])
    stock = models.IntegerField(validators=[MinValueValidator(0)])
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(category, on_delete=models.CASCADE)
    created_date = models.DateField(auto_now_add = True)
    modified_date = models.DateField(auto_now = True)
    is_active = models.BooleanField(default=True)# Soft delete flag
    
    class Meta:
        ordering = ['created_date'] 

    def get_url(self):
        return reverse('product_details', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name
    
    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count
    
    def price_after_discount(self):

        if self.discount > 0 and self.discount <= 50:
            print("Discount product")
            return round(self.price - (self.price * self.discount / 100),2)
        elif self.category.category_discount > 0 and self.category.category_discount <= 50:
            print("Discount category")
            return round(self.price - (self.price * self.category.category_discount / 100),2)
        else:
            print("No discount")
            return self.price
        
    


    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="image")
    image = models.FileField(upload_to='photos/products', blank=True, null=True)
    

    def __str__(self):
        return f"Image for {self.product.product_name}"
    

class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)
    
    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)
    
variation_category_choice = (
    ('color', 'color'),
    ('size', 'size'),
)
    

class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=200, choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default= True)
    created_at = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value
    

class Wishlist(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)

    def get_url(self):
        return reverse('product_detaill', args=[self.product.slug])


    def __str__(self):
        return f'{self.user.username} - {self.product.product_name}'


class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject

