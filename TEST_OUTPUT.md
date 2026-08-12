# Test Output

## Command

```bash
python manage.py test
```

## Results

```text
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
..............
----------------------------------------------------------------------
Ran 14 tests in 0.041s

OK
Destroying test database for alias 'default'...
Found 14 test(s).
```

## Summary of Executed Tests

1. `test_laptop_recommends_medium_box`: Verifies standard single-item laptop box recommendation.
2. `test_product_too_large_returns_no_box`: Verifies oversize product returns `None`.
3. `test_weight_exceeds_capacity_returns_no_box`: Verifies excessive product weight returns `None`.
4. `test_multiple_quantity_affects_total_weight`: Verifies quantity multiplier increases total weight beyond box capacity.
5. `test_empty_order_returns_no_box`: Verifies empty order returns `None`.
6. `test_total_volume_exceeding_box_capacity_returns_no_box`: Verifies total item volume exceeding box capacity returns `None`.
7. `test_api_recommend_view_success`: Verifies HTTP 200 response with JSON recommendation for Order #1.
8. `test_api_recommend_view_nonexistent_order_404`: Verifies HTTP 404 response for invalid order ID.
9. `test_api_recommend_view_no_suitable_box_404`: Verifies HTTP 404 response when no suitable box fits order constraints.
10. `test_index_view_renders_dashboard`: Verifies frontend dashboard HTML page renders successfully (HTTP 200).
11. `test_api_orders_list`: Verifies `/api/orders/` endpoint returns list of orders with items.
12. `test_api_boxes_list`: Verifies `/api/boxes/` endpoint returns list of registered shipping boxes.
13. `test_api_products_list`: Verifies `/api/products/` endpoint returns list of catalog products.
14. `test_api_simulate_recommendation_success`: Verifies `/api/simulate/` POST endpoint calculates live box recommendations for custom order item combinations.


