from collections import OrderedDict

import graphene
from django.db import models, transaction
from graphene_django.utils import is_valid_django_model

from ..options import PublisherOptions
from ..utils import get_related_fields
from .core import BaseMutation, BaseMutationOptions


class UpdateMutationOptions(BaseMutationOptions):
    pass


class UpdateMutation(BaseMutation):
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
            _meta = UpdateMutationOptions(cls)

        _meta.model = model
        _meta.OutputType = OutputType

        arguments = OrderedDict(
            input=InputType(required=True), id=graphene.ID(required=True)
        )

        setattr(cls, "Output", OutputType)

        super().__init_subclass_with_meta__(arguments=arguments, _meta=_meta, **kwargs)

    @classmethod
    def load_input_type(cls, type_name, model):
        selector = PublisherOptions.Selector.UPDATE
        InputType = super().load_input_type(type_name, model, selector)

        # > Validate meta fields
        assert (
            len(InputType._meta.fields) > 0
        ), f"""The model `{model.__name__}` must have `graphql_fields`. At least one requires `PublisherOptions({selector}=True)`.
            This required when registering a model using `bifrost.publisher.actions.register_{selector}()`!
            """

        return InputType

    @classmethod
    def mutate(cls, root, info, id, input):
        cls.before_resolve(root, info, input)

        Model: models.Model = cls._meta.model
        # OutputType = cls._meta.OutputType
        arguments: dict = input

        instance = None

        with transaction.atomic():
            instance = Model.objects.get(id=id)

            for related_field in get_related_fields(Model):

                if related_field.name in arguments:
                    values = arguments[related_field.name]

                    setattr(instance, f"{related_field.name}_id", values)

                    # Remove field name form arguments because they are already added above
                    arguments.pop(related_field.name)

            cls.before_save(root, info, input, instance)

            instance.save()

            qs = Model.objects.filter(id=id)
            qs.update(**arguments)

            instance.refresh_from_db()

        return instance
