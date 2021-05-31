from collections import OrderedDict

import graphene
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from graphene.types.utils import yank_fields_from_attrs
from graphene_django.utils import is_valid_django_model
from graphql import GraphQLError
from wagtail.core.models import Page

from ..options import PublisherOptions
from .core import BaseMutation, BaseMutationOptions


class CreateMutationOptions(BaseMutationOptions):
    pass


class CreateMutation(BaseMutation):
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
            _meta = CreateMutationOptions(cls)

        _meta.model = model
        _meta.OutputType = OutputType

        arguments = OrderedDict(input=InputType(required=True))

        setattr(cls, "Output", _meta.OutputType)

        super().__init_subclass_with_meta__(arguments=arguments, _meta=_meta, **kwargs)

    @classmethod
    def load_input_type(cls, type_name, model):
        selector = PublisherOptions.Selector.CREATE
        InputType = super().load_input_type(type_name, model, selector)

        # > Add custom fields for some model types
        if issubclass(model, Page):
            required_fields = ["slug", "title"]

            for field in required_fields:
                assert getattr(
                    InputType, field, False
                ), f"""The model `{model.__name__}` must have `{field}` in `graphql_fields` with `PublisherOptions({selector}=True)`.
                    This is required when registering a Page model using `bifrost.publisher.actions.register_{selector}()`!
                    """

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
    def mutate(cls, root, info, input):

        cls.before_resolve(root, info, input)

        Model: models.Model = cls._meta.model
        cls._meta.OutputType

        with transaction.atomic():
            instance = Model()

            if not hasattr(instance, "before_create"):
                arguments = input
            else:
                instance, arguments = instance.before_create(root, info, input)

            for related_field in Model._meta.get_fields():
                if related_field.is_relation:
                    if related_field.name in arguments:
                        values = arguments[related_field.name]

                        if isinstance(values, list):
                            related_set = getattr(instance, f"{related_field.name}")
                            related_model = related_field.related_model
                            for idx in values:
                                try:
                                    related_set.add(related_model.objects.get(id=idx))
                                except related_model.DoesNotExist:
                                    pass

                        else:
                            setattr(instance, f"{related_field.name}_id", values)

                        # Remove field name form arguments because they are already added above
                        arguments.pop(related_field.name)

            for field_name, field_value in arguments.items():
                setattr(instance, field_name, field_value)

            if issubclass(Model, Page):
                root = None
                parent_page_id = arguments.get("parent_page")

                if not parent_page_id:
                    root = Page.get_first_root_node()
                else:
                    try:
                        root = Page.objects.get(id=parent_page_id)
                    except Page.DoesNotExist:
                        raise GraphQLError("Parent page does not exists")

                instance.content_type = ContentType.objects.get_for_model(Model)

                root.add_child(instance=instance)

            cls.before_save(root, info, input, instance)

            instance.save()

        cls.after_resolve(root, info, instance)

        return instance
