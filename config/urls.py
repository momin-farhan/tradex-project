"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from shipping.views import (
    index_view,
    recommend_box_view,
    api_orders_list,
    api_boxes_list,
    api_products_list,
    api_simulate_recommendation,
)

urlpatterns = [
    path("", index_view, name="index"),
    path("admin/", admin.site.urls),
    path(
        "orders/<int:order_id>/recommend/",
        recommend_box_view,
        name="recommend-box",
    ),
    path("api/orders/", api_orders_list, name="api-orders-list"),
    path("api/boxes/", api_boxes_list, name="api-boxes-list"),
    path("api/products/", api_products_list, name="api-products-list"),
    path("api/simulate/", api_simulate_recommendation, name="api-simulate"),
]