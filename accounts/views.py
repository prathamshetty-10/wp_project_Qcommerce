from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from cart.models import Order
from django.contrib.auth import logout
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def dashboard_view(request):
    # Get user's recent orders
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'user': request.user,
        'recent_orders': recent_orders
    }
    return render(request, 'accounts/dashboard.html', context)

@csrf_protect
@require_POST
def logout_view(request):
    logout(request)
    return redirect('login')

def home_view(request):
    return render(request, 'home.html')