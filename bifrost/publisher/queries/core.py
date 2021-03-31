from typing import Type

from django.db.models import Model
from graphene.types.objecttype import ObjectTypeOptions

from bifrost.api.types import Query

from ..core import PublisherBase


class BaseQueryOptions(ObjectTypeOptions):
    model: Model = None
    OutputType: Type = None


class BaseQuery(Query, PublisherBase):
    class Meta:
        abstract = True

    @classmethod
    def before_resolve(cls, root, info, input):
        return None

    @classmethod
    def after_resolve(cls, root, info, return_data):
        return None
