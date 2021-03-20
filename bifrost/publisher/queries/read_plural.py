from collections import OrderedDict

from django.db import models
from graphene_django.utils import is_valid_django_model

from ..options import PublisherOptions
from .core import BaseQuery, BaseQueryOptions


class ReadPluralQueryOptions(BaseQueryOptions):
    pass


class ReadPluralQuery(BaseQuery):
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
        OutputType = cls.load_output_type(model, is_list=True)

        if not _meta:
            _meta = ReadPluralQueryOptions(cls)

        _meta.model = model
        _meta.OutputType = OutputType

        arguments = OrderedDict(input=InputType(required=True))

        setattr(cls, "Output", OutputType)

        super().__init_subclass_with_meta__(arguments=arguments, _meta=_meta, **kwargs)

    @classmethod
    def load_input_type(cls, type_name, model):
        selector = PublisherOptions.Selector.READ_FILTER
        InputType = super().load_input_type(type_name, model, selector)

        # > Validate meta fields
        assert (
            len(InputType._meta.fields) > 0
        ), f"""The model `{model.__name__}` must have `graphql_fields`. At least one requires `PublisherOptions({selector}=True)`.
            This required when registering a model using `bifrost.publisher.actions.register_{selector}()`!
            """

        return InputType

    @classmethod
    def resolve(cls, root, info, input):
        Model: models.Model = cls._meta.model
        # OutputType = cls._meta.OutputType
        arguments: dict = input

        # else:
        #   """
        #   The argument `id` is a required
        #   """
        #     pass
        qs = Model.objects.filter(**arguments)

        return qs
