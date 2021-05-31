from collections import OrderedDict

import graphene
from django.db import models
from graphene_django.utils import is_valid_django_model
from graphql import GraphQLError
from wagtail.core.models import Page

from .core import BaseQuery, BaseQueryOptions


class ReadQueryOptions(BaseQueryOptions):
    pass


class ReadQuery(BaseQuery):
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
        cls, _meta=None, model=None, type_name=None, **kwargs
    ):
        assert is_valid_django_model(model), (
            'You need to pass a valid Django Model in {}.Meta, received "{}".'
        ).format(cls.__name__, model)

        InputType = cls.load_input_type(type_name, model)
        OutputType = cls.load_output_type(model)

        if not _meta:
            _meta = ReadQueryOptions(cls)

        _meta.model = model
        _meta.OutputType = OutputType

        if issubclass(model, Page):
            arguments = OrderedDict(id=InputType(), slug=graphene.String())
        else:
            arguments = OrderedDict(id=InputType(required=True))

        setattr(cls, "Output", OutputType)

        super().__init_subclass_with_meta__(arguments=arguments, _meta=_meta, **kwargs)

    @classmethod
    def load_input_type(cls, type_name, model):
        InputType = graphene.ID

        return InputType

    @classmethod
    def resolve(cls, root, info, **kwargs):
        id = kwargs.get("id")
        # Slug for Wagtail Pages
        slug = kwargs.get("slug")

        cls.before_resolve(root, info, id)

        Model: models.Model = cls._meta.model

        if hasattr(Model, "before_read"):
            qs = Model.before_read(root, info, kwargs)
        else:
            qs = Model.objects

        if id:
            instance = qs.get(id=id)
        elif slug:
            instance = qs.get(slug=slug)
        else:
            raise GraphQLError("Id or slug must be provided")

        cls.after_resolve(root, info, instance)

        return instance
