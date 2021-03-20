from typing import Literal

import graphene

from bifrost.api.registry import registry

from .mutations import CreateMutation, DeleteMutation, UpdateMutation
from .queries import ReadPluralQuery, ReadQuery

KETSCHUP = []


def register_operation(
    model,
    operation,
    operation_name,
    operation_type: Literal["Query", "Mutation", "Subscription"],
    lazy=True,
):
    def tomato(mdl):
        class ModelMutation(operation):
            class Meta:
                model = mdl
                name = operation_name

        class Operation(graphene.ObjectType):
            pass

        setattr(Operation, operation_name, ModelMutation.Field())

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
    create=False, read_singular=False, read_plural=False, update=False, delete=True
):
    def inner(model):
        if create:
            register_operation(
                model, CreateMutation, f"create_{model.__name__}", "Mutation"
            )
        if read_singular:
            register_operation(model, ReadQuery, f"read_{model.__name__}", "Query")
        if read_plural:
            register_operation(
                model, ReadPluralQuery, f"read_{model.__name__}s", "Query"
            )
        if update:
            register_operation(
                model, UpdateMutation, f"update_{model.__name__}", "Mutation"
            )
        if delete:
            register_operation(
                model, DeleteMutation, f"delete_{model.__name__}", "Mutation"
            )

        return model

    return inner


def load_lazy_registrations():
    for tomato in KETSCHUP:
        tomato()