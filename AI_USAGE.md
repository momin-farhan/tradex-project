# Comprehensive AI Usage & Iterative Engineering Document

## 1. Overview & AI Assistance Strategy

During the development of the **Tradexa Box Selection System**, AI tooling (ChatGPT / Antigravity Agentic Assistant) was utilized as an efficiency accelerator for scaffold creation, architectural brainstorming, initial model design, and API endpoint drafting.

Crucially, **AI-generated output was not accepted blindly**. All AI recommendations were subjected to rigorous developer review, empirical testing, and iterative refactoring. When initial AI proposals failed complex domain requirements—such as multi-product 3D packing geometry, order quantity spatial expansion, and edge-case boundary validation—the developer actively intervened to redesign algorithms, implement 3D spatial packing heuristics, add strict input validation, and expand test coverage.

---

## 2. Iterative Review, Correction, and Refactoring Log

### Cycle 1: Single-Product vs Multi-Product 3D Physical Packing

- **Initial Developer Prompt**:
  > *"Write a service function `recommend_box(order_id)` that selects the cheapest suitable shipping box based on product dimensions, weight capacity, and rotation."*

- **Initial AI Output Received**:
  ```python
  def dimensions_fit(product, box):
      # AI generated simple 1D sorted dimension check per product
      p_dims = sorted([product.length, product.width, product.height])
      b_dims = sorted([box.internal_length, box.internal_width, box.internal_height])
      return all(p <= b for p, b in zip(p_dims, b_dims))

  def recommend_box(order_id):
      ...
      for box in Box.objects.all().order_by("cost"):
          if box.max_weight >= total_weight and box_volume >= total_volume:
              if all(dimensions_fit(item.product, box) for item in items):
                  return box
  ```

- **Developer Code Review & Failure Identification**:
  - **Critique**: The AI's proposed solution checks if each product *individually* fits inside the box. It calculates total volume, but completely ignores physical 3D spatial arrangements when multiple items (or multiple quantities of the same item) are packed together in the same box!
  - **Concrete Counter-Example**: Consider two plates (25x15x8 cm each, volume 3,000 cm³ each). A box of 30x20x12 cm (volume 7,200 cm³) has enough total volume for both plates (6,000 $\le$ 7,200). Each plate individually fits (25$\le$30, 15$\le$20, 8$\le$12). However, two plates *cannot physically fit together* because stacking them requires 16 cm height ($8+8=16 > 12$), placing them side-by-side along length requires 50 cm ($25+25=50 > 30$), and side-by-side along width requires 30 cm ($15+15=30 > 20$). The AI's code would incorrectly claim they fit!

- **Developer Correction & Implementation**:
  - Rejected the AI's naive item-by-item check.
  - Implemented an **Item3D** model class and an **Extreme Points 3D Bin Packing Engine** (`can_pack_items_3d` and `_try_pack_extreme_points`) with 6-DOF rotational evaluation and non-overlapping 3D spatial coordinate tracking.

---

### Cycle 2: Quantity Handling for Physical Packing Space

- **Initial Developer Prompt**:
  > *"Ensure quantity is considered when evaluating order items for box recommendations."*

- **Initial AI Output Received**:
  ```python
  total_weight = sum(item.product.weight * item.quantity for item in items)
  total_volume = sum((item.product.length * item.product.width * item.product.height) * item.quantity for item in items)
  ```

- **Developer Code Review & Failure Identification**:
  - **Critique**: The AI correctly multiplied `quantity` for scalar sums like `total_weight` and `total_volume`, but kept the 3D dimension check as `dimensions_fit(item.product, box)`.
  - **Flaw**: If an order contains 4 Laptops (30x20x5 cm each), `dimensions_fit` checked 1 Laptop against the box. A Medium Box (35x25x15 cm) passed because 1 Laptop fits easily. But 4 Laptops stacked physically require 20 cm height ($5 \times 4 = 20 \text{ cm} > 15 \text{ cm}$), exceeding the Medium Box capacity and requiring a Large Box!

- **Developer Correction & Implementation**:
  - Created `build_3d_items_from_order_items()` to expand each `OrderItem` with `quantity = N` into $N$ discrete `Item3D` bounding box objects.
  - Fed all $N$ expanded 3D objects directly into the 3D Bin Packing simulation engine.

---

### Cycle 3: Edge Cases, Input Validation, and Exception Handling

- **Initial Developer Prompt**:
  > *"Handle invalid order IDs, missing items, and zero/negative product dimensions."*

- **Initial AI Output Received**:
  ```python
  def recommend_box_view(request, order_id):
      box = recommend_box(order_id)
      return JsonResponse({"recommended_box": box.name, "cost": str(box.cost)})
  ```

- **Developer Code Review & Failure Identification**:
  - **Critique**: The AI code lacked exception handling. Passing an unmapped `order_id` triggered an uncaught `Order.DoesNotExist` exception resulting in HTTP 500 server crashes. It also allowed invalid database entries with zero or negative dimensions/weights to silently pass or cause division-by-zero errors.

- **Developer Correction & Implementation**:
  - Wrapped views with explicit `try...except (Order.DoesNotExist, ValueError)` blocks returning clean HTTP 404 and HTTP 400 JSON payloads.
  - Added strict validation inside `Item3D.__init__`:
    ```python
    if self.length <= 0 or self.width <= 0 or self.height <= 0:
        raise ValueError(f"Invalid product dimensions for '{name}': {length}x{width}x{height}. Dimensions must be positive.")
    if self.weight < 0:
        raise ValueError("Weight cannot be negative.")
    ```

---

### Cycle 4: Definition of "Best Box" & Tie-Breaking Criteria

- **Initial Developer Prompt**:
  > *"Sort boxes to find the best recommendation."*

- **Initial AI Output Received**:
  ```python
  Box.objects.all().order_by("cost")
  ```

- **Developer Code Review & Failure Identification**:
  - **Critique**: Sorting strictly by `cost` leaves tie-breaking undefined when multiple boxes have identical prices. In warehouse fulfillment, selecting a huge 50x50x50 box over a compact 30x20x15 box when both cost $25 wastes void fill packaging material and increases carrier dimensional weight charges.

- **Developer Correction & Implementation**:
  - Designed a multi-tier sorting tuple for candidate box evaluation:
    ```python
    valid_boxes.sort(key=lambda b: (
        float(b.cost),                                                   # Primary: Lowest Cost
        float(b.internal_length * b.internal_width * b.internal_height), # Secondary: Smallest Volume (Void Fill Min)
        -float(b.max_weight)                                             # Tertiary: Higher Weight Margin
    ))
    ```

---

### Cycle 5: Expansion of Automated Test Coverage

- **Initial AI Output Received**:
  - AI provided 4 basic unit test cases (Laptop happy path, oversized product, overweight order, and quantity weight test).

- **Developer Intervention**:
  - Recognized that 4 tests provided inadequate coverage for 3D rotational mechanics, multi-product spatial failures, tie-breaking logic, invalid input validation, and API error codes.
  - Built a comprehensive **26-case unit test suite** in `shipping/tests.py` covering:
    - 3D spatial placement failure when volume fits (`test_multi_product_spatial_failure_despite_volume_fit`)
    - Quantity physical expansion (`test_quantity_affects_physical_packing_space`)
    - 6-DOF 3D orientation rotation (`test_3d_rotation_enables_fit`)
    - Volume & weight margin tie-breaking (`test_best_box_tie_breaking_volume`, `test_best_box_tie_breaking_weight_margin`)
    - Boundary exact matches (`test_boundary_exact_dimension_match`, `test_boundary_exact_weight_match`)
    - Invalid negative inputs & empty order handling
    - HTTP 200, 400, and 404 REST API view responses.

---

## 3. Summary of AI Mistakes & Developer Corrections

| AI Flaw / Oversight | Impact | Developer Correction / Refactoring |
| :--- | :--- | :--- |
| **1D Single-Item Dimension Checking** | Failed on multi-product orders where combined items don't fit 3D layout. | Replaced with **Extreme Points 3D Bin Packing Engine** with 6-DOF rotational search. |
| **Quantity Ignored in Spatial Packing** | Checked single product dimensions instead of expanded item quantities. | Built `build_3d_items_from_order_items()` to expand quantity $N$ into $N$ discrete 3D bounding boxes. |
| **Single-Criterion Box Sorting** | Picked arbitrary boxes when costs were identical. | Implemented multi-tier sorting: Cost (asc) $\rightarrow$ Volume (asc) $\rightarrow$ Weight Capacity (desc). |
| **Missing Exception Handling** | Invalid order IDs caused HTTP 500 Uncaught Exception crashes. | Added `try...except Order.DoesNotExist` and `ValueError` handlers returning HTTP 404 / 400. |
| **No Input Range Validation** | Zero or negative product dimensions caused invalid recommendations or errors. | Added strict input validation guards in `Item3D` throwing explicit `ValueError`. |
| **Minimal Test Coverage** | Only 4 tests provided; missing spatial failure and rotation edge cases. | Expanded test suite to **26 automated test cases** covering all domain edge cases. |

---

## 4. Empirical Debugging & Verification Log

### Test Execution Verification

```bash
./venv/bin/python manage.py test
```

#### Verification Terminal Output

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

All 26 test cases passed cleanly in 0.053 seconds.