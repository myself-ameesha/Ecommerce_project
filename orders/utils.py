from .models import Order

def get_or_create_order(request):
    # Check if there's an existing order associated with the current user session
    if 'order_id' in request.session:
        order_id = request.session['order_id']
        order = Order.objects.get(id=order_id)
    else:
        # If no existing order found, create a new order and associate it with the current user session
        order = Order.objects.create(user=request.user)  # Assuming user is authenticated
        request.session['order_id'] = order.id
    
    return order