from django.core.management.base import BaseCommand
from shipping.models import Product, Box, Order, OrderItem


class Command(BaseCommand):
    help = "Seed database with products, boxes, and orders for testing and UI demonstration."

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        # Create Boxes
        boxes_data = [
            {"name": "Small Box", "internal_length": 20, "internal_width": 20, "internal_height": 10, "max_weight": 5, "cost": 20.00},
            {"name": "Medium Box", "internal_length": 35, "internal_width": 25, "internal_height": 15, "max_weight": 10, "cost": 30.00},
            {"name": "Large Box", "internal_length": 50, "internal_width": 40, "internal_height": 30, "max_weight": 20, "cost": 50.00},
            {"name": "Extra Large Freight Box", "internal_length": 75, "internal_width": 70, "internal_height": 100, "max_weight": 40, "cost": 95.00},
        ]

        for data in boxes_data:
            Box.objects.get_or_create(name=data["name"], defaults=data)

        # Create Products
        products_data = [
            {"name": "Laptop", "length": 30, "width": 20, "height": 5, "weight": 2.0},
            {"name": "Mechanical Keyboard", "length": 45, "width": 15, "height": 4, "weight": 1.1},
            {"name": "27\" Gaming Monitor", "length": 62, "width": 38, "height": 12, "weight": 5.5},
            {"name": "Wireless Mouse", "length": 12, "width": 7, "height": 4, "weight": 0.15},
            {"name": "Noise-Canceling Headphones", "length": 20, "width": 18, "height": 9, "weight": 0.35},
            {"name": "Hardcover Textbook", "length": 26, "width": 19, "height": 4, "weight": 1.4},
            {"name": "Ergonomic Office Chair", "length": 68, "width": 65, "height": 95, "weight": 16.0},
        ]

        products = {}
        for data in products_data:
            p, _ = Product.objects.get_or_create(name=data["name"], defaults=data)
            products[data["name"]] = p

        # Create Orders if only 1 exists
        if Order.objects.count() <= 1:
            # Order 2: Keyboard + Mouse x2 + Headphones
            o2 = Order.objects.create()
            OrderItem.objects.create(order=o2, product=products["Mechanical Keyboard"], quantity=1)
            OrderItem.objects.create(order=o2, product=products["Wireless Mouse"], quantity=2)
            OrderItem.objects.create(order=o2, product=products["Noise-Canceling Headphones"], quantity=1)

            # Order 3: Gaming Monitor + Laptop
            o3 = Order.objects.create()
            OrderItem.objects.create(order=o3, product=products["27\" Gaming Monitor"], quantity=1)
            OrderItem.objects.create(order=o3, product=products["Laptop"], quantity=1)

            # Order 4: Ergonomic Office Chair
            o4 = Order.objects.create()
            OrderItem.objects.create(order=o4, product=products["Ergonomic Office Chair"], quantity=1)

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
