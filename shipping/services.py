from .models import Box, Order


def dimensions_fit(product, box):
    """
    Checks if a single product fits inside a box by comparing sorted dimensions
    (accounting for product rotation).
    """
    product_dimensions = sorted([
        float(product.length),
        float(product.width),
        float(product.height)
    ])

    box_dimensions = sorted([
        float(box.internal_length),
        float(box.internal_width),
        float(box.internal_height)
    ])

    return all(
        p_dim <= b_dim
        for p_dim, b_dim in zip(product_dimensions, box_dimensions)
    )


def recommend_box(order_id):
    """
    Recommends the cheapest suitable box for an order.
    Checks:
    1. Order existence and non-empty items.
    2. Weight capacity constraint (total weight <= max weight).
    3. Volume capacity constraint (total volume <= box volume).
    4. Individual item dimension constraint (each item fits inside box).
    """
    order = Order.objects.get(id=order_id)
    items = list(order.items.select_related("product"))

    if not items:
        return None

    total_weight = sum(
        item.product.weight * item.quantity
        for item in items
    )

    total_volume = sum(
        (item.product.length * item.product.width * item.product.height) * item.quantity
        for item in items
    )

    suitable_boxes = []

    for box in Box.objects.all().order_by("cost"):
        # Check max weight capacity
        if box.max_weight < total_weight:
            continue

        # Check total volume capacity
        box_volume = box.internal_length * box.internal_width * box.internal_height
        if box_volume < total_volume:
            continue

        # Check each item's individual dimensions fit
        if all(dimensions_fit(item.product, box) for item in items):
            suitable_boxes.append(box)

    return suitable_boxes[0] if suitable_boxes else None