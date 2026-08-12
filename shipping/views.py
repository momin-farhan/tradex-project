import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Order, Box, Product
from .services import recommend_box, dimensions_fit


def index_view(request):
    return render(request, "shipping/index.html")


def recommend_box_view(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        box = recommend_box(order_id)
    except Order.DoesNotExist:
        return JsonResponse(
            {
                "error": f"Order #{order_id} does not exist"
            },
            status=404
        )

    if box is None:
        return JsonResponse(
            {
                "error": "No suitable box found"
            },
            status=404
        )

    items = list(order.items.select_related("product"))
    total_weight = sum(item.product.weight * item.quantity for item in items)
    total_volume = sum((item.product.length * item.product.width * item.product.height) * item.quantity for item in items)
    box_volume = box.internal_length * box.internal_width * box.internal_height

    weight_utilization = round(float(total_weight / box.max_weight * 100), 1) if box.max_weight > 0 else 0
    volume_utilization = round(float(total_volume / box_volume * 100), 1) if box_volume > 0 else 0

    items_summary = [
        {
            "product_name": item.product.name,
            "quantity": item.quantity,
            "dimensions": f"{item.product.length}×{item.product.width}×{item.product.height} cm",
            "weight": str(item.product.weight),
        }
        for item in items
    ]

    return JsonResponse(
        {
            "order_id": order_id,
            "recommended_box": box.name,
            "cost": str(box.cost),
            "box_details": {
                "id": box.id,
                "name": box.name,
                "internal_length": str(box.internal_length),
                "internal_width": str(box.internal_width),
                "internal_height": str(box.internal_height),
                "max_weight": str(box.max_weight),
                "cost": str(box.cost),
                "volume": str(box_volume),
            },
            "metrics": {
                "total_weight": str(total_weight),
                "total_volume": str(total_volume),
                "weight_utilization_pct": weight_utilization,
                "volume_utilization_pct": volume_utilization,
            },
            "items": items_summary,
        }
    )


def api_orders_list(request):
    orders = Order.objects.prefetch_related("items__product").all().order_by("-created_at")
    result = []
    for order in orders:
        items = list(order.items.all())
        total_weight = sum(item.product.weight * item.quantity for item in items)
        total_volume = sum((item.product.length * item.product.width * item.product.height) * item.quantity for item in items)
        result.append({
            "id": order.id,
            "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "items_count": len(items),
            "total_weight": str(total_weight),
            "total_volume": str(total_volume),
            "items": [
                {
                    "product_id": item.product.id,
                    "product_name": item.product.name,
                    "quantity": item.quantity,
                    "length": str(item.product.length),
                    "width": str(item.product.width),
                    "height": str(item.product.height),
                    "weight": str(item.product.weight),
                }
                for item in items
            ]
        })
    return JsonResponse({"orders": result})


def api_boxes_list(request):
    boxes = Box.objects.all().order_by("cost")
    result = [
        {
            "id": b.id,
            "name": b.name,
            "internal_length": str(b.internal_length),
            "internal_width": str(b.internal_width),
            "internal_height": str(b.internal_height),
            "max_weight": str(b.max_weight),
            "cost": str(b.cost),
            "volume": str(b.internal_length * b.internal_width * b.internal_height),
        }
        for b in boxes
    ]
    return JsonResponse({"boxes": result})


def api_products_list(request):
    products = Product.objects.all().order_by("name")
    result = [
        {
            "id": p.id,
            "name": p.name,
            "length": str(p.length),
            "width": str(p.width),
            "height": str(p.height),
            "weight": str(p.weight),
            "volume": str(p.length * p.width * p.height),
        }
        for p in products
    ]
    return JsonResponse({"products": result})


@require_http_methods(["POST"])
def api_simulate_recommendation(request):
    try:
        data = json.loads(request.body)
        items_input = data.get("items", [])
    except Exception:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    if not items_input:
        return JsonResponse({"error": "No items provided"}, status=400)

    items_summary = []
    total_weight = 0
    total_volume = 0

    for item_data in items_input:
        product_id = item_data.get("product_id")
        quantity = int(item_data.get("quantity", 1))
        if quantity <= 0:
            continue
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue

        item_weight = product.weight * quantity
        item_vol = (product.length * product.width * product.height) * quantity
        total_weight += item_weight
        total_volume += item_vol

        items_summary.append({
            "product": product,
            "quantity": quantity,
        })

    if not items_summary:
        return JsonResponse({"error": "No valid products in order"}, status=400)

    suitable_boxes = []
    for box in Box.objects.all().order_by("cost"):
        if box.max_weight < total_weight:
            continue
        box_vol = box.internal_length * box.internal_width * box.internal_height
        if box_vol < total_volume:
            continue
        if all(dimensions_fit(item["product"], box) for item in items_summary):
            suitable_boxes.append(box)

    if not suitable_boxes:
        return JsonResponse({"error": "No suitable box found"}, status=404)

    recommended = suitable_boxes[0]
    box_vol = recommended.internal_length * recommended.internal_width * recommended.internal_height
    weight_util = round(float(total_weight / recommended.max_weight * 100), 1) if recommended.max_weight > 0 else 0
    volume_util = round(float(total_volume / box_vol * 100), 1) if box_vol > 0 else 0

    return JsonResponse({
        "recommended_box": recommended.name,
        "cost": str(recommended.cost),
        "box_details": {
            "id": recommended.id,
            "name": recommended.name,
            "internal_length": str(recommended.internal_length),
            "internal_width": str(recommended.internal_width),
            "internal_height": str(recommended.internal_height),
            "max_weight": str(recommended.max_weight),
            "cost": str(recommended.cost),
            "volume": str(box_vol),
        },
        "metrics": {
            "total_weight": str(total_weight),
            "total_volume": str(total_volume),
            "weight_utilization_pct": weight_util,
            "volume_utilization_pct": volume_util,
        }
    })