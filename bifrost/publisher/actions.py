from typing import Literal

import graphene

from bifrost.api.registry import registry

from .mutations import CreateMutation, DeleteMutation, UpdateMutation
from .queries import ReadPluralQuery, ReadQuery
from .utils import camel_to_snake

KETSCHUP = []


def register_operation(
    model,
    operation,
    operation_name,
    operation_type: Literal["Query", "Mutation", "Subscription"],
    permission=None,
    lazy=True,
):
    def tomato(mdl):
        class ModelOperation(operation):
            class Meta:
                model = mdl
                name = operation_name

        class Operation(graphene.ObjectType):
            pass

        if permission:
            ModelOperation.before_resolve = permission(ModelOperation.before_resolve)

        setattr(Operation, operation_name, ModelOperation.Field())

        if operation_type == "Query":
            registry.queries.append(Operation)
        elif operation_type == "Mutation":
            registry.mutations.append(Operation)
        elif operation_type == "Subscription":
            registry.subscriptions.append(Operation)

    if lazy:
        KETSCHUP.append(lambda: tomato(model))
    else:
        tomato(model)


def register_publisher(
    create=False,
    read_singular=False,
    read_plural=False,
    update=False,
    delete=True,
    # Permission decorators
    create_permission=None,
    read_singular_permission=None,
    read_plural_permission=None,
    update_permission=None,
    delete_permission=None,
):
    def inner(model):
        operation_name = camel_to_snake(model.__name__)

        if create:
            register_operation(
                model,
                CreateMutation,
                f"create_{operation_name}",
                "Mutation",
                create_permission,
            )

        if read_singular:
            register_operation(
                model,
                ReadQuery,
                f"read_{operation_name}",
                "Query",
                read_singular_permission,
            )

        if read_plural:
            register_operation(
                model,
                ReadPluralQuery,
                f"read_{operation_name}s",
                "Query",
                read_plural_permission,
            )

        if update:
            register_operation(
                model,
                UpdateMutation,
                f"update_{operation_name}",
                "Mutation",
                update_permission,
            )

        if delete:
            register_operation(
                model,
                DeleteMutation,
                f"delete_{operation_name}",
                "Mutation",
                delete_permission,
            )

        return model

    return inner


def load_lazy_registrations():
    for tomato in KETSCHUP:
        tomato()
