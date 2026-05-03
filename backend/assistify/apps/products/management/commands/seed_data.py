import random
from django.core.management.base import BaseCommand
from assistify.apps.products.models import Product, ProductBenefit, Offer
from assistify.apps.users.models import User
from assistify.apps.orders.models import Order, OrderItem
PRODUCTS = [
    {
        "id": 1,
        "name": "Blood Pressure Monitor",
        "description": "Digital BP monitor for accurate readings",
        "price": 2699,
        "emoji": "🩺",
        "benefits": [
            "FDA approved and clinically validated",
            "Large display for easy reading",
            "Stores up to 60 measurements",
            "Automatic inflation for comfort",
            "Detects irregular heartbeat",
        ],
        "related_ids": [2, 5],
    },
    {
        "id": 2,
        "name": "Pulse Oximeter",
        "description": "Finger pulse oximeter for measuring oxygen levels",
        "price": 1499,
        "emoji": "📊",
        "benefits": [
            "Medical-grade accuracy",
            "Fast reading in 1-2 seconds",
            "Portable and lightweight",
            "Low battery indicator",
            "Perfect for home monitoring",
        ],
        "related_ids": [1, 5],
    },
    {
        "id": 3,
        "name": "Digital Thermometer",
        "description": "Fast temperature reading device",
        "price": 899,
        "emoji": "🌡️",
        "benefits": [
            "Measures temperature in seconds",
            "High accuracy ±0.1°C",
            "Memory function for last reading",
            "Waterproof design",
            "Suitable for all ages",
        ],
        "related_ids": [1, 2],
    },
    {
        "id": 4,
        "name": "Smart Scale",
        "description": "Digital scale with BMI calculation",
        "price": 2399,
        "emoji": "⚖️",
        "benefits": [
            "Tracks weight and calculates BMI automatically",
            "Measures body fat percentage",
            "Stores up to 10 user profiles",
            "Bluetooth connectivity",
            "Mobile app integration",
        ],
        "related_ids": [5, 1],
    },
    {
        "id": 5,
        "name": "Heart Rate Monitor",
        "description": "Wearable monitor for 24/7 tracking",
        "price": 3899,
        "emoji": "❤️",
        "benefits": [
            "Monitors heart rate 24/7",
            "Provides health insights",
            "Water resistant design",
            "Long battery life (7-10 days)",
            "Syncs with smartphone app",
        ],
        "related_ids": [2, 4],
    },
    {
        "id": 6,
        "name": "Glucose Monitor",
        "description": "Blood glucose monitoring system",
        "price": 1799,
        "emoji": "🩸",
        "benefits": [
            "Essential for diabetes management",
            "Quick and painless testing",
            "Stores 500 test results",
            "Includes lancets and test strips",
            "Portable and easy to use",
        ],
        "related_ids": [1, 2],
    },
    {
        "id": 7,
        "name": "Nebulizer Machine",
        "description": "Compressor nebulizer for respiratory treatment",
        "price": 3200,
        "emoji": "🌬️",
        "benefits": [
            "Effective medication delivery",
            "Low noise operation",
            "Suitable for children and adults",
            "Easy to clean and maintain",
            "Compact and portable design",
        ],
        "related_ids": [3, 5],
    },
    {
        "id": 8,
        "name": "Infrared Thermometer",
        "description": "Non-contact forehead thermometer",
        "price": 1250,
        "emoji": "🌡️",
        "benefits": [
            "Instant reading in 1 second",
            "Non-contact for hygiene",
            "Fever alarm system",
            "Backlit LCD display",
            "Stores last 32 readings",
        ],
        "related_ids": [3, 2],
    },
    {
        "id": 9,
        "name": "Electric Heating Pad",
        "description": "Fast-heating pad for pain relief",
        "price": 1100,
        "emoji": "🔥",
        "benefits": [
            "3 heat settings",
            "Auto shut-off for safety",
            "Soft, washable cover",
            "Large size for full coverage",
            "Moist heat option",
        ],
        "related_ids": [5, 4],
    },
    {
        "id": 10,
        "name": "Posture Corrector",
        "description": "Adjustable back brace for posture support",
        "price": 650,
        "emoji": "🧍",
        "benefits": [
            "Improves posture and alignment",
            "Breathable material",
            "Discreet under clothing",
            "Adjustable straps",
            "Relieves back and neck pain",
        ],
        "related_ids": [4, 5],
    },
]
OFFERS = [
    {"product_id": 2, "discount_percent": 20, "discounted_price": 1199},
    {"product_id": 4, "discount_percent": 15, "discounted_price": 2039},
    {"product_id": 5, "discount_percent": 25, "discounted_price": 2924},
]
class Command(BaseCommand):
    help = "Seed database with initial Assistify products, offers, and user interactions for LightFM"
    def handle(self, *args, **options):
        self.stdout.write("Seeding products...")
        id_map = {}
        all_products = []
        for data in PRODUCTS:
            product, created = Product.objects.get_or_create(
                name=data["name"],
                defaults={
                    "description": data["description"],
                    "price": data["price"],
                    "emoji": data["emoji"],
                    "currency": "EGP",
                },
            )
            id_map[data["id"]] = product
            all_products.append(product)
            if created:
                for i, text in enumerate(data["benefits"]):
                    ProductBenefit.objects.create(product=product, text=text, order=i)
                self.stdout.write(self.style.SUCCESS(f"  Created: {product.name}"))
            else:
                self.stdout.write(f"  Exists:  {product.name}")
        for data in PRODUCTS:
            product = id_map[data["id"]]
            related = [id_map[rid] for rid in data["related_ids"] if rid in id_map]
            product.related_products.set(related)
        self.stdout.write("Seeding offers...")
        for offer_data in OFFERS:
            product = id_map.get(offer_data["product_id"])
            if product:
                offer, created = Offer.objects.get_or_create(
                    product=product,
                    defaults={
                        "discount_percent": offer_data["discount_percent"],
                        "discounted_price": offer_data["discounted_price"],
                    },
                )
                status = "Created" if created else "Exists"
                self.stdout.write(
                    self.style.SUCCESS(f"  {status}: {product.name} — {offer.discount_percent}% off")
                )
        self.stdout.write("Seeding user interactions for LightFM...")
        users = []
        for i in range(1, 6):
            username = f'user_{i}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': f'{username}@example.com'}
            )
            users.append(user)
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'  Created user: {username}')
        if users and all_products:
            for user in users:
                num_purchases = random.randint(2, 4)
                purchased_products = random.sample(all_products, num_purchases)
                order = Order.objects.create(
                    user=user, 
                    customer_email=user.email,
                    subtotal=0,
                    total=0,
                    shipping_fee=50
                )
                total_subtotal = 0
                for product in purchased_products:
                    OrderItem.objects.create(
                        order=order, 
                        product=product, 
                        product_name=product.name,
                        product_emoji=product.emoji,
                        unit_price=product.price,
                        quantity=1
                    )
                    total_subtotal += product.price
                order.subtotal = total_subtotal
                order.total = total_subtotal + order.shipping_fee
                order.save()
                self.stdout.write(f'  User {user.username} interacted with {num_purchases} products.')
        self.stdout.write(self.style.SUCCESS("\n✅ Seeding complete! LightFM now has data to learn from."))