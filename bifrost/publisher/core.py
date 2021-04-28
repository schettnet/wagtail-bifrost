from typing import OrderedDict

import graphene
from graphene.types.scalars import Scalar
from graphene.types.utils import yank_fields_from_attrs

from bifrost.api.registry import registry
from bifrost.api.types.streamfield import StreamFieldInterface


class PublisherBase:
    @classmethod
    def load_input_type(cls, type_name, model, selector: str):
        graphql_fields = getattr(model, "graphql_fields", None)

        assert (
            graphql_fields
        ), f"The model `{model.__name__}` of `{cls.__name__}` must contain `graphql_fields`!"

        class InputType(graphene.InputObjectType):
            class Meta:
                name = type_name or f"{selector.capitalize()}{model.__name__}Input"

        for field in graphql_fields:

            collection_field = None
            if callable(field):
                field = field()

            if type(field) is tuple:
                field, outer_field = field
                field = field()

                # collection_field = outer_field
                collection_field = graphene.List

            if getattr(field.publisher_options, selector, False):
                if field.is_relation:
                    abc = graphene.ID(required=field.required)
                    if collection_field:
                        abc = graphene.List(graphene.ID, required=field.required)

                    setattr(InputType, f"{field.field_name}", abc)
                else:
                    field_type = field.field_type

                    if callable(field_type):
                        field_type = field_type()

                        if callable(field_type):
                            field_type = field_type()

                    if getattr(field_type, "_of_type", False):
                        field_type = field_type._of_type
                        if issubclass(field_type, StreamFieldInterface):
                            print(field_type.__dict__)
                            field_type = graphene.JSONString()
                        else:
                            field_type = field_type()

                    if isinstance(field_type, Scalar):
                        if collection_field:
                            setattr(
                                InputType,
                                field.field_name,
                                collection_field(lambda: field_type),
                            )
                        else:
                            setattr(InputType, field.field_name, field_type)

        # > Update meta fields
        fields = OrderedDict()
        for base in reversed(InputType.__mro__):
            fields.update(
                yank_fields_from_attrs(base.__dict__, _as=graphene.InputField)
            )

        InputType._meta.fields.update(fields)

        return InputType

    @classmethod
    def load_output_type(cls, model, is_list=False):
        OutputType = registry.models.get(model)

        if is_list:
            OutputType = graphene.List(OutputType)

        return OutputType
