from django.http import HttpRequest
from django.db.models import QuerySet
from .documents import ServiceDocument
from .models import Response
from typing import Dict, List, Optional
from elasticsearch_dsl.query import MultiMatch


def search_by_services(request: HttpRequest) -> QuerySet:
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

    filters = __get_filters_from_request(request, "type", "validity", "company")
    for field, term in filters.items():
        services = services.filter("term", **{field: term})

    return services.to_queryset()


def get_services_by_company(company_id: int) -> QuerySet:
    return ServiceDocument.search().filter("term", **{"company.id": company_id}).to_queryset()


def convert_response_to_notification(response: Response) -> Dict[str, str]:
    return {
        "email": response.email,
        "phone": response.phone,
        "full_name": response.full_name,
        "company": response.company.email,
        "service": response.service.title,
        "response_date": response.response_date,
    }


def __get_filters_from_request(request: HttpRequest, *args: str) -> Dict[str, Optional[int]]:
    """Function that parse filter parameters from request"""
    filters: Dict[str, Optional[int]] = dict()
    for arg in args:
        parameter = request.GET.get(arg)
        if parameter is not None:
            filters.update({f"{arg}.id": int(parameter)})

    return filters
