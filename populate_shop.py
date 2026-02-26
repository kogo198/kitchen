import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_kitchenwareshop.settings')
django.setup()

from shop.models import Category, Product

def populate():
    print("Starting shop population script...")
    
    # 1. Create Categories
    categories_data = [
        {'name': 'Sufuria & Pots', 'slug': 'sufuria'},
        {'name': 'Frying Pans', 'slug': 'pans'},
        {'name': 'Knives', 'slug': 'knives'},
        {'name': 'Utensils', 'slug': 'utensils'},
        {'name': 'Bowls & Storage', 'slug': 'bowls'},
        {'name': 'Appliances', 'slug': 'appliances'},
        {'name': 'Baking', 'slug': 'baking'},
        {'name': 'Accessories', 'slug': 'accessories'},
    ]
    
    category_objects = {}
    for cat_data in categories_data:
        cat, created = Category.objects.get_or_create(name=cat_data['name'], defaults={'slug': cat_data['slug']})
        category_objects[cat_data['slug']] = cat
        if created:
            print(f"Created category: {cat.name}")

    # 2. Create Products
    products_data = [
        # Sufuria & Pots
        {
            'name': 'Aluminium Sufuria Set (5pcs)',
            'category': 'sufuria',
            'price': 3200,
            'old_price': 4000,
            'description': 'Set of 5 heavy-gauge aluminium sufuria in assorted sizes (1L, 2L, 3L, 5L, 7L) with lids.',
            'badge': 'POPULAR',
            'is_featured': True
        },
        {
            'name': 'Stainless Steel Cooking Pot 10L',
            'category': 'sufuria',
            'price': 4500,
            'description': 'Premium stainless steel pot, 10 litre capacity. Tri-ply base for even heat distribution.',
            'badge': 'NEW',
            'is_featured': False
        },
        {
            'name': 'Pressure Cooker 7.5L',
            'category': 'sufuria',
            'price': 6800,
            'old_price': 8500,
            'description': 'Safety-certified stainless steel pressure cooker. 7.5 litre. Cooks beans up to 70% faster.',
            'badge': 'SALE',
            'is_featured': True
        },
        # Frying Pans
        {
            'name': 'Non-Stick Frying Pan 28cm',
            'category': 'pans',
            'price': 1850,
            'old_price': 2500,
            'description': 'PFOA-free granite-coated non-stick frying pan. 28cm diameter.',
            'badge': 'SALE',
            'is_featured': True
        },
        # Appliances
        {
            'name': 'High-Power Blender 1500W',
            'category': 'appliances',
            'price': 7500,
            'old_price': 9500,
            'description': '1500-watt professional blender with 6 pre-set programmes. 1.5L BPA-free jar.',
            'badge': 'SALE',
            'is_featured': True
        },
        {
            'name': 'Electric Kettle 1.7L',
            'category': 'appliances',
            'price': 2800,
            'description': '1.7 litre stainless steel electric kettle with 1500W rapid boil.',
            'badge': 'NEW',
            'is_featured': False
        }
    ]

    for prod_data in products_data:
        cat_slug = prod_data.pop('category')
        category = category_objects.get(cat_slug)
        if category:
            prod, created = Product.objects.get_or_create(name=prod_data['name'], category=category, defaults=prod_data)
            if created:
                print(f"Created product: {prod.name}")

    print("Success: Shop population complete!")

if __name__ == '__main__':
    populate()
