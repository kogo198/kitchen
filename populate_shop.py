import os
import shutil
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_kitchenwareshop.settings')
django.setup()

from shop.models import Category, Product

def populate():
    print("Starting shop population script...")
    BASE_DIR = Path(__file__).resolve().parent
    STATIC_IMG_DIR = BASE_DIR / 'shop' / 'static' / 'shop' / 'images'
    MEDIA_IMG_DIR = BASE_DIR / 'media' / 'products'
    MEDIA_IMG_DIR.mkdir(parents=True, exist_ok=True)
    
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
            'description': 'Set of 5 heavy-gauge aluminium sufuria for everyday cooking. 1L to 7L.',
            'badge': 'POPULAR',
        },
        {
            'name': 'Stainless Steel Cooking Pot 10L',
            'category': 'sufuria',
            'price': 4500,
            'description': 'Premium large volume pot for heavy cooking.',
        },
        # Frying Pans
        {
            'name': 'Non-Stick Frying Pan 28cm',
            'category': 'pans',
            'price': 1850,
            'old_price': 2500,
            'description': 'Premium PFOA-free non-stick coating for easy cleaning.',
            'badge': 'SALE',
        },
        # Knives
        {
            'name': 'Professional Chef Knife 8"',
            'category': 'knives',
            'price': 1200,
            'description': 'High-carbon stainless steel blade for precision cutting.',
            'badge': 'NEW',
        },
        {
            'name': 'Paring Knife Set (3pcs)',
            'category': 'knives',
            'price': 450,
            'description': 'Three essential small knives for peeling and detail work.',
        },
        # Utensils
        {
            'name': 'Silicone Spatula Set',
            'category': 'utensils',
            'price': 850,
            'description': 'Heat-resistant silicone spatulas in various sizes.',
        },
        {
            'name': 'Wooden Cooking Spoons (5pcs)',
            'category': 'utensils',
            'price': 600,
            'description': 'Traditional handcrafted wooden spoons for non-stick pots.',
        },
        # Bowls & Storage
        {
            'name': 'Glass Mixing Bowls Set',
            'category': 'bowls',
            'price': 2200,
            'description': 'Set of 3 stackable tempered glass mixing bowls.',
        },
        {
            'name': 'Food Storage Containers (12pcs)',
            'category': 'bowls',
            'price': 1500,
            'description': 'Airtight plastic containers to keep food fresh.',
            'badge': 'HOT',
        },
        # Appliances
        {
            'name': 'High-Power Blender 1500W',
            'category': 'appliances',
            'price': 7500,
            'old_price': 9500,
            'description': 'Heavy duty commercial style blender for smoothies.',
            'badge': 'SALE',
        },
        {
            'name': 'Electric Kettle 1.7L',
            'category': 'appliances',
            'price': 2800,
            'description': 'Fast boiling cordless electric kettle.',
        },
        # Baking
        {
            'name': 'Non-Stick Baking Tray',
            'category': 'baking',
            'price': 950,
            'description': 'Heavy gauge carbon steel baking tray.',
        },
        {
            'name': 'Muffin Tin (12 Cup)',
            'category': 'baking',
            'price': 1100,
            'description': 'Standard 12-cup non-stick muffin and cupcake tin.',
        },
        # Accessories
        {
            'name': 'Digital Kitchen Scale',
            'category': 'accessories',
            'price': 1800,
            'description': 'Precise measurement up to 5kg with gram/oz toggle.',
        },
        {
            'name': 'Cotton Kitchen Apron',
            'category': 'accessories',
            'price': 750,
            'description': 'Durable cotton apron with front pockets.',
        }
    ]

    # Mapping of product name substrings to static image filenames
    image_mapping = {
        'Sufuria': 'pots.png',
        'Pot': 'pots.png',
        'Pan': 'pots.png',
        'Knife': 'knives.png',
        'Spoon': 'utensils.png',
        'Spatula': 'utensils.png',
        'Bowl': 'bowls.png',
        'Container': 'bowls.png',
        'Blender': 'blender.png',
        'Kettle': 'blender.png',
        'Baking': 'hero.png',
        'Muffin': 'hero.png',
        'Scale': 'utensils.png',
        'Apron': 'utensils.png',
    }

    for prod_data in products_data:
        cat_slug = prod_data.pop('category')
        category = category_objects.get(cat_slug)
        if category:
            name = prod_data['name']
            prod, created = Product.objects.get_or_create(name=name, category=category, defaults=prod_data)
            
            # Update image if missing
            if not prod.image:
                assigned = False
                for key, filename in image_mapping.items():
                    if key.lower() in name.lower():
                        source_path = STATIC_IMG_DIR / filename
                        if source_path.exists():
                            # Sanitize filename for Windows
                            clean_name = "".join(c for c in name if c.isalnum() or c in (' ', '_')).strip().replace(' ', '_').lower()
                            target_filename = f"{clean_name}.png"
                            target_path = MEDIA_IMG_DIR / target_filename
                            shutil.copy(source_path, target_path)
                            prod.image = f'products/{target_filename}'
                            prod.save()
                            assigned = True
                            break
                
                if not assigned:
                    # Fallback
                    source_path = STATIC_IMG_DIR / 'pots.png'
                    if source_path.exists():
                        clean_name = "".join(c for c in name if c.isalnum() or c in (' ', '_')).strip().replace(' ', '_').lower()
                        target_filename = f"{clean_name}.png"
                        target_path = MEDIA_IMG_DIR / target_filename
                        shutil.copy(source_path, target_path)
                        prod.image = f'products/{target_filename}'
                        prod.save()

            if created:
                print(f"Created product: {prod.name}")

    print("Success: Shop population complete with categories and products!")

if __name__ == '__main__':
    populate()
