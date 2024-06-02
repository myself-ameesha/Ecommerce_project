from django.shortcuts import render, redirect, get_object_or_404
from carts.models import CartItem
from .forms import OrderForm
from .models import Order, OrderProduct, Payment, Coupon , Wallet
from django.http import HttpResponse, JsonResponse
from datetime import datetime
from ecommerceapp.models import Address
from django.contrib import messages
import json
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.utils import timezone 
from django.contrib.auth.decorators import login_required



# Create your views here.

@login_required(login_url = 'loginn')
def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    # Store transaction details inside Payment model
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
     )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()


        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order recieved email to customer
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_recieved_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # Send order number and transaction id back to sendData method via JsonResponse
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)

@login_required(login_url = 'loginn')
def place_order(request, total=0, quantity=0):
    if request.method == "POST":
        current_user = request.user
        # Get the current date and time
        current_datetime = timezone.now()  
        # Get the selected address and coupon from the request
        selected_address_id = request.POST.get('selected_address')
        
        try:
            # Retrieve the user's wallet and get the wallet balance
            wallet = Wallet.objects.get(account=current_user)
            wallet_balance = wallet.wallet_balance
        except Wallet.DoesNotExist:
            # If the user doesn't have a wallet, set wallet_balance to 0
            wallet_balance = 0      


        # if the cart count is less than or equal to 0, then redirect back to shop
        cart_items = CartItem.objects.filter(user=current_user)
        cart_count = cart_items.count()
        if cart_count <= 0:
            return redirect('store')

        grand_total = 0
        tax = 0
        final_total = 0  # Initialize final_total here
        discount = 0
    
        if selected_address_id:
            selected_address = get_object_or_404(Address, id=selected_address_id)
        
            for cart_item in cart_items:
                total +=(cart_item.product.price_after_discount() * cart_item.quantity)
                quantity += cart_item.quantity
            tax = (2 * total)/100
            grand_total = total + tax
        # Coupon logic
        coupon_code = request.POST.get('coupon_code')
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                
                if coupon.valid_from <= current_datetime <= coupon.valid_to:
                    discount = coupon.discount
                    final_total = grand_total - Decimal(discount)
                    # Ensure grand total is not negative
                    final_total = max(0, final_total)
                else:
                    discount = 0
                    final_total = grand_total
                    
            except Coupon.DoesNotExist:
                discount = 0
                final_total = grand_total
                pass  # Coupon does not exist
        # Set final_total to grand_total if no coupon is entered
        if not coupon_code:
            final_total = grand_total
            
        if selected_address_id and (coupon_code or not coupon_code):    
            order = Order.objects.create(
                user=current_user,
                first_name=current_user.first_name,
                last_name=current_user.last_name,
                coupon=coupon_code,
                email=current_user.email,
                street_address=selected_address.street_address,
                city=selected_address.city,
                state=selected_address.state,
                country=selected_address.country,
                phone_number=selected_address.phone_number,
                order_total=grand_total,
                final_total=final_total,
                tax=tax,
                ip=request.META.get('REMOTE_ADDR')
            )

            

            # generate order number 
            '''yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))'''
            yr = current_datetime.year
            mt = current_datetime.month
            dt = current_datetime.day
            d = datetime(yr, mt, dt)
            current_date = d.strftime("%Y%d%m")
            order_number = current_date + str(order.id)
            order.order_number = order_number
            order.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            # Reduce the stock of products in the cart items by 1
            '''for cart_item in cart_items:
                product = cart_item.product
                product.stock -= 1  # Reduce the stock by 1
                product.save()'''

            context={
                'order' : order,
                'cart_items' : cart_items,
                'total' : total,
                'tax' : tax,
                'grand_total' : grand_total,
                'discount' : discount,
                'final_total': final_total,
                'wallet_balance' : wallet_balance,
                'error_message': None  # Set error message to None initially

            }
            
            return render(request, 'orders/payments.html', context)
        else:
            # Set error message and pass address details to context
            error_message = "Please select an address"
            addresses = Address.objects.filter(user=current_user)  # Fetch user's addresses
            context = {
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
                'wallet_balance': wallet_balance,
                'addresses': addresses,
                'error_message': error_message
            }
            return render(request, 'store/checkout.html', context)
    else:
        return redirect('checkout')    
    
@login_required(login_url = 'loginn') 
def cash_on_delivery(request, order_number):
    # Retrieve the order based on the order number
    order = get_object_or_404(Order, order_number=order_number)


    # Update the order status to indicate payment confirmation
    order.is_ordered = True
    order.status = 'COMPLETED'
    order.save()

    # Create a new Payment instance for cash on delivery payment method
    payment = Payment.objects.create(
        user=request.user,
        payment_id=f'COD-{order.order_number}',
        payment_method='COD',
        amount_paid=order.final_total,
        status='Pending'
    )

    # Assign the Payment instance to the order
    order.payment = payment
    order.save()

    
    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)


    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price 
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()
        # Update product stock
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # Delete all the current user's cart items
    CartItem.objects.filter(user=request.user).delete()

    # Render the confirm_payment.html template with the order details
    context = {
        'order_number': order_number,
        'order': order,
        'payment': payment,
    }
    return render(request, 'orders/confirmpayment.html', context)

@login_required(login_url = 'loginn')
def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        # Update the order status to 'COMPLETED'
        order.status = 'Completed'  # 'Completed' instead of 'COMPLETED' for consistency with the model
        order.save()

        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        # Retrieve coupon discount
        coupon_discount = 0
        if order.coupon:
            try:
                coupon = Coupon.objects.get(code=order.coupon)
                # Check if the coupon is valid
                if coupon.valid_from <= order.created_at <= coupon.valid_to:
                    coupon_discount = coupon.discount
            except Coupon.DoesNotExist:
                pass

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
            'coupon_discount': coupon_discount,  # Pass coupon discount to the context
        }

        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('store')
    
@login_required(login_url = 'loginn')  
def cancel_order(request, order_number):
        # Retrieve the order based on the order number
        order = get_object_or_404(Order, order_number=order_number)
    
        # Update order status to 'Cancelled' and set is_ordered to False
        order.status = 'Cancelled'
        order.is_ordered = True
        order.save()

        # Retrieve order items and update product stock
        order_items = OrderProduct.objects.filter(order=order)
        for order_item in order_items:
            product = order_item.product
            product.stock += order_item.quantity  # Increase product stock
            product.save()
        messages.success(request, "Order has been cancelled successfully.")
        return redirect('dashboard')  # Redirect to a success page after cancellation

@login_required(login_url = 'loginn')
def cancell_order(request, order_number):
    # Retrieve the order based on the order number
    order = get_object_or_404(Order, order_number=order_number)
    
    # Check if the order is already cancelled
    if order.status == 'Cancelled':
        messages.warning(request, "This order has already been cancelled.")
        return redirect('store')  # Redirect to a relevant page
    
    # Retrieve the final_total from the Order model
    final_total = order.final_total
    
    # Update order status to 'Cancelled' and set is_ordered to False
    order.status = 'Cancelled'
    order.is_ordered = True
    order.save()
    # Retrieve order items and update product stock
    order_items = OrderProduct.objects.filter(order=order)
    for order_item in order_items:
        product = order_item.product
        product.stock += order_item.quantity  # Increase product stock
        product.save()

    # Retrieve the user's wallet if it exists, or create a new wallet if it doesn't exist
    wallet, created = Wallet.objects.get_or_create(account=request.user)

    # If the wallet was just created, set the wallet balance to the final_total
    if created:
        wallet.wallet_balance = final_total
    else:
        # If the wallet already exists, add the final_total to the existing wallet balance
        wallet.wallet_balance += final_total
    wallet.save()
    messages.success(request, "Order has been cancelled successfully.")
    return redirect('store')  # Redirect to a success page after cancellation


@login_required(login_url = 'loginn')
def add_to_wallet(request, order_number):
    try:
        # Retrieve the user's wallet
        wallet = get_object_or_404(Wallet, account=request.user)
        
        # Retrieve the order based on the order number
        order = get_object_or_404(Order, order_number=order_number)
        
        # Retrieve the final_total from the order
        final_total = order.final_total
        
        # Check if the user has enough balance in the wallet
        if wallet.wallet_balance < final_total:
            messages.error(request, "Insufficient balance in your wallet.")
            return redirect('cart')  # Redirect to the cart page or any relevant page
        
        # Reduce the final_total amount from the wallet_balance
        wallet.wallet_balance -= final_total
        wallet.save()

        # Update the order status to 'Completed' and is_ordered to True
        order.status = 'Completed'
        order.is_ordered = True
        order.save()

        # Create a new Payment instance for wallet payment method
        payment = Payment.objects.create(
            user=request.user,
            payment_id=f'WAL-{order.order_number}',
            payment_method='Wallet',
            amount_paid=order.final_total,
            status='Completed'  # Assuming payment is completed since it's deducted from the wallet
        )

        # Assign the Payment instance to the order
        order.payment = payment
        order.save()

        # Retrieve cart items and add them to the order
        cart_items = CartItem.objects.filter(user=request.user)
        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.user_id = request.user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.save()

            cart_item = CartItem.objects.get(id=item.id)
            product_variation = cart_item.variations.all()
            orderproduct = OrderProduct.objects.get(id=orderproduct.id)
            orderproduct.variations.set(product_variation)
            orderproduct.save()
        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()
    #clear cart

        # Delete all the current user's cart items
        CartItem.objects.filter(user=request.user).delete()

        # Render the confirm_payment.html template with the order details
        context = {
            'order_number': order_number,
            'order': order,
            'payment': payment  # Include the payment details in the context
        }

        messages.success(request, "Order placed successfully. Amount deducted from your wallet.")
        return render(request, 'orders/confirmpayment.html', context)
    except Exception as e:
        messages.error(request, "An error occurred while processing your order.")
        return redirect('cart')  # Redirect to the cart page or any relevant page
