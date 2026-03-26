from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from django.http import JsonResponse

from .models import Category, Product, Order, OrderItem, ContactMessage, NewsletterSubscriber, Review
from .mpesa import MpesaClient
import json
from django.views.decorators.csrf import csrf_exempt
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
    return render(request, 'shop/shop.html', {
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

    return render(request, 'shop/login.html', {'form': form})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('shop')

    form = SignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Welcome to KitchenCraft, {user.first_name or user.username}! 🎉')
        return redirect('shop')

    return render(request, 'shop/signup.html', {'form': form})


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
        
    return render(request, 'shop/products.html', {
        'products': products,
        'categories': categories,
        'active_cat': cat_slug
    })


def about(request):
    return render(request, 'shop/about.html')


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
        
    return render(request, 'shop/contact.html')




@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/dashboard.html', {
        'orders': orders,
        'reviews': reviews
    })


@login_required(login_url='login')
def payment(request):
    return render(request, 'shop/payment.html')


@login_required(login_url='login')
def place_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone = data.get('phone')
            payment_method = data.get('payment_method', 'mpesa')
            cart = data.get('cart', [])
            total = data.get('total', 0)

            if not cart:
                return JsonResponse({'status': 'error', 'message': 'Cart is empty'}, status=400)

            # Create Order
            order = Order.objects.create(
                user=request.user,
                phone_number=phone,
                payment_method=payment_method,
                total_amount=total,
                status='pending'
            )

            # Create Order Items
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product_name=item['name'],
                    product_price=item['price'],
                    quantity=item['qty'],
                    image_url=item.get('image', '')
                )

            # If M-Pesa, trigger STK Push
            if payment_method == 'mpesa':
                client = MpesaClient()
                response = client.stk_push(phone, total, f"Order {order.id}")
                
                if "ResponseCode" in response and response["ResponseCode"] == "0":
                    return JsonResponse({
                        'status': 'success', 
                        'message': 'STK Push sent to your phone! Please enter PIN.',
                        'order_id': order.id
                    })
                else:
                    return JsonResponse({
                        'status': 'warning', 
                        'message': 'Order created, but M-Pesa push failed. Please pay manually.',
                        'order_id': order.id,
                        'debug': response
                    })

            return JsonResponse({'status': 'success', 'message': 'Order placed successfully!', 'order_id': order.id})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@csrf_exempt
def mpesa_callback(request):
    """
    Safaricom calls this URL when a payment has been processed (Success or Fail)
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        print(f"M-PESA CALLBACK DATA: {data}")
        
        result_code = data.get('stkCallback', {}).get('ResultCode')
        if result_code == 0:
            # Payment Success!
            items = data.get('stkCallback', {}).get('CallbackMetadata', {}).get('Item', [])
            receipt_number = ""
            for item in items:
                if item.get('Name') == 'MpesaReceiptNumber':
                    receipt_number = item.get('Value')
            
            # Find the order via AccountReference or we can use metadata if passed
            # For now, let's assume we can match it (In production, use CheckoutRequestID)
            checkout_request_id = data.get('stkCallback', {}).get('CheckoutRequestID')
            # Mark the most recent pending order for this phone/amount as paid
            # (In a real app, you'd store the CheckoutRequestID in the Order model)
            order = Order.objects.filter(is_paid=False).order_by('-created_at').first()
            if order:
                order.is_paid = True
                order.transaction_id = receipt_number
                order.status = 'processing'
                order.save()

        return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})
    return JsonResponse({'status': 'error'}, status=400)


@login_required(login_url='login')
def submit_review(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment
        )
        messages.success(request, "Your review has been submitted! Thank you.")
        return redirect('products') # Or redirect back to product detail if it existed
    return redirect('products')


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

