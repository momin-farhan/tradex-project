# AI Development Transcript — Tradexa Box Selection System

## 1. Assignment Understanding

**User:** I need to complete the assignment from scratch and demonstrate it.

**Assistant:** We broke the work into small steps: Django setup, models, admin data, recommendation logic, API endpoint, tests, documentation, GitHub synchronization, and final demonstration.

## 2. Environment Setup

**User:** Django/virtual environment setup was giving PowerShell activation errors.

**Assistant:** We used the virtual environment and PowerShell execution-policy workaround, then verified Django with:

```bash
python -m django --version
```

Django was available and the project was opened in VS Code.

## 3. Django Project

The project structure was established around:

```text
tradex-project/
├── config/
├── shipping/
├── manage.py
└── venv/
```

The `shipping` application contains the business models and recommendation logic.

## 4. Models and Database

The project uses these core entities:

- `Box`
- `Product`
- `Order`
- `OrderItem`

Migrations were created and applied successfully:

```bash
python manage.py makemigrations
python manage.py migrate
```

Django system checks also passed.

## 5. Admin Data

Test data was created through Django Admin:

### Boxes

- Small Box
- Medium Box
- Large Box

### Products

- Laptop
- Book
- Monitor
- Keyboard

### Order

- Order #1
- Laptop × 1

## 6. Recommendation Logic

The business logic was separated into:

```text
shipping/services.py
```

The recommendation process:

1. Load the order.
2. Calculate total order weight using product weight × quantity.
3. Check each box's maximum weight.
4. Check whether product dimensions fit inside the box.
5. Sort suitable boxes by cost.
6. Return the cheapest suitable box.
7. Return `None` if no box is suitable.

The dimension check sorts product and box dimensions before comparison, allowing orientation/rotation of the product.

## 7. API Endpoint

The Django view was connected to:

```text
/orders/<order_id>/recommend/
```

For Order #1 the working response was:

```json
{
    "order_id": 1,
    "recommended_box": "Medium Box",
    "cost": "30.00"
}
```

### Why Medium Box?

Laptop:

```text
30 × 20 × 5
Weight = 2
```

Small Box:

```text
20 × 20 × 10
```

The laptop does not fit.

Medium Box:

```text
35 × 25 × 15
Max Weight = 10
Cost = 30
```

The laptop fits and the weight is within capacity.

Large Box also fits, but it costs more.

Therefore the cheapest suitable option is the Medium Box.

## 8. Automated Testing

The test suite was created in:

```text
shipping/tests.py
```

Four scenarios are covered:

1. Normal recommendation: Laptop → Medium Box.
2. Product too large: no suitable box.
3. Product too heavy: no suitable box.
4. Multiple quantity affects total weight.

Final test result:

```text
Found 4 test(s).
....
Ran 4 tests in 0.005s

OK
```

## 9. GitHub Workflow

The project was committed and pushed to GitHub throughout development.

The final repository contained:

```text
.gitignore
AI_USAGE.md
README.md
TEST_OUTPUT.md
config/
manage.py
shipping/
```

The virtual environment was excluded from the repository.

Final Git status:

```text
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

## 10. Documentation

The repository includes:

- `README.md` — project overview, stack, setup, API and testing instructions.
- `AI_USAGE.md` — AI assistance, prompts, and learning summary.
- `TEST_OUTPUT.md` — final automated test output.

## 11. Reasoning / Decision Summary

This section is a concise explanation of the development decisions. It is intentionally a summary rather than private chain-of-thought.

### Decision 1 — Separate business logic

The box-selection algorithm was placed in `shipping/services.py` instead of putting the logic directly in the view. This keeps the view small and makes the algorithm easier to test.

### Decision 2 — Check weight before dimensions

A box that cannot carry the total weight can immediately be rejected. This avoids unnecessary dimension processing for boxes that already fail a basic constraint.

### Decision 3 — Allow product rotation

Sorting dimensions before comparison provides a simple orientation-independent fit check.

### Decision 4 — Prefer the cheapest suitable box

Boxes are considered in ascending cost order. The first box that satisfies the constraints is therefore the cheapest suitable option.

### Decision 5 — Return `None` when nothing fits

This gives the application a clear failure state, which the API converts into a `404` response.

### Decision 6 — Test edge cases

Testing only the successful Laptop case would not be enough. Oversized products, excessive weight, and quantities were added to verify important failure and calculation paths.

## 12. Final Demonstration Flow

The recommended demonstration order is:

1. Explain the problem.
2. Show Django Admin.
3. Show the Laptop and box dimensions.
4. Show Order #1 containing Laptop × 1.
5. Explain the recommendation algorithm.
6. Open `/orders/1/recommend/`.
7. Show `Medium Box` and cost `30.00`.
8. Run `python manage.py test`.
9. Show all 4 tests passing.
10. Show the GitHub repository and documentation.

## 13. Important Technical Limitation

The current implementation is a simple rotation-aware dimension and weight heuristic. It is not a full 3D bin-packing optimization algorithm. This should be stated honestly if asked during evaluation.
