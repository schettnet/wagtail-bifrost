from collections import OrderedDict

import graphene
from django.db import models, transaction
from graphene.types.utils import yank_fields_from_attrs
from graphene_django.utils import is_valid_django_model
from graphql import GraphQLError
from wagtail.core.models import Page

from ..options import PublisherOptions
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

        if issubclass(model, Page):
            arguments = OrderedDict(
                input=InputType(required=True), id=graphene.ID(), slug=graphene.String()
            )
        else:
            arguments = OrderedDict(
                input=InputType(required=True), id=graphene.ID(required=True)
            )

        setattr(cls, "Output", OutputType)

        super().__init_subclass_with_meta__(arguments=arguments, _meta=_meta, **kwargs)

    @classmethod
    def load_input_type(cls, type_name, model):
        selector = PublisherOptions.Selector.UPDATE
        InputType = super().load_input_type(type_name, model, selector)

        # Add parent page field
        setattr(InputType, "parent_page", graphene.ID())

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
    def mutate(cls, root, info, input, **kwargs):
        Model: models.Model = cls._meta.model
        # OutputType = cls._meta.OutputType
        arguments: dict = input
        instance = None

        id = kwargs.get("id")
        slug = kwargs.get("slug")

        cls.before_resolve(root, info, input)

        with transaction.atomic():
            if id:
                instance = Model.objects.get(id=id)
            elif slug:
                instance = Model.objects.get(slug=slug)
            else:
                raise GraphQLError("Id or slug must be provided")

            for field in Model._meta.get_fields():
                field_name = field.name
                try:
                    value = arguments[field_name]

                    if field.is_relation:
                        setattr(instance, f"{field_name}_id", value)
                    else:
                        setattr(instance, field_name, value)

                    arguments.pop(field_name)
                except:
                    pass

            # Save before handeling the parent page move to ensure correct path handling
            cls.before_save(root, info, input, instance)

            instance.save()

            if issubclass(Model, Page):
                parent_page_id = arguments.get("parent_page")

                if parent_page_id:
                    try:
                        parent = Page.objects.get(id=parent_page_id)
                        instance = instance.specific
                        instance.move(parent, pos="last-child")
                    except Page.DoesNotExist:
                        raise GraphQLError("Parent page does not exists")

                arguments.pop("parent_page", None)

            instance.refresh_from_db()

        return instance
