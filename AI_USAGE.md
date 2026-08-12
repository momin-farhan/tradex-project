# AI Usage Document

## 1. Tools Used

- **ChatGPT / Antigravity Agentic Assistant**: Used for project planning, architecture design, algorithm design, Django implementation, and automated test creation.

## 2. Prompts Provided

1. *"Explain how I should structure and demonstrate this Django Box Selection assignment from scratch."*
2. *"Help me design the models for Product, Box, Order, and OrderItem with fields for dimensions and weight."*
3. *"Write a service function `recommend_box(order_id)` that selects the cheapest suitable shipping box based on product dimensions, weight capacity, and rotation."*
4. *"Add checks for total volumetric capacity and handle empty orders or missing orders gracefully with 404 responses."*
5. *"Write automated test cases using Django TestCase covering standard orders, oversize products, overweight orders, volume overflow, and API endpoint views."*
6. *"Configure GitHub Actions CI workflow to run `manage.py test` automatically."*

## 3. What Output Was Accepted

- Django model definitions for `Product`, `Box`, `Order`, and `OrderItem` in `shipping/models.py`.
- Service-layer separation pattern placing `recommend_box` inside `shipping/services.py`.
- Dimension sorting logic (`sorted([length, width, height])`) to handle 3D box orientation/rotation.
- Ascending cost ordering (`Box.objects.all().order_by('cost')`) to guarantee selecting the cheapest suitable box.
- RESTful JSON API view returning `order_id`, `recommended_box`, and `cost`.
- GitHub Actions CI workflow definition in `.github/workflows/test.yml`.

## 4. What Output Was Rejected or Modified

- **Initial item-by-item dimension check**: The initial AI suggestion checked individual product dimensions in isolation without considering total order volume. This was modified to calculate total order volume (`sum(length * width * height * qty)`) and enforce `total_volume <= box_volume`.
- **Unhandled exceptions in view**: The initial view did not catch `Order.DoesNotExist`, causing HTTP 500 server errors on invalid order IDs. Modified `recommend_box_view` to catch `Order.DoesNotExist` and return a clean HTTP 404 response.
- **Hardcoded test database dependencies**: Initial test recommendations depended on pre-existing database rows. Modified tests to use Django's `TestCase` isolation with `setUp()` fixture creation.

## 5. Mistakes Made by AI

1. **Omission of Volumetric Capacity**: AI initially assumed that if each item individually fits inside a box, the entire multi-item order fits, ignoring combined volume constraints.
2. **Missing Exception Handling**: AI omitted `try...except Order.DoesNotExist` in the API view.
3. **Environment setup command mismatches**: Initial virtual environment activation instructions used Linux syntax on Windows environments.

## 6. How Final Code Was Verified

1. **Automated Unit Testing**: Executed `./venv/bin/python manage.py test` to run all 9 test cases covering dimension constraints, weight capacity, volumetric overflow, non-existent orders, and JSON API HTTP responses.
2. **Django System Checks**: Ran `python manage.py check` to verify model schemas and migrations.
3. **API Validation**: Sent HTTP requests to `/orders/1/recommend/` and verified response payload structure and status codes.
4. **CI Workflow Verification**: Verified syntax of `.github/workflows/test.yml`.

---

## 7. What I Learned in This Assignment

Through completing this assignment, I learned:

- **Domain Modeling**: How to structure e-commerce domain models (`Product`, `Box`, `Order`, `OrderItem`) with precise Decimal representation for dimensions and weight.
- **Service Layer Architecture**: The value of separating business logic (`services.py`) from request/response handling (`views.py`), making the core box recommendation algorithm clean, reusable, and easy to unit test.
- **Spatial Fitting & Constraints**: How to implement rotation-invariant fitting using dimension sorting, combined with weight capacity and total volumetric boundary checks.
- **Defensive Error Handling**: Properly handling edge cases like empty orders, oversized/overweight items, and non-existent database records with clean RESTful JSON responses.
- **Automated Testing & CI/CD**: How to write unit tests using Django's test framework and set up automated GitHub Actions workflows for continuous integration.
- **Critical AI Oversight**: How to use AI as an efficiency assistant while maintaining rigorous code inspection to catch logic gaps like missing volumetric constraints or exception handling.