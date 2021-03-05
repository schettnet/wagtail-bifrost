import graphene
import graphql_jwt

# django
from django.utils.text import camel_case_to_spaces
from graphql.validation.rules import NoUnusedFragments, specified_rules

# HACK: Remove NoUnusedFragments validator
# Due to the way previews work on the frontend, we need to pass all
# fragments into the query even if they're not used.
# This would usually cause a validation error. There doesn't appear
# to be a nice way to disable this validator so we monkey-patch it instead.


# We need to update specified_rules in-place so the change appears
# everywhere it's been imported

specified_rules[:] = [rule for rule in specified_rules if rule is not NoUnusedFragments]

# We load all Queries, Mutations and Subscriptions into the registry if not excluded
# by settings.

import bifrost.dropper.schema
import bifrost.files.schema
import bifrost.types.documents
import bifrost.types.images
import bifrost.types.redirects
import bifrost.types.search
import bifrost.types.settings
import bifrost.types.snippets

from .registry import registry
from .settings import (
    BIFROST_API_DOCUMENTS,
    BIFROST_API_DROPPER,
    BIFROST_API_FILES,
    BIFROST_API_IMAGES,
    BIFROST_API_REDIRECTS,
    BIFROST_API_SEARCH,
    BIFROST_API_SETTINGS,
    BIFROST_API_SNIPPETS,
    BIFROST_AUTO_CAMELCASE,
)

QUERIES = [
    {"cls": bifrost.files.schema.Query, "active": BIFROST_API_FILES},
    {"cls": bifrost.types.documents.DocumentsQuery(), "active": BIFROST_API_DOCUMENTS},
    {"cls": bifrost.types.images.ImagesQuery(), "active": BIFROST_API_IMAGES},
    {"cls": bifrost.types.redirects.RedirectsQuery, "active": BIFROST_API_REDIRECTS},
    {"cls": bifrost.types.search.SearchQuery(), "active": BIFROST_API_SEARCH},
    {"cls": bifrost.types.settings.SettingsQuery(), "active": BIFROST_API_SETTINGS},
    {"cls": bifrost.types.snippets.SnippetsQuery(), "active": BIFROST_API_SNIPPETS},
]

MUTATIONS = [{"cls": bifrost.dropper.schema.Mutation, "active": BIFROST_API_DROPPER}]

SUBSCRIPTIONS = [
    {"cls": bifrost.dropper.schema.Subscription, "active": BIFROST_API_DROPPER}
]


registry.queries += [o["cls"] for o in QUERIES if o["active"]]
registry.mutations += [o["cls"] for o in MUTATIONS if o["active"]]
registry.subscriptions += [o["cls"] for o in SUBSCRIPTIONS if o["active"]]


def create_schema():
    """
    Root schema object that graphene is pointed at.
    It inherits its queries from each of the specific type mixins.
    """
    from .jwtauth.schema import ObtainJSONWebToken
    from .types.pages import PagesQuery, PagesSubscription

    class Query(PagesQuery(), *registry.queries, graphene.ObjectType):
        pass

    class Subscription(
        PagesSubscription(), *registry.subscriptions, graphene.ObjectType
    ):
        pass

    def mutation_parameters() -> dict:
        dict_params = {
            "token_auth": ObtainJSONWebToken.Field(),
            "verify_token": graphql_jwt.Verify.Field(),
            "refresh_token": graphql_jwt.Refresh.Field(),
            "revoke_token": graphql_jwt.Revoke.Field(),
        }

        dict_params.update(
            (camel_case_to_spaces(n).replace(" ", "_"), mut.Field())
            for n, mut in registry.forms.items()
        )
        return dict_params

    Mutations = type("Mutation", (graphene.ObjectType,), mutation_parameters())

    class Mutation(Mutations, *registry.mutations):
        pass

    return graphene.Schema(
        query=Query,
        mutation=Mutation,
        subscription=Subscription,
        types=list(registry.models.values()),
        auto_camelcase=BIFROST_AUTO_CAMELCASE,
    )


schema = create_schema()
