from django.db import models
from ecommerceapp.models import Account
from store.models import Product
from carts.models import Variation
from django.core.validators import MinValueValidator

# Create your models here.
class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)# this is the total amount paid
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id
    
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.FloatField(validators=[MinValueValidator(0)])
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    def __str__(self):
        return self.code
    
class Order(models.Model):
    STATUS = (
        ('processing', 'processing'),
        ('Shipped', 'Shipped'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled' ),
        ('Delivered', 'Delivered'),
        ('Returned', 'Returned'),

    )

    PAYMENT = (
        ('COD', 'COD'),
        ('PayPal', 'Paypal'),
        ('Wallet','Wallet'),
    )

    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.CharField(max_length=100, null=True)
    final_total=models.DecimalField(max_digits=10, decimal_places=2, null=True)
    order_number = models.CharField(max_length=100)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    street_address = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)  # Add this line for state field
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=50)
    tax = models.FloatField(null=True)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    status = models.CharField(max_length=10, choices=STATUS, default='New')
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    
    def __str__(self):
        return self.first_name
    
  

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    


    def __str__(self):
        return self.product.product_name
    

    
class Wallet(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    wallet_balance = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    def __str__(self):
        return f"{self.account.email}'s Wallet"
    



    

