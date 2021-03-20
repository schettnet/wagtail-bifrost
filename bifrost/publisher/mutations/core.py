from typing import Type

import graphene
from django.db.models import Model
from graphene.types.objecttype import ObjectTypeOptions

from ..core import PublisherBase


class BaseMutationOptions(ObjectTypeOptions):
    model: Model = None
    OutputType: Type = None


class BaseMutation(graphene.Mutation, PublisherBase):
    class Meta:
        abstract = True

    @classmethod
    def before_mutate(cls, root, info, input):
        return None

    @classmethod
    def before_save(cls, root, info, input, obj):
        return None

    @classmethod
    def after_mutate(cls, root, info, obj, return_data):
        return None
