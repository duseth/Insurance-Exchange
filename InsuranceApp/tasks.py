import os
import requests

from redis import StrictRedis
from django.conf import settings
from celery.signals import celeryd_after_setup
from django.template.loader import get_template
from InsuranceExchange.celery import celery_app


@celeryd_after_setup.connect
def configure_redis(*args, **kwargs) -> None:
    """Task method for Celery application, that forces Redis instance to take a snapshot of all the data."""
    redis = StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
    redis.save()


@celery_app.task
def send_response_notification(response: dict) -> None:
    """Task method for Celery application, that send response notification from client to 'company'"""
    body_template = get_template("mail.html")
    params = {
        "format": "json",
        "api_key": os.getenv("UNISENDER_KEY", "api_key"),
        "email": response["company"],
        "sender_name": os.getenv("COMPANY_NAME", "name"),
        "sender_email": os.getenv("COMPANY_EMAIL", "email"),
        "subject": f"You have new response for «{response['service']}»",
        "body": body_template.render(response),
        "list_id": 1
    }
    requests.post("https://api.unisender.com/ru/api/sendEmail", params=params)
