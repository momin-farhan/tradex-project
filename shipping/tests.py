from django.test import TestCase, Client
from django.urls import reverse
from .models import Box, Order, OrderItem, Product
from .services import recommend_box, Item3D, can_pack_items_3d, dimensions_fit


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

        self.book = Product.objects.create(
            name="Book",
            length=20,
            width=15,
            height=3,
            weight=0.5,
        )

        self.keyboard = Product.objects.create(
            name="Keyboard",
            length=40,
            width=12,
            height=4,
            weight=1.0,
        )

        self.order = Order.objects.create()
        OrderItem.objects.create(
            order=self.order,
            product=self.laptop,
            quantity=1,
        )

    def test_laptop_recommends_medium_box(self):
        """Single laptop fits in Medium Box (35x25x15). Small Box (20x20x10) is too small."""
        recommended_box = recommend_box(self.order.id)
        self.assertIsNotNone(recommended_box)
        self.assertEqual(recommended_box.name, "Medium Box")

    def test_product_too_large_returns_no_box(self):
        """Product exceeding all box dimensions returns None."""
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
        """Heavy product exceeding max_weight returns None."""
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

    def test_empty_order_returns_no_box(self):
        """Empty order with no items returns None."""
        empty_order = Order.objects.create()
        recommended_box = recommend_box(empty_order.id)
        self.assertIsNone(recommended_box)

    def test_total_volume_exceeding_box_capacity_returns_no_box(self):
        """1000 small items exceeding total volume of largest box returns None."""
        small_item = Product.objects.create(
            name="Small Cube",
            length=5,
            width=5,
            height=5,
            weight=0.01,
        )
        volumetric_order = Order.objects.create()
        OrderItem.objects.create(
            order=volumetric_order,
            product=small_item,
            quantity=1000,
        )
        recommended_box = recommend_box(volumetric_order.id)
        self.assertIsNone(recommended_box)

    def test_multi_product_order_packing_success(self):
        """Multi-product order (Laptop + Keyboard + Book) packed together into Large Box."""
        multi_order = Order.objects.create()
        OrderItem.objects.create(order=multi_order, product=self.laptop, quantity=1)
        OrderItem.objects.create(order=multi_order, product=self.keyboard, quantity=1)
        OrderItem.objects.create(order=multi_order, product=self.book, quantity=1)

        recommended_box = recommend_box(multi_order.id)
        self.assertIsNotNone(recommended_box)
        self.assertEqual(recommended_box.name, "Large Box")

    def test_multi_product_spatial_failure_despite_volume_fit(self):
        """
        Tests multi-product 3D packing failure.
        Two items fit volume & individual dimensions, but cannot physically fit together
        inside a restricted box due to 3D spatial layout constraints.
        """
        # Box: 30 x 20 x 12 (Volume 7,200)
        test_box = Box.objects.create(
            name="Restricted Box",
            internal_length=30,
            internal_width=20,
            internal_height=12,
            max_weight=10,
            cost=15,
        )
        # Item A: 25 x 15 x 8 (Volume 3,000)
        # Item B: 25 x 15 x 8 (Volume 3,000)
        # Combined Volume = 6,000 <= 7,200 (Volume fits!)
        # Individual fit passes (25<=30, 15<=20, 8<=12).
        # BUT 3D spatial fit fails:
        # Along L (30): 25+25=50 > 30.
        # Along W (20): 15+15=30 > 20.
        # Along H (12): 8+8=16 > 12.
        flat_item = Product.objects.create(
            name="Flat Plate",
            length=25,
            width=15,
            height=8,
            weight=1.0,
        )
        spatial_order = Order.objects.create()
        OrderItem.objects.create(order=spatial_order, product=flat_item, quantity=2)

        # Should NOT pick Restricted Box; should pick Medium Box (35x25x15) or Large Box where they fit!
        recommended_box = recommend_box(spatial_order.id)
        self.assertIsNotNone(recommended_box)
        self.assertNotEqual(recommended_box.name, "Restricted Box")

    def test_quantity_affects_physical_packing_space(self):
        """
        Verifies quantity expansion in 3D packing space.
        1 Laptop (30x20x5) fits in Medium Box (35x25x15).
        4 Laptops (30x20x5 each) stacked along height require 20cm height (5x4=20cm),
        which exceeds Medium Box height (15cm), forcing recommendation of Large Box (50x40x30)!
        """
        multi_qty_order = Order.objects.create()
        OrderItem.objects.create(order=multi_qty_order, product=self.laptop, quantity=4)

        recommended_box = recommend_box(multi_qty_order.id)
        self.assertIsNotNone(recommended_box)
        self.assertEqual(recommended_box.name, "Large Box")

    def test_3d_rotation_enables_fit(self):
        """
        Verifies 6-DOF 3D rotation support.
        Item dimensions (5 x 30 x 20) fit inside Medium Box (35 x 25 x 15)
        only when rotated to (30 x 20 x 5).
        """
        tall_item = Product.objects.create(
            name="Standing Board",
            length=5,
            width=30,
            height=20,
            weight=1.0,
        )
        rotation_order = Order.objects.create()
        OrderItem.objects.create(order=rotation_order, product=tall_item, quantity=1)

        recommended_box = recommend_box(rotation_order.id)
        self.assertIsNotNone(recommended_box)
        self.assertEqual(recommended_box.name, "Medium Box")

    def test_zero_and_negative_quantity_ignored(self):
        """OrderItem with quantity <= 0 is safely ignored."""
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=self.laptop, quantity=0)

        recommended_box = recommend_box(order.id)
        self.assertIsNone(recommended_box)

    def test_invalid_product_dimensions_raises_value_error(self):
        """Creating an Item3D with non-positive dimensions raises ValueError."""
        with self.assertRaises(ValueError):
            Item3D(length=0, width=10, height=10, weight=1)

        with self.assertRaises(ValueError):
            Item3D(length=10, width=-5, height=10, weight=1)

    def test_invalid_product_weight_raises_value_error(self):
        """Creating an Item3D with negative weight raises ValueError."""
        with self.assertRaises(ValueError):
            Item3D(length=10, width=10, height=10, weight=-2.5)

    def test_boundary_exact_dimension_match(self):
        """Item with dimensions exactly equal to box internal dimensions fits."""
        exact_box = Box.objects.create(
            name="Exact Fit Box",
            internal_length=20,
            internal_width=20,
            internal_height=10,
            max_weight=5,
            cost=15,
        )
        exact_item = Product.objects.create(
            name="Exact Cube",
            length=20,
            width=20,
            height=10,
            weight=1,
        )
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=exact_item, quantity=1)

        recommended_box = recommend_box(order.id)
        self.assertIsNotNone(recommended_box)
        self.assertEqual(recommended_box.name, "Exact Fit Box")

    def test_boundary_exact_weight_match(self):
        """Order total weight exactly equal to box max_weight capacity fits."""
        weight_box = Box.objects.create(
            name="Weight Limit Box",
            internal_length=40,
            internal_width=40,
            internal_height=40,
            max_weight=10.0,
            cost=10,
        )
        heavy_item = Product.objects.create(
            name="10kg Item",
            length=10,
            width=10,
            height=10,
            weight=10.0,
        )
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=heavy_item, quantity=1)

        recommended_box = recommend_box(order.id)
        self.assertIsNotNone(recommended_box)
        self.assertEqual(recommended_box.name, "Weight Limit Box")

    def test_best_box_tie_breaking_volume(self):
        """
        When two boxes have identical cost ($25), the algorithm breaks ties by choosing
        the box with smaller internal volume to maximize space utilization and reduce void fill.
        """
        Box.objects.create(
            name="Huge Box Same Cost",
            internal_length=40,
            internal_width=40,
            internal_height=30,  # Volume = 48,000
            max_weight=10,
            cost=25,
        )
        Box.objects.create(
            name="Compact Box Same Cost",
            internal_length=30,
            internal_width=25,
            internal_height=15,  # Volume = 11,250
            max_weight=10,
            cost=25,
        )
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=self.laptop, quantity=1)

        recommended_box = recommend_box(order.id)
        self.assertIsNotNone(recommended_box)
        self.assertEqual(recommended_box.name, "Compact Box Same Cost")

    def test_best_box_tie_breaking_weight_margin(self):
        """
        When two boxes have identical cost ($25) and identical volume (12,000),
        the algorithm breaks ties by choosing the box with higher max_weight capacity.
        """
        Box.objects.create(
            name="Low Capacity Box",
            internal_length=30,
            internal_width=20,
            internal_height=20,  # Volume 12,000
            max_weight=5,
            cost=25,
        )
        Box.objects.create(
            name="High Capacity Box",
            internal_length=30,
            internal_width=20,
            internal_height=20,  # Volume 12,000
            max_weight=15,
            cost=25,
        )
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=self.laptop, quantity=1)

        recommended_box = recommend_box(order.id)
        self.assertIsNotNone(recommended_box)
        self.assertEqual(recommended_box.name, "High Capacity Box")

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

    def test_api_boxes_list(self):
        url = reverse("api-boxes-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("boxes", data)

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

    def test_api_simulate_recommendation_invalid_json_400(self):
        url = reverse("api-simulate")
        response = self.client.post(url, data="invalid json string", content_type="application/json")
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)

    def test_api_simulate_recommendation_empty_items_400(self):
        url = reverse("api-simulate")
        response = self.client.post(url, data={"items": []}, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)