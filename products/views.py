from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, Wishlist
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

# def product_list(request):
#     # Get filter parameters
#     category = request.GET.get('category')
#     condition = request.GET.get('condition')
    
#     # Start with all products
#     products = Product.objects.all()
    
#     # Apply filters if provided
#     if category:
#         products = products.filter(category__name=category)
#     if condition:
#         products = products.filter(condition=condition)
    
#     categories = Category.objects.all()
    
#     context = {
#         'products': products,
#         'categories': categories,
#     }
#     return render(request, 'products/product_list.html', context)

def product_list(request):
    # Start with all products
    products = Product.objects.all()
    
    # Get search and filter parameters
    search_query = request.GET.get('q', '')
    category = request.GET.get('category')
    condition = request.GET.get('condition')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_by = request.GET.get('sort_by', 'name')
    
    # Apply search if provided
    if search_query:
        products = products.filter(name__icontains=search_query) | products.filter(description__icontains=search_query)
    
    # Apply category filter if provided
    if category:
        products = products.filter(category__name=category)
    
    # Apply condition filter if provided
    if condition:
        products = products.filter(condition=condition)
    
    # Apply price range filters if provided
    if min_price:
        try:
            min_price = float(min_price)
            products = products.filter(price__gte=min_price)
        except ValueError:
            pass
    
    if max_price:
        try:
            max_price = float(max_price)
            products = products.filter(price__lte=max_price)
        except ValueError:
            pass
    
    # Apply sorting
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-id')  # Assuming newest products have higher IDs
    else:  # Default to name
        products = products.order_by('name')
    
    # Get all categories for sidebar
    categories = Category.objects.all()
    
    # Get all conditions for filter options
    conditions = [choice[0] for choice in Product.CONDITION_CHOICES]
    
    context = {
        'products': products,
        'categories': categories,
        'conditions': conditions,
        'search_query': search_query,
        'selected_category': category,
        'selected_condition': condition,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
    }
    
    return render(request, 'products/product_list.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # Check if the product is in the user's wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
    
    return render(request, 'products/product_detail.html', {
        'product': product,
        'in_wishlist': in_wishlist
    })

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'added' if created else 'already_exists',
            'message': 'Product added to wishlist!' if created else 'Product already in wishlist'
        })
    
    # Redirect back to the product page if not AJAX
    return redirect('product_detail', pk=product_id)

@login_required
def remove_from_wishlist(request, product_id):
    Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'removed',
            'message': 'Product removed from wishlist!'
        })
    
    return redirect('wishlist')

@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'products/wishlist.html', {
        'wishlist_items': wishlist_items
    })