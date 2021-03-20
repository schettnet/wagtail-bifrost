from collections import OrderedDict

import graphene
from django.db import models, transaction
from graphene.types.utils import yank_fields_from_attrs
from graphene_django.utils import is_valid_django_model
from graphql import GraphQLError

from ..options import PublisherOptions
from .core import BaseMutation, BaseMutationOptions


class DeleteMutationOptions(BaseMutationOptions):
    pass


class DeleteMutation(BaseMutation):
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
        OutputType = graphene.Int

        if not _meta:
            _meta = DeleteMutationOptions(cls)

        _meta.model = model
        _meta.OutputType = OutputType

        arguments = OrderedDict(input=InputType(required=True))

        setattr(cls, "Output", OutputType)

        super().__init_subclass_with_meta__(arguments=arguments, _meta=_meta, **kwargs)

    @classmethod
    def load_input_type(cls, type_name, model):
        selector = PublisherOptions.Selector.DELETE
        InputType = super().load_input_type(type_name, model, selector)

        # > Add custom fields for delete
        setattr(InputType, "id", graphene.ID())

        fields = OrderedDict()
        for base in reversed(InputType.__mro__):
            fields.update(
                yank_fields_from_attrs(base.__dict__, _as=graphene.InputField)
            )

        InputType._meta.fields.update(fields)

        # > Validate meta fields
        assert (
            len(InputType._meta.fields) > 0
        ), f"""The model `{model.__name__}` must have `graphql_fields`. At least one requires `PublisherOptions({selector}=True)`.
            This required when registering a model using `bifrost.publisher.actions.register_{selector}()`!
            """

        return InputType

    @classmethod
    def mutate(cls, root, info, input):
        Model: models.Model = cls._meta.model
        # OutputType = cls._meta.OutputType
        arguments: dict = input

        with transaction.atomic():
            if arguments.get("id") and len(arguments) > 1:
                raise GraphQLError("Cannot use multiple arguments when `id` is used!")

            """
            Filter for objects and delete them.
            
            This way of determining the total deletions `deletion_count, _ = Model.objects.filter(**arguments).delete()`
            is not used because it not always return `Tuple[int, Dict[str, int]]` but also `None` when deletion succeed.
            """
            qs = Model.objects.filter(**arguments)
            deletion_count = qs.count()
            qs.delete()

            return deletion_count
