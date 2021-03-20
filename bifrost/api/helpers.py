import inspect
from types import MethodType

import graphene
from django.utils.translation import ugettext_lazy
from wagtail.core.models import Page

from .registry import registry
from .types.streamfield import StreamFieldInterface

streamfield_types = []


def register_streamfield_block(cls):
    base_block = None
    for block_class in inspect.getmro(cls):
        if block_class in registry.streamfield_blocks:
            base_block = registry.streamfield_blocks[block_class]

    streamfield_types.append(
        {
            "cls": cls,
            "type_prefix": "",
            "interface": StreamFieldInterface,
            "base_type": base_block,
        }
    )

    return cls


def register_graphql_schema(Query=None, Mutation=None, Subscription=None):
    if Query:
        registry.queries.append(Query)
    if Mutation:
        registry.mutations.append(Mutation)
    if Subscription:
        registry.subscriptions.append(Subscription)


def register_query_field(field_name, plural_field_name=None, query_params=None):
    from .types.structures import QuerySetList
    from .utils import resolve_queryset

    if not plural_field_name:
        plural_field_name = field_name + "s"

    def inner(cls):
        field_type = lambda: registry.models[cls]
        field_query_params = query_params or {"id": graphene.Int()}

        def Mixin():
            # Generic methods to get all and query one model instance.
            def resolve_singular(self, _, info, **kwargs):
                # If no filters then return nothing,
                if not kwargs:
                    return None

                try:
                    # If is a Page then only query live/public pages.
                    if issubclass(cls, Page):
                        return cls.objects.live().public().get(**kwargs)

                    return cls.objects.get(**kwargs)
                except:
                    return None

            def resolve_plural(self, _, info, **kwargs):
                qs = cls.objects
                if issubclass(cls, Page):
                    qs = cls.objects.live().public().order_by("-first_published_at")

                # Filter queryset for field_query_params
                # Important: each field_query_param must be indexed in the model:
                # index.FilterField("field_query_param")
                qs = qs.filter(
                    **{
                        key: kwargs.get(key)
                        for (key, value) in field_query_params.items()
                        if key not in ["id", "token"] and key in kwargs
                    }
                )

                return resolve_queryset(qs.all(), info, **kwargs)

            # Create schema and add resolve methods
            schema = type(cls.__name__ + "Query", (), {})
            setattr(
                schema, field_name, graphene.Field(field_type, **field_query_params)
            )
            setattr(schema, plural_field_name, QuerySetList(field_type))
            setattr(
                schema, "resolve_" + field_name, MethodType(resolve_singular, schema)
            )
            setattr(
                schema,
                "resolve_" + plural_field_name,
                MethodType(resolve_plural, schema),
            )
            return schema

        # Send schema to Bifrost schema.
        register_graphql_schema(Query=Mixin())
        return cls

    return inner


def register_paginated_query_field(
    field_name,
    plural_field_name=None,
    query_params=None,
    required=False,
    plural_required=False,
    plural_item_required=False,
):
    from .types.structures import PaginatedQuerySet
    from .utils import resolve_paginated_queryset

    if not plural_field_name:
        plural_field_name = field_name + "s"

    def inner(cls):
        field_type = lambda: registry.models[cls]
        field_query_params = query_params

        field_query_params = query_params or {"id": graphene.Int()}

        if issubclass(cls, Page):
            field_query_params["slug"] = graphene.Argument(
                graphene.String, description=ugettext_lazy("The page slug.")
            )
            field_query_params["token"] = graphene.Argument(
                graphene.String, description=ugettext_lazy("The preview token.")
            )

        def Mixin():
            # Generic methods to get all and query one model instance.
            # @test(cls)
            def resolve_singular(self, _, info, **kwargs):
                if hasattr(cls, "bifrost_queryset"):
                    qs = cls.bifrost_queryset(info, **kwargs)
                else:
                    qs = cls.objects

                # If no filters then return nothing.
                if not kwargs:
                    return None

                try:
                    # If is a Page then only query live/public pages.
                    if issubclass(cls, Page):
                        if "token" in kwargs and hasattr(
                            cls, "get_page_from_preview_token"
                        ):
                            return cls.get_page_from_preview_token(kwargs["token"])

                        return qs.live().public().get(**kwargs)

                    return qs.get(**kwargs)
                except:
                    return None

            def resolve_plural(self, _, info, **kwargs):
                if hasattr(cls, "bifrost_queryset"):
                    qs = cls.bifrost_queryset(info, **kwargs)
                else:
                    qs = cls.objects

                if issubclass(cls, Page):
                    qs = qs.live().public().order_by("-first_published_at")

                # Filter queryset for field_query_params
                # Important: each field_query_param must be indexed in the model:
                # index.FilterField("field_query_param")
                qs = qs.filter(
                    **{
                        key: kwargs.get(key)
                        for (key, value) in field_query_params.items()
                        if key not in ["id", "token"] and key in kwargs
                    }
                )

                return resolve_paginated_queryset(qs.all(), info, **kwargs)

            # Create schema and add resolve methods
            schema = type(cls.__name__ + "Query", (), {})

            singular_field_type = field_type
            if required:
                singular_field_type = graphene.NonNull(field_type)

            setattr(
                schema,
                field_name,
                graphene.Field(singular_field_type, **field_query_params),
            )

            plural_field_type = field_type
            if plural_item_required:
                plural_field_type = graphene.NonNull(field_type)

            setattr(
                schema,
                plural_field_name,
                PaginatedQuerySet(
                    plural_field_type,
                    cls,
                    required=plural_required,
                    **field_query_params,
                ),
            )

            setattr(
                schema, "resolve_" + field_name, MethodType(resolve_singular, schema)
            )
            setattr(
                schema,
                "resolve_" + plural_field_name,
                MethodType(resolve_plural, schema),
            )
            return schema

        # Send schema to Bifrost schema.
        register_graphql_schema(Query=Mixin())
        return cls

    return inner
