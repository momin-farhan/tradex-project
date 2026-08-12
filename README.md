# Tradexa Box Selection System

![Django CI](https://github.com/momin-farhan/tradex-project/actions/workflows/test.yml/badge.svg)

## Overview

The **Tradexa Box Selection System** is an e-commerce shipping optimization engine built with Django. It determines the optimal shipping box for multi-product, multi-quantity customer orders using a **3D Bin Packing Engine (Extreme Points Algorithm)** that enforces 3D spatial layout constraints, 6-DOF rotational orientation, weight limits, and multi-tier cost/volume optimization.

---

## 📐 Business Assumptions & Tradeoffs

### 1. Definition of the "Best" Box
In e-commerce fulfillment, selecting the "best" shipping box involves balancing direct packaging costs against carrier shipping fees and damage risks. The system defines the optimal box using a strict multi-tier hierarchy:

1. **Feasibility (Hard Constraints)**:
   - **3D Physical Bin Packing**: All items in the order (expanded by quantity) must physically fit inside the box's internal 3D bounding box simultaneously without 3D spatial overlap.
   - **Weight Capacity**: Combined order weight ($\sum \text{weight}_i \times \text{qty}_i$) must not exceed the box's maximum weight limit (`max_weight`).
   - **Input Integrity**: All dimensions and weight values must be strictly positive ($>0$).

2. **Primary Optimization Metric — Lowest Direct Unit Cost**:
   - The algorithm primary goal is to minimize direct packaging material expense (`Box.cost`).

3. **Secondary Optimization Metric — Volume Utilization & Void Fill Minimization (Tie-Breaker)**:
   - If two candidate boxes have identical costs, the system selects the box with the **smallest internal volume**.
   - *Rationale*: Smaller boxes require less void fill material (bubble wrap, air pillows, kraft paper), reduce package movement during transit (lowering item breakage rates), and minimize carrier **Dimensional Weight (Dim Weight)** freight charges.

4. **Tertiary Optimization Metric — Weight Reserve Safety Margin (Tie-Breaker)**:
   - If cost and internal volume are identical, the system selects the box with the **highest `max_weight` capacity** to provide a structural safety margin during transport.

---

### 2. 3D Packing Algorithm & Trade-offs

#### Algorithm Choice: Extreme Points 3D Bin Packing
3D Bin Packing (3D-BPP) is an **NP-hard combinatorial optimization problem**. The system implements an **Extreme Points (EP) Bin Packing Algorithm** with 6-Degrees-of-Freedom (6-DOF) rotational search and multi-heuristic item sorting (volume, max dimension, footprint area, height).

#### Why Extreme Points vs. Simple Volume/1D Checks or Exact ILP?
- **Simple 1D / Volume Checking (Previous Flaw)**: Checking if total order volume $\le$ box volume or checking items individually fails whenever item geometry prevents packing (e.g., two tall plates that fit volume but exceed height when stacked).
- **Exact Integer Linear Programming (ILP)**: Solving 3D-BPP to mathematical optimality via branch-and-bound guarantees optimal packing but takes seconds to minutes per request—unacceptable for live checkout APIs.
- **Extreme Points Heuristic**: Generates potential 3D placement coordinates $(x,y,z)$ at the boundaries of placed items. It evaluates 6-DOF rotations in milliseconds ($<5\text{ms}$) while guaranteeing exact 3D non-overlapping spatial fitting.

---

### 3. Real-World Logistics & Warehouse Assumptions

1. **Full 6-DOF Rotational Freedom**:
   - The algorithm assumes items can be rotated freely around all 3 spatial axes (6 orientations).
   - *Future Extension*: Certain fragile goods or liquids require "This Side Up" orientation restrictions. The `Item3D` engine supports restricting allowed rotation sets per item class.

2. **Quantity Expansion**:
   - An order item with `quantity = N` is expanded into $N$ individual 3D bounding boxes. Each instance occupies physical space inside the box.

3. **Exact Bounding Box vs. Cushioning Clearance Buffer**:
   - Dimensions represent internal box boundaries. In production warehouse environments, a configurable clearance margin (e.g., 1.5 cm buffer on all sides) can be subtracted from internal dimensions to account for protective bubble wrapping.

---

## 🛠️ System Architecture

```text
tradex-project/
├── shipping/
│   ├── models.py          # Product, Box, Order, OrderItem models
│   ├── services.py        # Item3D, Extreme Points 3D Packing Engine, recommend_box logic
│   ├── views.py           # REST APIs, Recommender, Simulator endpoints
│   ├── tests.py           # Comprehensive 26-case test suite
│   ├── templates/         # Interactive Django Admin & Web Dashboard
│   └── static/            # CSS / Vanilla JavaScript UI
├── AI_USAGE.md            # Detailed AI prompt log, corrections, and debugging transcript
├── AI_CHAT_TRANSCRIPT.md   # Step-by-step decision record
└── TEST_OUTPUT.md         # Full automated test log
```

---

## 🚀 Installation & Setup

### 1. Clone Repository & Environment Setup

```bash
git clone https://github.com/momin-farhan/tradex-project.git
cd tradex-project

# Create & activate virtual environment
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies & Run Migrations

```bash
pip install django
python manage.py migrate
```

### 3. Run Server & Access Web Dashboard

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` to access the interactive web dashboard.

---

## 📡 API Reference

### 1. Recommendation Endpoint

```text
GET /orders/<order_id>/recommend/
```

#### Example Successful Response (HTTP 200)

```json
{
    "order_id": 1,
    "recommended_box": "Medium Box",
    "cost": "30.00",
    "box_details": {
        "id": 2,
        "name": "Medium Box",
        "internal_length": "35.00",
        "internal_width": "25.00",
        "internal_height": "15.00",
        "max_weight": "10.00",
        "cost": "30.00",
        "volume": "13125.0"
    },
    "metrics": {
        "total_weight": "2.0",
        "total_volume": "3000.0",
        "weight_utilization_pct": 20.0,
        "volume_utilization_pct": 22.9
    },
    "items": [
        {
            "product_name": "Laptop",
            "quantity": 1,
            "dimensions": "30.00×20.00×5.00 cm",
            "weight": "2.00"
        }
    ]
}
```

#### Example Error Responses

- **Order Not Found (HTTP 404)**:
  ```json
  { "error": "Order #99999 does not exist" }
  ```
- **No Suitable Box Fits (HTTP 404)**:
  ```json
  { "error": "No suitable box found" }
  ```

---

### 2. Live Order Simulation Endpoint

```text
POST /api/simulate/
Content-Type: application/json

{
    "items": [
        { "product_id": 1, "quantity": 2 },
        { "product_id": 3, "quantity": 1 }
    ]
}
```

---

## 🧪 Automated Testing

Execute the test suite with:

```bash
python manage.py test
```

### Sample Output

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