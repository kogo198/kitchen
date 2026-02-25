from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import Category, Product, Order, OrderItem, ContactMessage, NewsletterSubscriber


# ---------------------------------------------------------------------------
# Customize admin site branding
# ---------------------------------------------------------------------------
admin.site.site_header = '🍳 KitchenCraft Admin'
admin.site.site_title = 'KitchenCraft Admin Panel'
admin.site.index_title = 'Welcome to KitchenCraft Dashboard'


# ---------------------------------------------------------------------------
# Category Admin
# ---------------------------------------------------------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('icon', 'name', 'slug', 'product_count', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

    def product_count(self, obj):
        count = obj.products.count()
        return format_html('<strong>{}</strong>', count)
    product_count.short_description = 'Products'


# ---------------------------------------------------------------------------
# Product Admin
# ---------------------------------------------------------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'display_price', 'badge', 'is_featured', 'is_active', 'created_at')
    list_filter = ('category', 'badge', 'is_featured', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('is_featured', 'is_active', 'badge')
    list_per_page = 25
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Product Info', {
            'fields': ('name', 'description', 'category', 'image')
        }),
        ('Pricing', {
            'fields': ('price', 'old_price')
        }),
        ('Display Options', {
            'fields': ('badge', 'is_featured', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def display_price(self, obj):
        if obj.old_price:
            return format_html(
                '<span style="color:#e74c3c;text-decoration:line-through;">KES {}</span> '
                '<strong style="color:#27ae60;">KES {}</strong> '
                '<span style="background:#27ae60;color:#fff;padding:2px 6px;border-radius:4px;font-size:11px;">-{}%</span>',
                obj.old_price, obj.price, obj.discount_percent
            )
        return format_html('<strong>KES {}</strong>', obj.price)
    display_price.short_description = 'Price'


# ---------------------------------------------------------------------------
# Order Admin (with inline items)
# ---------------------------------------------------------------------------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'product_price', 'quantity', 'subtotal')

    def subtotal(self, obj):
        return f'KES {obj.subtotal:,.2f}'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'status_badge', 'payment_method', 'display_total', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'phone_number')
    list_editable = ()
    readonly_fields = ('user', 'payment_method', 'phone_number', 'total_amount', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    list_per_page = 20

    fieldsets = (
        ('Order Details', {
            'fields': ('user', 'status', 'payment_method', 'phone_number')
        }),
        ('Financials', {
            'fields': ('total_amount',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def order_id(self, obj):
        return format_html('<strong>#{}</strong>', obj.id)
    order_id.short_description = 'Order'

    def status_badge(self, obj):
        colors = {
            'pending': '#f39c12',
            'processing': '#3498db',
            'shipped': '#9b59b6',
            'delivered': '#27ae60',
            'cancelled': '#e74c3c',
        }
        color = colors.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def display_total(self, obj):
        return format_html('<strong style="color:#27ae60;">KES {:,.2f}</strong>', obj.total_amount)
    display_total.short_description = 'Total'

    def has_add_permission(self, request):
        return False  # Orders come from customers, not admin


# ---------------------------------------------------------------------------
# Contact Messages Admin
# ---------------------------------------------------------------------------
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name', 'email', 'is_read_badge', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_editable = ()
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    list_per_page = 20

    def is_read_badge(self, obj):
        if obj.is_read:
            return format_html('<span style="color:#27ae60;font-weight:600;">✅ Read</span>')
        return format_html('<span style="color:#e74c3c;font-weight:600;">🔴 Unread</span>')
    is_read_badge.short_description = 'Status'

    def has_add_permission(self, request):
        return False  # Messages come from customers

    actions = ['mark_as_read', 'mark_as_unread']

    @admin.action(description='Mark selected as read')
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description='Mark selected as unread')
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)


# ---------------------------------------------------------------------------
# Newsletter Subscribers Admin
# ---------------------------------------------------------------------------
@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'subscribed_at')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email',)
    list_per_page = 30

    def has_add_permission(self, request):
        return False  # Subscribers come from the frontend
