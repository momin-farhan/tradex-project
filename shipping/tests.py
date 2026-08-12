from django.test import TestCase

from .models import Box, Order, OrderItem, Product
from .services import recommend_box


class BoxRecommendationTest(TestCase):

    def setUp(self):
        self.small_box = Box.objects.create(
            name="Small Box",
            internal_length=20,
            internal_width=20,
            internal_height=10,
            max_weight=5,
            cost=20,
        )

        self.medium_box = Box.objects.create(
            name="Medium Box",
            internal_length=35,
            internal_width=25,
            internal_height=15,
            max_weight=10,
            cost=30,
        )

        self.large_box = Box.objects.create(
            name="Large Box",
            internal_length=50,
            internal_width=40,
            internal_height=30,
            max_weight=20,
            cost=50,
        )

        self.laptop = Product.objects.create(
            name="Laptop",
            length=30,
            width=20,
            height=5,
            weight=2,
        )

        self.order = Order.objects.create()

        OrderItem.objects.create(
            order=self.order,
            product=self.laptop,
            quantity=1,
        )

    def test_laptop_recommends_medium_box(self):
        recommended_box = recommend_box(self.order.id)

        self.assertIsNotNone(recommended_box)
        self.assertEqual(recommended_box.name, "Medium Box")

    def test_product_too_large_returns_no_box(self):
        large_product = Product.objects.create(
            name="Oversized Product",
            length=100,
            width=100,
            height=100,
            weight=2,
        )

        oversized_order = Order.objects.create()

        OrderItem.objects.create(
            order=oversized_order,
            product=large_product,
            quantity=1,
        )

        recommended_box = recommend_box(oversized_order.id)

        self.assertIsNone(recommended_box)

    def test_weight_exceeds_capacity_returns_no_box(self):
        heavy_product = Product.objects.create(
            name="Heavy Product",
            length=10,
            width=10,
            height=10,
            weight=25,
        )

        heavy_order = Order.objects.create()

        OrderItem.objects.create(
            order=heavy_order,
            product=heavy_product,
            quantity=1,
        )

        recommended_box = recommend_box(heavy_order.id)

        self.assertIsNone(recommended_box)
        