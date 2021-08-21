from django.http import HttpRequest
from django.db.models import QuerySet
from .documents import ServiceDocument
from .models import Response
from typing import Dict, List, Optional, Any
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

    sort: Optional[str] = request.GET.get("sort")
    services = services.sort(sort) if sort is not None else services.sort()

    return services[0:services.count()].to_queryset()


def get_services_by_company(company_id: int) -> QuerySet:
    """Service for receive all services by 'company_id'"""
    return ServiceDocument.search().filter("term", **{"company.id": company_id}).to_queryset()
