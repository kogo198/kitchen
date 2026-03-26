from django.urls import path
from . import views

urlpatterns = [
    path('', views.shop, name='shop'),
    path('products/', views.products, name='products'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    path('payment/', views.payment, name='payment'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('place-order/', views.place_order, name='place_order'),
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    path('submit-review/<int:product_id>/', views.submit_review, name='submit_review'),
    path('newsletter-subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
]
