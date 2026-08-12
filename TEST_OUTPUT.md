# Automated Test Suite Output — Tradexa Box Selection System

## Command Executed

```bash
./venv/bin/python manage.py test
```

## Raw Output Log

```text
Found 26 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
..........................
----------------------------------------------------------------------
Ran 26 tests in 0.053s

OK
Destroying test database for alias 'default'...
```

## Summary of Executed Test Cases (26/26 Passed)

### 1. 3D Spatial Packing & Rotation Tests
1. `test_laptop_recommends_medium_box`: Verifies single laptop (30x20x5) fits into Medium Box (35x25x15) while Small Box (20x20x10) is rejected.
2. `test_3d_rotation_enables_fit`: Verifies 6-DOF 3D rotation support. Item with dimensions 5x30x20 fits into 35x25x15 box only when rotated to 30x20x5.
3. `test_multi_product_order_packing_success`: Verifies multi-product order (Laptop + Keyboard + Book) packed simultaneously into Large Box.
4. `test_multi_product_spatial_failure_despite_volume_fit`: Verifies 3D spatial packing failure. Two items whose total volume fits inside a box are correctly REJECTED because physical 3D layout bounds prevent side-by-side or stacked placement without overlapping.
5. `test_quantity_affects_physical_packing_space`: Verifies physical spatial expansion for order quantities. 1 Laptop fits in Medium Box (35x25x15), but 4 Laptops (30x20x5 each) stacked require 20cm height (5x4=20cm > 15cm), forcing recommendation of Large Box (50x40x30).

### 2. Business Logic & Tie-Breaking Tests
6. `test_best_box_tie_breaking_volume`: Verifies that when two boxes have identical cost ($25), the system breaks ties by selecting the box with smaller internal volume to minimize void fill (bubble wrap) and dimensional weight charges.
7. `test_best_box_tie_breaking_weight_margin`: Verifies that when two boxes have identical cost ($25) and identical volume (12,000 cm³), the system selects the box with higher `max_weight` capacity for a safety margin.
8. `test_boundary_exact_dimension_match`: Verifies item with dimensions matching box internal bounds exactly (20x20x10 item in 20x20x10 box) fits.
9. `test_boundary_exact_weight_match`: Verifies order total weight matching box `max_weight` capacity exactly (10.0kg in 10.0kg box) fits.

### 3. Edge Cases & Boundary Conditions
10. `test_product_too_large_returns_no_box`: Verifies oversized product exceeding all box dimensions returns `None`.
11. `test_weight_exceeds_capacity_returns_no_box`: Verifies overweight order exceeding max weight returns `None`.
12. `test_empty_order_returns_no_box`: Verifies order with 0 items returns `None`.
13. `test_total_volume_exceeding_box_capacity_returns_no_box`: Verifies 1000 small items exceeding total container volume returns `None`.
14. `test_zero_and_negative_quantity_ignored`: Verifies order items with quantity <= 0 are safely ignored.
15. `test_invalid_product_dimensions_raises_value_error`: Verifies zero or negative dimensions raise `ValueError` in `Item3D`.
16. `test_invalid_product_weight_raises_value_error`: Verifies negative weight raises `ValueError` in `Item3D`.

### 4. API Endpoints & View Tests
17. `test_api_recommend_view_success`: Verifies HTTP 200 JSON response for `/orders/1/recommend/`.
18. `test_api_recommend_view_nonexistent_order_404`: Verifies HTTP 404 response for non-existent order ID `99999`.
19. `test_api_recommend_view_no_suitable_box_404`: Verifies HTTP 404 response when no suitable box fits order constraints.
20. `test_index_view_renders_dashboard`: Verifies frontend dashboard HTML page renders successfully (HTTP 200).
21. `test_api_orders_list`: Verifies `/api/orders/` endpoint returns list of active orders with items.
22. `test_api_boxes_list`: Verifies `/api/boxes/` endpoint returns registered shipping boxes.
23. `test_api_products_list`: Verifies `/api/products/` endpoint returns catalog products.
24. `test_api_simulate_recommendation_success`: Verifies `/api/simulate/` POST endpoint calculates live box recommendations for custom order item combinations.
25. `test_api_simulate_recommendation_invalid_json_400`: Verifies `/api/simulate/` returns HTTP 400 Bad Request on malformed JSON payload.
26. `test_api_simulate_recommendation_empty_items_400`: Verifies `/api/simulate/` returns HTTP 400 Bad Request when items array is empty.
