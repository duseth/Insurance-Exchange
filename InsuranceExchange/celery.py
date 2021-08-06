"""
Celery config for InsuranceExchange project.

It exposes the Celery callable as a module-level variable named ``celery_app``.
"""

import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "InsuranceExchange.settings")

celery_app = Celery("InsuranceExchange")
celery_app.config_from_object("django.conf:settings", namespace="CELERY")

celery_app.autodiscover_tasks()
