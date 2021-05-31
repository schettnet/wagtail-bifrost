from collections import OrderedDict

import graphene
from django.db import models
from graphene_django.utils import is_valid_django_model

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

        arguments = OrderedDict(id=InputType(required=True))

        setattr(cls, "Output", OutputType)

        super().__init_subclass_with_meta__(arguments=arguments, _meta=_meta, **kwargs)

    @classmethod
    def load_input_type(cls, type_name, model):
        InputType = graphene.ID

        return InputType

    @classmethod
    def resolve(cls, root, info, id):
        cls.before_resolve(root, info, id)

        Model: models.Model = cls._meta.model

        if hasattr(Model, "before_read"):
            qs = Model.before_read(root, info, input)
        else:
            qs = Model.objects

        instance = qs.get(id=id)

        cls.after_resolve(root, info, instance)

        return instance
