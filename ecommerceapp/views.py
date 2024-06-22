from django.shortcuts import render, redirect , get_object_or_404
from store.models import Product 
from .forms import RegistrationForm , AddressForm ,UserProfileForm , UserForm 
from .models import Account , UserProfile, Address
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.http import request
from carts.views import _cart_id
from carts.models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
import requests
from orders.models import Order , Wallet
from orders.models import OrderProduct , Coupon



#verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.conf import settings
import random



# Create your views here.
def index(request):
    products = Product.objects.all().filter(is_available=True)
    context={
        'products':products,
        }
    return render(request,'index.html',context)

def contact(request):
    return render(request,'contact.html')

def shopcart(request):
    return render(request,'shopcart.html')

def checkout(request):
    return render(request,'checkout.html')

def wishlist(request):
    return render(request,'wishlist.html')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username=email.split("@")[0]           

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.username = user.email.split('@')[0]  # Use email as username
            user.save()

            # user activation
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('ecommerceapp/account_verification_email.html', {
                'user' : user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            to_email = user.email 
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            # Redirect to OTP verification page
            # return redirect(reverse('verify_otp'))
            messages.success(request, 'Thank you for Registering with us, we have sent you verification email to your email address. Please verify it')
            return redirect(reverse('loginn')+'?command=verification&email='+email)
    else:
        form = RegistrationForm()
    context = {
        'form' : form,

        }
    return render(request, 'ecommerceapp/register.html', context)


def loginn(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart) 

                    # getting the product variations by cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    #Get the cart items from the user to access his product variation
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    #product_variation = [1, 2, 3, 4, 6]
                    #ex_var_list = [4, 6, 3, 5]
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass

            auth.login(request, user)
            #messages.success(request, 'You are now logged in')
            if user.is_superadmin:
                # Redirect superuser to admin home 
                return redirect('adminn:adminhome')
            else:
                # Redirect regular user to user home
                messages.success(request, 'You are now logged in')
                url = request.META.get('HTTP_REFERER')
                try:
                    query = requests.utils.urlparse(url).query
                    #next=/cart/checkout/
                    params = dict(x.split('=') for x in query.split('&'))
                    if 'next' in params:
                        nextPage = params['next']
                        return redirect(nextPage)
                    
                except:
                    return redirect('dashboard')
        else:
            messages.error(request, "Invalid Login Credentials")
            return redirect('loginn')
    return render(request, 'ecommerceapp/loginn.html')



@login_required(login_url = 'loginn')
def logout(request):
    auth.logout(request)
    messages.success(request, "you are logged out")
    return redirect('loginn')



def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated')
        return redirect('loginn')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')
   
def forgotpassword(request):
    if request.method == "POST":
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # reset password email
            current_site = get_current_site(request)
            mail_subject = 'Please reset your Password'
            message = render_to_string('ecommerceapp/reset_password_email.html', {
                'user' : user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            to_email = email 
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address')
            return redirect('loginn')

        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgotpassword')
    return render(request,'ecommerceapp/forgotpassword.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your Password')
        return redirect('resetpassword')
    else:
        messages.error(request, "This link has been expired!")
        return redirect('loginn')


def resetpassword(request):
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset Successfull')
            return redirect('loginn')
        else:
            messages.error(request, 'Password do not match')
            return redirect('resetpassword')
    else:
        return render(request, 'ecommerceapp/resetpassword.html')
    

@login_required(login_url = 'loginn')  
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()
    user_full_name = request.user.full_name  # Corrected this line

    context = {
        'orders_count' : orders_count,
        'user_full_name': user_full_name,
        'user': request.user,

    }
    return render(request, 'ecommerceapp/dashboard.html',context)


@login_required(login_url = 'loginn')
def edit_profile(request):
    user = request.user
    profile = UserProfile.objects.get_or_create(user=user)[0]
    addresses = Address.objects.filter(user=user)

    if request.method == 'POST':
        address_form = AddressForm(request.POST)
        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.user = user
            address.save()
            profile.addresses.add(address)
            messages.success(request, 'Address added successfully')
            return redirect('edit_profile')
    else:
        address_form = AddressForm()

    context = {
        'address_form': address_form,
        'addresses': addresses
    }
    return render(request, 'ecommerceapp/edit_profile.html', context)

@login_required(login_url = 'loginn')
def add_address(request):
    if request.method == 'POST':
        address_form = AddressForm(request.POST)
        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address added successfully')
            return redirect('edit_profile')
    else:
        address_form = AddressForm()

    context = {
        'address_form': address_form,
    }
    return render(request, 'ecommerceapp/add_address.html', context)

@login_required(login_url = 'loginn')
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id)
    if request.method == 'POST':
        address_form = AddressForm(request.POST, instance=address)
        if address_form.is_valid():
            address_form.save()
            messages.success(request, 'Address updated successfully')
            return redirect('edit_profile')
    else:
        address_form = AddressForm(instance=address)

    context = {
        'address_form': address_form
    }
    return render(request, 'ecommerceapp/edit_address.html', context)


@login_required(login_url='loginn') 
def editprofile(request):
    user = request.user  # Get the current user
    user_profile = UserProfile.objects.get(user=user)  # Get the related user profile

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)  # Update user form with instance
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)  # Update profile form with instance

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()  # Save user form
            profile_form.save()  # Save profile form
            messages.success(request, 'Profile updated successfully!')
            return redirect('edit_profile')  # Redirect to user profile after successful update
    else:
        user_form = UserForm(instance=user)  # Pre-populate user form with current data
        profile_form = UserProfileForm(instance=user_profile)  # Pre-populate profile form with current data

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }

    return render(request, 'ecommerceapp/editprofile.html', context)


@login_required(login_url = 'loginn')
def delete_address(request, address_id):
    address = Address.objects.get(pk=address_id)
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully')
    return redirect('edit_profile')

@login_required(login_url='loginn')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered = True).order_by('-created_at')
    context = {
        'orders' : orders,

    }
    return render(request, 'ecommerceapp/my_orders.html', context)



@login_required(login_url='loginn')   
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        user = Account.objects.get(username__exact = request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, 'Password Updated Successfully')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match')
            return redirect('change_password')
            
    return render(request, 'ecommerceapp/change_password.html')


@login_required(login_url='loginn') 
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number = order_id)
    order = Order.objects.get(order_number = order_id)
    subtotal = 0
    for i in order_detail:
        product = Product.objects.get(id=i.product_id)  # Retrieve the product
        subtotal += product.price_after_discount() * i.quantity  # Calculate subtotal using price_after_discount


    # Fetching payment method from the related Payment object
    payment_method = order.payment.payment_method if order.payment else None

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
        'order_detail' : order_detail,
        'order' : order,
        'subtotal' : subtotal,
        'payment': order.payment,
        'payment_method': payment_method,
        'coupon_discount': coupon_discount,  # Pass coupon discount to the context
        
    }

    return render(request, 'ecommerceapp/order_detail.html', context)

@login_required(login_url = 'loginn')
def cancel_orderr(request, order_number):
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
    return redirect('my_orders')  # Redirect to a success page after cancellation
    
@login_required(login_url = 'loginn')
def return_order(request):
    if request.method == 'POST':
        order_number = request.POST.get('order_number')
        try:
            order = Order.objects.get(order_number=order_number)
            # Check if the order status is 'Completed'
            if order.status == 'Completed':
                # Set the order status to 'Returned'
                order.status = 'Returned'
                order.save()
                return redirect('my_orders')
        except Order.DoesNotExist:
            # Handle the case where the order does not exist
            pass
    # Redirect to a specific URL after processing the return request
    return redirect('my_orders')  # Replace 'order_return_confirmation' with the desired URL name


@login_required(login_url='loginn')
def user_wallet(request):
    try:
        wallet = Wallet.objects.get(account=request.user)
    except ObjectDoesNotExist:
        # If wallet doesn't exist, create a new one for the user
        wallet = Wallet.objects.create(account=request.user, wallet_balance=0.00)
    
    # Fetching orders with payment method 'Wallet'
    orders_wallet = Order.objects.filter(user=request.user, payment__payment_method='Wallet').order_by('-created_at')
    
    return render(request, 'ecommerceapp/user_wallet.html', {'wallet': wallet, 'orders_wallet': orders_wallet})


    

    
    
















