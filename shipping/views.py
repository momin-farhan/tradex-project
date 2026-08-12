from django.http import JsonResponse

from .services import recommend_box


def recommend_box_view(request, order_id):
    box = recommend_box(order_id)

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