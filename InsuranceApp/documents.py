from .models import Service, InsuranceType, ValidityType, Company

from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry


@registry.register_document
class ServiceDocument(Document):
    type = fields.ObjectField(properties={
        "id": fields.IntegerField(),
        "name": fields.TextField(),
        "risks": fields.TextField()
    })
    validity = fields.ObjectField(properties={
        "id": fields.IntegerField(),
        "name": fields.TextField(),
        "time": fields.IntegerField()
    })
    company = fields.ObjectField(properties={
        "id": fields.IntegerField(),
        "name": fields.TextField(),
        "description": fields.TextField(),
        "phone": fields.TextField()
    })

    class Index:
        name = "service"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }

    class Django:
        model = Service
        fields = ["title", "description", "coverage_amount", "price"]
        related_models = [InsuranceType, ValidityType, Company]

    def get_queryset(self):
        return super(ServiceDocument, self).get_queryset().select_related("type", "validity", "company")

    def get_instances_from_related(self, related_instance):
        return related_instance.service_set.all()
