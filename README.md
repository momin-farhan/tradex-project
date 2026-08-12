# Tradexa Box Selection System

## Overview

The Tradexa Box Selection System is a Django-based application that recommends a suitable shipping box for an order based on product dimensions, product weight, box dimensions, maximum box weight, and box cost.

## Technology Stack

- Python
- Django
- SQLite
- Django REST-style JSON endpoint
- Django Test Framework

## Features

- Product management with dimensions and weight
- Shipping box management with dimensions, weight capacity, and cost
- Order and order-item management
- Automatic box recommendation
- Dimension-based box fitting
- Weight-capacity validation
- Cheapest suitable box selection
- JSON recommendation endpoint
- Automated tests for key scenarios

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/momin-farhan/tradex-project.git
cd tradex-project

python3 -m venv venv
source venv/bin/activate

py -m venv venv
.\venv\Scripts\Activate.ps1

python -m pip install django

python manage.py migrate

python manage.py createsuperuser

python manage.py runserver

http://127.0.0.1:8000/

http://127.0.0.1:8000/admin/

## Recommendation API

To get a box recommendation for an order, open:

```text
http://127.0.0.1:8000/orders/1/recommend/

{
    "order_id": 1,
    "recommended_box": "Medium Box",
    "cost": "30.00"
}

## Testing

Run the automated test suite with:

```bash
python manage.py test