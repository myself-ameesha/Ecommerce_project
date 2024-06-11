from django.shortcuts import render,get_object_or_404, redirect
from store.models import Product, Wishlist, ReviewRating
from category.models import category
from carts.views import _cart_id
from carts.models import CartItem , Variation
from django.contrib import messages
from django.core.paginator import EmptyPage , PageNotAnInteger , Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from orders.models import OrderProduct
from .forms import ReviewForm
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, category, Variation



def store(request, category_slug=None):
    categories = None
    products = Product.objects.filter(is_available=True).distinct()

    # Get unique sizes and colors from variations
    sizes = Variation.objects.filter(variation_category='size').values_list('variation_value', flat=True).distinct()
    colors = Variation.objects.filter(variation_category='color').values_list('variation_value', flat=True).distinct()

    selected_size = request.GET.get('size')
    selected_color = request.GET.get('color')

    # Apply filters
    if selected_size:
        products = products.filter(variation__variation_category='size', variation__variation_value=selected_size)
    if selected_color:
        products = products.filter(variation__variation_category='color', variation__variation_value=selected_color)

    if category_slug:
        categories = get_object_or_404(category, slug=category_slug)
        products = products.filter(category=categories)

    products = products.distinct()

    paginator = Paginator(products, 6)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = products.count()

    context = {
        'products': paged_products,
        'product_count': product_count,
        'sizes': sizes,
        'colors': colors,
        'selected_size': selected_size,
        'selected_color': selected_color,
    }
    return render(request, 'store/store.html', context)



def product_details(request, category_slug, product_slug):
    # Get the single product or return 404 if not found
    single_product = get_object_or_404(Product, category__slug=category_slug, slug=product_slug)

    # Check if the product is in the cart
    in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    

    if request.user.is_authenticated:  # Check if the user is authenticated
        try:
            single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
            in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
            in_wishlist = Wishlist.objects.filter(user=request.user, product=single_product).exists()
        except Exception as e:
            raise e
    else:
        in_wishlist = None
    
    orderproduct = None  # Initialize orderproduct as None
    if request.user.is_authenticated:  # Check if the user is authenticated
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            pass
    else:
        orderproduct = None

    
    # Get the reviews if single_product is not None
    reviews = []
    if single_product:

    #Get the reviews

        reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
    
    context = {
        'single_product': single_product,
        'in_cart' : in_cart if single_product else False,
        'orderproduct' : orderproduct if single_product else False,
        'in_wishlist': in_wishlist,
        'reviews' : reviews,
        
    }
    return render(request, 'store/product_details.html', context)


@login_required(login_url = 'loginn')
def search(request):
    keyword = request.GET.get('keyword', None)
    products = Product.objects.all()
    product_count = products.count()  # Initialize product_count

    if keyword:
        products = products.filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
        product_count = products.count()

        # Sorting options
    sort_by = request.GET.get('sort_by')
    if sort_by == 'price_low_high':
        products = products.order_by('price')
    elif sort_by == 'price_high_low':
        products = products.order_by('-price')
    elif sort_by == 'name_a_to_z':
        products = products.order_by('product_name')
    elif sort_by == 'name_z_to_a':
        products = products.order_by('-product_name')
    
    context = {
        'products' : products,
        'product_count' : product_count,
    }
    return render(request, 'store/store.html', context)


@login_required(login_url = 'loginn')
def add_wishlist(request, product_slug):
    try:
        product = Product.objects.get(slug=product_slug)
        variations = []  # Initialize an empty list to store variations

        # Get the selected variations from the request
        if request.method == "POST":
            for item in request.POST:
                if 'variation_id' in item:
                    variation_id = request.POST.get(item)
                    print(f"Variation ID: {variation_id}")
                    try:
                        variation = Variation.objects.get(id=variation_id)
                        variations.append(variation)
                    except Variation.DoesNotExist:
                        pass

        # Create the Wishlist item with the selected variations
        wishlist_item = Wishlist.objects.create(user=request.user, product=product)
        if variations:
            wishlist_item.variations.set(variations)


    except Product.DoesNotExist:
        return redirect('store')  # Redirect to home page if the product doesn't exist

    return redirect('wishlist')  # Redirect to the wishlist page after adding the product

    
@login_required(login_url = 'loginn')
def remove_from_wishlist(request, wishlist_item_id):
    wishlist_item = get_object_or_404(Wishlist, id=wishlist_item_id)
    wishlist_item.delete()
    return redirect('wishlist')


@login_required(login_url='loginn')
def wishlist(request):
    if request.method == 'POST':
        wishlist_item_id = request.POST.get('wishlist_item_id')
        if wishlist_item_id:
            wishlist_item = get_object_or_404(Wishlist, id=wishlist_item_id)
            wishlist_item.delete()
            return redirect('wishlist')

    wishlist_items = Wishlist.objects.filter(user=request.user)
    
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'store/wishlist.html', context)

@login_required(login_url = 'loginn')
def product_detaill(request, product_slug):
    try:
        single_product = Product.objects.get(slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
        in_wishlist = Wishlist.objects.filter(user=request.user, product=single_product).exists()
        
    except Exception as e:
        raise e
    
    
    context = {
        'single_product': single_product,
        'in_cart' : in_cart,
        'in_wishlist': in_wishlist,
        
        
    }
    return render(request, 'store/product_details.html', context)


@login_required(login_url = 'loginn')
def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == "POST":
        try:
            reviews = ReviewRating.objects.get(user__id = request.user.id, product__id = product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)

        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been Submitted.')
                return redirect(url)













