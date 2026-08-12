from decimal import Decimal
from .models import Box, Order, Product


class Item3D:
    """
    Represents a single 3D item instance to be physically packed into a shipping box.
    Enforces positive dimensions and weight validation.
    """
    def __init__(self, length, width, height, weight, name="Item"):
        self.length = float(length)
        self.width = float(width)
        self.height = float(height)
        self.weight = float(weight)
        self.name = name

        if self.length <= 0 or self.width <= 0 or self.height <= 0:
            raise ValueError(f"Invalid product dimensions for '{name}': {length}x{width}x{height}. Dimensions must be positive.")
        if self.weight < 0:
            raise ValueError(f"Invalid product weight for '{name}': {weight}. Weight cannot be negative.")

    @property
    def volume(self):
        return self.length * self.width * self.height

    def get_rotations(self):
        """
        Returns all unique 3D rotational orientations (dx, dy, dz) for this item.
        Supports 6 degrees of freedom (6-DOF) spatial rotation.
        """
        l, w, h = self.length, self.width, self.height
        rotations = {
            (l, w, h), (l, h, w),
            (w, l, h), (w, h, l),
            (h, l, w), (h, w, l)
        }
        return list(rotations)


def boxes_overlap(box1, box2):
    """
    Checks if two 3D boxes overlap in space.
    box format: (x, y, z, dx, dy, dz)
    """
    x1, y1, z1, dx1, dy1, dz1 = box1
    x2, y2, z2, dx2, dy2, dz2 = box2

    return (
        max(x1, x2) < min(x1 + dx1, x2 + dx2) and
        max(y1, y2) < min(y1 + dy1, y2 + dy2) and
        max(z1, z2) < min(z1 + dz1, z2 + dz2)
    )


def can_pack_items_3d(items, box_length, box_width, box_height):
    """
    Determines whether a list of Item3D objects can physically fit simultaneously
    inside a container box of dimensions (box_length, box_width, box_height).

    Uses Extreme Points 3D Bin Packing with 6-DOF rotation search and multiple item sorting strategies.
    """
    if not items:
        return True

    box_l, box_w, box_h = float(box_length), float(box_width), float(box_height)
    if box_l <= 0 or box_w <= 0 or box_h <= 0:
        return False

    # 1. Fast-fail: Combined volume check
    total_item_vol = sum(item.volume for item in items)
    box_vol = box_l * box_w * box_h
    if total_item_vol > box_vol:
        return False

    # 2. Fast-fail: Individual item dimension fit check under rotation
    box_sorted = sorted([box_l, box_w, box_h])
    for item in items:
        item_sorted = sorted([item.length, item.width, item.height])
        if any(i_dim > b_dim for i_dim, b_dim in zip(item_sorted, box_sorted)):
            return False

    # 3. 3D Spatial Packing Simulation using Extreme Points with heuristic sorting
    sorting_strategies = [
        lambda it: it.volume,                            # Volume descending
        lambda it: max(it.length, it.width, it.height),  # Max dimension descending
        lambda it: it.length * it.width,                 # Footprint area descending
        lambda it: it.height,                            # Height descending
    ]

    for strategy in sorting_strategies:
        sorted_items = sorted(items, key=strategy, reverse=True)
        if _try_pack_extreme_points(sorted_items, box_l, box_w, box_h):
            return True

    return False


def _try_pack_extreme_points(items, box_l, box_w, box_h):
    """
    Attempts to place items into the box using Extreme Points coordinate placement.
    """
    placed_boxes = []  # List of tuples: (x, y, z, dx, dy, dz)
    extreme_points = [(0.0, 0.0, 0.0)]

    for item in items:
        placed = False
        # Prioritize lower z (bottom first), lower y, lower x
        extreme_points.sort(key=lambda p: (p[2], p[1], p[0]))

        for ep in list(extreme_points):
            x, y, z = ep

            for dx, dy, dz in item.get_rotations():
                # Verify container boundaries
                if x + dx > box_l + 1e-6 or y + dy > box_w + 1e-6 or z + dz > box_h + 1e-6:
                    continue

                candidate_box = (x, y, z, dx, dy, dz)

                # Check 3D overlap against already placed items
                if any(boxes_overlap(candidate_box, pb) for pb in placed_boxes):
                    continue

                # Successful placement!
                placed_boxes.append(candidate_box)
                placed = True

                # Generate new Extreme Points at boundaries of placed box
                new_eps = [
                    (x + dx, y, z),
                    (x, y + dy, z),
                    (x, y, z + dz),
                ]

                # Filter and add valid extreme points
                for nep in new_eps:
                    nx, ny, nz = nep
                    if nx <= box_l and ny <= box_w and nz <= box_h:
                        if not any(
                            pb[0] <= nx < pb[0] + pb[3] and
                            pb[1] <= ny < pb[1] + pb[4] and
                            pb[2] <= nz < pb[2] + pb[5]
                            for pb in placed_boxes
                        ):
                            if nep not in extreme_points:
                                extreme_points.append(nep)
                break

            if placed:
                break

        if not placed:
            return False

    return True


def dimensions_fit(product, box):
    """
    Legacy helper: checks if a single product individually fits inside a box
    under 3D rotation. (Note: For full order packing, use recommend_box or can_pack_items_3d).
    """
    try:
        item = Item3D(product.length, product.width, product.height, product.weight, name=product.name)
        box_l, box_w, box_h = float(box.internal_length), float(box.internal_width), float(box.internal_height)
        box_sorted = sorted([box_l, box_w, box_h])
        item_sorted = sorted([item.length, item.width, item.height])
        return all(i_dim <= b_dim for i_dim, b_dim in zip(item_sorted, box_sorted))
    except (ValueError, AttributeError):
        return False


def build_3d_items_from_order_items(order_items):
    """
    Converts database OrderItem models (with quantity) into an expanded list of Item3D objects.
    Expands quantity N into N discrete 3D items.
    """
    items_3d = []
    for item in order_items:
        if item.quantity <= 0:
            continue
        product = item.product
        if not product:
            continue
        for _ in range(item.quantity):
            items_3d.append(
                Item3D(
                    length=product.length,
                    width=product.width,
                    height=product.height,
                    weight=product.weight,
                    name=product.name
                )
            )
    return items_3d


def recommend_box(order_id):
    """
    Recommends the optimal (cheapest suitable) shipping box for a database Order.

    Algorithm & Criteria:
    1. Fetches Order and associated items.
    2. Returns None for empty orders or orders without valid items.
    3. Expands order items into individual 3D physical item instances based on quantity.
    4. Evaluates boxes ordered by:
       a) Primary: Lowest packaging cost (`cost`).
       b) Secondary: Smallest internal volume (tie-breaker for space utilization/void fill).
       c) Tertiary: Higher weight capacity (tie-breaker for safety margin).
    5. Validates total order weight vs box max_weight capacity.
    6. Validates 3D physical layout packing using Extreme Points algorithm with 6-DOF rotations.
    """
    order = Order.objects.get(id=order_id)
    items = list(order.items.select_related("product").all())

    if not items:
        return None

    items_3d = build_3d_items_from_order_items(items)

    if not items_3d:
        return None

    total_weight = float(sum(item.weight for item in items_3d))

    # Query boxes ordered by cost ascending, volume ascending, max_weight descending
    all_boxes = list(Box.objects.all())
    valid_boxes = [b for b in all_boxes if float(b.internal_length) > 0 and float(b.internal_width) > 0 and float(b.internal_height) > 0 and float(b.max_weight) > 0]

    # Sort candidates by cost (asc), internal volume (asc), max_weight (desc)
    valid_boxes.sort(key=lambda b: (
        float(b.cost),
        float(b.internal_length * b.internal_width * b.internal_height),
        -float(b.max_weight)
    ))

    for box in valid_boxes:
        # Check weight capacity constraint
        if float(box.max_weight) < total_weight:
            continue

        # Check 3D physical packing fit constraint (including quantity and rotations)
        if can_pack_items_3d(items_3d, box.internal_length, box.internal_width, box.internal_height):
            return box

    return None