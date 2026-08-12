from django.test import TestCase, Client
from django.urls import reverse

from .models import Box, Order, OrderItem, Product
from .services import recommend_box


class BoxRecommendationTest(TestCase):

    def setUp(self):
        self.client = Client()

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

    def test_multiple_quantity_affects_total_weight(self):
        order = Order.objects.create()

        OrderItem.objects.create(
            order=order,
            product=self.laptop,
            quantity=11,
        )

        recommended_box = recommend_box(order.id)

        self.assertIsNone(recommended_box)

    def test_empty_order_returns_no_box(self):
        empty_order = Order.objects.create()
        recommended_box = recommend_box(empty_order.id)
        self.assertIsNone(recommended_box)

    def test_total_volume_exceeding_box_capacity_returns_no_box(self):
        # Create small product (5x5x5 = 125 volume, weight=0.01)
        small_item = Product.objects.create(
            name="Small Cube",
            length=5,
            width=5,
            height=5,
            weight=0.01,
        )
        # 1000 small cubes = 125,000 volume. Large box volume is 60,000.
        volumetric_order = Order.objects.create()
        OrderItem.objects.create(
            order=volumetric_order,
            product=small_item,
            quantity=1000,
        )
        recommended_box = recommend_box(volumetric_order.id)
        self.assertIsNone(recommended_box)

    def test_api_recommend_view_success(self):
        url = reverse("recommend-box", kwargs={"order_id": self.order.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["recommended_box"], "Medium Box")
        self.assertEqual(data["cost"], "30.00")

    def test_api_recommend_view_nonexistent_order_404(self):
        url = reverse("recommend-box", kwargs={"order_id": 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("error", data)

    def test_api_recommend_view_no_suitable_box_404(self):
        heavy_product = Product.objects.create(
            name="Super Heavy",
            length=10,
            width=10,
            height=10,
            weight=500,
        )
        heavy_order = Order.objects.create()
        OrderItem.objects.create(order=heavy_order, product=heavy_product, quantity=1)

        url = reverse("recommend-box", kwargs={"order_id": heavy_order.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data["error"], "No suitable box found")

    def test_index_view_renders_dashboard(self):
        url = reverse("index")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tradexa Box Recommender")

    def test_api_orders_list(self):
        url = reverse("api-orders-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("orders", data)
        self.assertGreaterEqual(len(data["orders"]), 1)

    def test_api_boxes_list(self):
        url = reverse("api-boxes-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("boxes", data)
        self.assertEqual(len(data["boxes"]), 3)

    def test_api_products_list(self):
        url = reverse("api-products-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("products", data)

    def test_api_simulate_recommendation_success(self):
        url = reverse("api-simulate")
        payload = {"items": [{"product_id": self.laptop.id, "quantity": 1}]}
        response = self.client.post(url, data=payload, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["recommended_box"], "Medium Box")