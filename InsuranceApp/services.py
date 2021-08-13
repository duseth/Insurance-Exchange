from django.http import HttpRequest
from django.db.models import QuerySet
from .documents import ServiceDocument
from .models import Response
from typing import Dict, List, Optional
from elasticsearch_dsl.query import MultiMatch


def search_by_services(request: HttpRequest) -> QuerySet:
    """Service for receive all services by query and filter terms"""
    services = ServiceDocument.search()

    query: str = request.GET.get("query")
    if (query is not None) and (query != ""):
        services = services.query(
            MultiMatch(
                query=query,
                fields=[
                    "title",
                    "description",
                    "type.name",
                    "type.risks",
                    "validity.name",
                    "company.name",
                    "company.description",
                    "company.phone"
                ]
            )
        )

    filters: Dict[str, Optional[int]] = dict()
    for field in ["type", "validity", "company"]:
        parameter = request.GET.get(field)
        if parameter is not None:
            filters.update({f"{field}.id": int(parameter)})

    for field, term in filters.items():
        services = services.filter("term", **{field: term})

    return services.to_queryset()


def convert_response_to_notification(response: Response) -> Dict[str, str]:
    """Service for convert 'Response' object to 'dict' with client information"""
    return {
        "email": response.email,
        "phone": response.phone,
        "full_name": response.full_name,
        "company": response.company.email,
        "service": response.service.title,
        "response_date": response.response_date,
    }


def get_services_by_company(company_id: int) -> QuerySet:
    """Service for receive all services by 'company_id'"""
    return ServiceDocument.search().filter("term", **{"company.id": company_id}).to_queryset()
