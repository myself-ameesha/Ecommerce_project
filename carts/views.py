from django.shortcuts import render, redirect, get_object_or_404
from carts.models import Cart, CartItem
from store.models import Product, Variation , Wishlist
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from ecommerceapp.models import Address
from django.contrib import messages
from ecommerceapp.forms import AddressForm
from django.http import JsonResponse
from django.utils import timezone
import json
from orders.models import Coupon

# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

@login_required(login_url = 'loginn')
def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id) #get the product
    # If the user is authenticated
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass


        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ex_var_list:
                # increase the cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            else:
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')
    # If the user is not authenticated
    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass


        try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart using the cart_id present in the session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            # existing_variations -> database
            # current variation -> product_variation
            # item_id -> database
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            print(ex_var_list)

            if product_variation in ex_var_list:
                # increase the cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            else:
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')

 
@login_required(login_url = 'loginn')
def remove_cart(request, product_id, cart_item_id):
    
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)

        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

@login_required(login_url = 'loginn')
def remove_cart_item(request, product_id, cart_item_id):
    
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

@login_required(login_url = 'loginn')
def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0  # Initialize tax variable outside of try block
        grand_total = 0  # Initialize tax variable outside of try block
             
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            wishlist_items = Wishlist.objects.filter(user=request.user)  # Fetch wishlist items for the user
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            wishlist_items = None  # If the user is not authenticated, wishlist items will be None
        for cart_item in cart_items:
            total += cart_item.sub_total()
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax

    except ObjectDoesNotExist:
        pass

    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items': cart_items,
        'tax' : tax,
        'grand_total' : grand_total,
        'wishlist_items': wishlist_items,  # Include wishlist items in the context
    
    }
    return render(request,'store/cart.html', context)



@login_required(login_url='loginn')
def checkout(request, total=0, quantity=0, cart_items=None):

    try:
        tax = 0  # Initialize tax variable outside of try block
        grand_total = 0  # Initialize tax variable outside of try block
        addresses = Address.objects.filter(user=request.user)
        coupon = None  # Initialize coupon variable
        final_total = 0  # Initialize final_total variable
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)        
        for cart_item in cart_items:
            total += cart_item.sub_total()
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax 

    except ObjectDoesNotExist:
        pass

    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items': cart_items,
        'tax' : tax,
        'grand_total' : grand_total,
        'addresses': addresses,
    }
    return render(request, 'store/checkout.html',context)

@login_required(login_url = 'loginn')
def apply_coupon(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Extract the coupon code from the request body
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        coupon_code = body_data.get('coupon_code')
        current_datetime = timezone.now()

        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.valid_from <= current_datetime <= coupon.valid_to:
                # Coupon is valid, you can return success and additional coupon information
                print('good')
                return JsonResponse({'success': True, 'discount': coupon.discount}, status=200)
                
            else:
                # Coupon is expired
                print('expir')
                return JsonResponse({'success': False, 'error': 'Coupon is expired'}, status=400)
        except Coupon.DoesNotExist:
            # Coupon does not exist
            print('error')
            return JsonResponse({'success': False, 'error': 'Invalid coupon code'}, status=400)
    else:
        # Method not allowed or request is not AJAX
        print('big error')
        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

