from django.contrib import admin
from .models import Order, OrderProduct, Payment , Coupon, Wallet

# Register your models here.
class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'ordered')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'payment', 'email', 'street_address', 'city', 'state', 'country','phone_number', 'tax', 'status', 'is_ordered', 'created_at']
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'first_name', 'last_name', 'email']
    list_per_page = 20
    inlines = [OrderProductInline]

    def full_name(self, obj):
        return obj.full_name()
    full_name.short_description = 'Full Name'

    def city(self, obj):
        return obj.city
    city.short_description = 'City'

    def phone_number(self, obj):
        return obj.phone_number
    phone_number.short_description = 'Phone Number'


    def tax(self, obj):
        return obj.tax
    tax.short_description = 'Tax'


class WalletAdmin(admin.ModelAdmin):
    list_display = ('account', 'wallet_balance' )


admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(OrderProduct)
admin.site.register(Coupon)
admin.site.register(Wallet, WalletAdmin)


