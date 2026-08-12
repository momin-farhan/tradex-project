# Tradexa Box Selection System

![Django CI](https://github.com/momin-farhan/tradex-project/actions/workflows/test.yml/badge.svg)

## Overview

The Tradexa Box Selection System is a Django-based web application that recommends the optimal shipping box for an e-commerce order based on:
1. Individual product dimensions (with 3D orientation/rotation support).
2. Combined product weight capacity versus box weight limits.
3. Total volumetric capacity of all items in an order.
4. Box cost optimization (selecting the cheapest suitable box).

## Technology Stack

- **Backend**: Python 3.12, Django 5.x / 6.x
- **Database**: SQLite3
- **API**: Django REST-style JSON API
- **Testing**: Django Test Framework (`django.test.TestCase`)
- **CI/CD**: GitHub Actions (`.github/workflows/test.yml`)

## Features

- **Product Management**: Models products with length, width, height, and weight.
- **Box Management**: Models internal length, width, height, maximum weight capacity, and cost.
- **Order Management**: Models orders and multi-item order quantities.
- **Rotation-Aware Dimension Fitting**: Sorts dimensions to determine 3D orientation fit.
- **Volumetric & Weight Capacity Constraints**: Evaluates total order weight and total volume.
- **Cost Minimization**: Automatically picks the cheapest suitable box among all valid candidates.
- **Defensive Error Handling**: Returns HTTP 404 with structured JSON for invalid orders or when no suitable box fits.
- **Automated Testing Suite**: 9 unit test cases covering all edge cases.

## Installation & Setup

### 1. Clone Repository & Create Virtual Environment

```bash
git clone https://github.com/momin-farhan/tradex-project.git
cd tradex-project

# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies & Run Migrations

```bash
pip install django
python manage.py migrate
```

### 3. Create Superuser (Optional) & Run Server

```bash
python manage.py createsuperuser
python manage.py runserver
```

The application will be accessible at:
- Web App / Admin: `http://127.0.0.1:8000/admin/`

## Recommendation API

### Request

```text
GET /orders/<order_id>/recommend/
```

### Example Successful Response (HTTP 200)

```json
{
    "order_id": 1,
    "recommended_box": "Medium Box",
    "cost": "30.00"
}
```

### Example Error Response (HTTP 404)

```json
{
    "error": "No suitable box found"
}
```

## Automated Testing

Run the full test suite with:

```bash
python manage.py test
```

Sample output:

```text
Found 9 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.........
----------------------------------------------------------------------
Ran 9 tests in 0.015s

OK
Destroying test database for alias 'default'...
```

## Submission Files

- `README.md` — Project overview and setup instructions.
- `AI_USAGE.md` — Complete AI usage log, prompt details, modifications, AI mistakes, and learnings.
- `AI_CHAT_TRANSCRIPT.md` — Step-by-step development process and decision log.
- `TEST_OUTPUT.md` — Full terminal output log of test executions.
- `.github/workflows/test.yml` — GitHub Actions CI pipeline configuration.