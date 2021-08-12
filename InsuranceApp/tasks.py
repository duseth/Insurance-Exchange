import os
import requests

from redis import StrictRedis
from django.conf import settings
from celery.signals import celeryd_after_setup
from InsuranceExchange.celery import celery_app


@celeryd_after_setup.connect
def configure_redis(*args, **kwargs) -> None:
    """Task method for Celery application, that forces Redis instance to take a snapshot of all the data."""
    redis = StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
    redis.save()


@celery_app.task
def send_response_notification(response: dict) -> None:
    """Task method for Celery application, that send response notification from client to 'company'"""
    params = {
        "format": "json",
        "api_key": os.getenv("UNISENDER_KEY", "api_key"),
        "email": response["company"],
        "sender_name": os.getenv("COMPANY_NAME", "name"),
        "sender_email": os.getenv("COMPANY_EMAIL", "email"),
        "subject": f"You have new response for «{response['service']}»",
        "body": f"<h4>You have new response for «{response['service']}»</h4>"
                f"<table><tbody>"
                f"<tr><td>Full name</td><td>{response['full_name']}</td></tr>"
                f"<tr><td>Email</td><td>{response['email']}</td></tr>"
                f"<tr><td>Phone</td><td>{response['phone']}</td></tr>"
                f"<tr><td>Date</td><td>{response['response_date']}</td></tr>"
                f"</tbody></table>",
        "list_id": 1
    }
    requests.post("https://api.unisender.com/ru/api/sendEmail", params=params)
