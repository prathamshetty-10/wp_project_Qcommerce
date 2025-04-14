from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem, Order, OrderItem
from products.models import Product
from django.db import transaction

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Get or create cart for the user
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Check if product is already in cart
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart, 
        product=product,
        defaults={'quantity': 1}
    )
    
    # If item already exists, increase quantity
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('cart_detail')

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    
    total = sum(item.subtotal() for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total': total
    }
    return render(request, 'cart/cart.html', context)

@login_required
@transaction.atomic
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()
    
    if not cart_items:
        return redirect('product_list')
    
    # Calculate total price
    total_price = sum(item.subtotal() for item in cart_items)
    
    # Create order
    order = Order.objects.create(
        user=request.user,
        total_price=total_price
    )
    
    # Create order items
    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            price=cart_item.product.price
        )
    
    # Clear the cart
    cart_items.delete()
    
    return render(request, 'cart/checkout.html', {'order': order})