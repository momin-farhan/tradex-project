from .models import Box, Order


def dimensions_fit(product, box):
    product_dimensions = sorted([
        product.length,
        product.width,
        product.height
    ])

    box_dimensions = sorted([
        box.internal_length,
        box.internal_width,
        box.internal_height
    ])

    return all(
        product_dimension <= box_dimension
        for product_dimension, box_dimension
        in zip(product_dimensions, box_dimensions)
    )


def recommend_box(order_id):
    order = Order.objects.get(id=order_id)

    items = order.items.select_related("product")

    total_weight = sum(
        item.product.weight * item.quantity
        for item in items
    )

    suitable_boxes = []

    for box in Box.objects.all().order_by("cost"):
        if box.max_weight < total_weight:
            continue

        if all(
            dimensions_fit(item.product, box)
            for item in items
        ):
            suitable_boxes.append(box)

    return suitable_boxes[0] if suitable_boxes else None