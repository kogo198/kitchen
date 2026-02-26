from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from django.http import JsonResponse

from .models import Category, Product, Order, OrderItem, ContactMessage, NewsletterSubscriber
# ---------------------------------------------------------------------------
# Extended signup form (adds first_name, last_name, email)
# ---------------------------------------------------------------------------
class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name  = forms.CharField(max_length=30, required=False)
    email      = forms.EmailField(required=False)

    class Meta(UserCreationForm.Meta):
        fields = ('username', 'first_name', 'last_name', 'email')


# ---------------------------------------------------------------------------
# Main shop / home page
# ---------------------------------------------------------------------------
def shop(request):
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:3]
    categories = Category.objects.all()[:6]
    return render(request, 'shop.html', {
        'featured_products': featured_products,
        'categories': categories
    })


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
def login_view(request):
    if request.user.is_authenticated:
        return redirect('shop')

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'Welcome back, {user.first_name or user.username}! 🎉')
        return redirect(request.GET.get('next', 'shop'))

    return render(request, 'login.html', {'form': form})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('shop')

    form = SignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Welcome to KitchenCraft, {user.first_name or user.username}! 🎉')
        return redirect('shop')

    return render(request, 'signup.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('shop')


# ---------------------------------------------------------------------------
# Static pages
# ---------------------------------------------------------------------------
def products(request):
    cat_slug = request.GET.get('cat', 'all')
    categories = Category.objects.all()
    
    if cat_slug == 'all':
        products = Product.objects.filter(is_active=True)
    else:
        products = Product.objects.filter(category__slug=cat_slug, is_active=True)
        
    return render(request, 'products.html', {
        'products': products,
        'categories': categories,
        'active_cat': cat_slug
    })


def about(request):
    return render(request, 'about.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        ContactMessage.objects.create(
            name=name, email=email, subject=subject, message=message
        )
        messages.success(request, "Your message has been sent successfully! We'll get back to you soon.")
        return redirect('contact')
        
    return render(request, 'contact.html')


# ---------------------------------------------------------------------------
# Hostel views (kept from original urls – not used in main shop navigation)
# ---------------------------------------------------------------------------
def hostels(request):
    return render(request, 'hostels.html')


def add_hostel(request):
    return render(request, 'add_hostel.html')


@login_required(login_url='login')
def payment(request):
    return render(request, 'payment.html')


# ---------------------------------------------------------------------------
# API & Interactivity
# ---------------------------------------------------------------------------
def api_hostels(request):
    return JsonResponse({'hostels': []})


def newsletter_subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            NewsletterSubscriber.objects.get_or_create(email=email)
            return JsonResponse({'status': 'success', 'message': 'Subscribed successfully!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

