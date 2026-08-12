from django.http import JsonResponse
from .models import Order
from .services import recommend_box


def recommend_box_view(request, order_id):
    try:
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

    return JsonResponse(
        {
            "order_id": order_id,
            "recommended_box": box.name,
            "cost": str(box.cost),
        }
    )