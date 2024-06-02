from django.contrib import admin
from .models import Product, Variation , Wishlist , ReviewRating

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name','price','stock','category','created_date','modified_date','is_available')
    prepopulated_fields = {'slug':('product_name',)}

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value',)

class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_date')  # Display these fields in the admin list
    list_filter = ('user', 'added_date')  # Add filters for these fields
    search_fields = ['user__username', 'product__product_name']  # Add search functionality for related fields

admin.site.register(Wishlist, WishlistAdmin)   
admin.site.register(Product,ProductAdmin)
admin.site.register(Variation,VariationAdmin)
admin.site.register(ReviewRating)
