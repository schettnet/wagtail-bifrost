import json

import channels_graphql_ws
import graphene
from graphql import GraphQLError
from python_graphql_client import GraphqlClient

from bifrost.decorators import superuser_required

from ..settings import BIFROST_HIVE_ENDPOINT, BIFROST_HIVE_HEIMDALL_LICENSE
from .types import GenerationTypes


class HiveHeimdallGeneration(graphene.Mutation):
    task_id = graphene.String()
    remaining_uses = graphene.String()

    class Arguments:
        token = graphene.String(required=False)

    @superuser_required
    def mutate(self, info, **kwargs):
        try:
            import bifrost.api.schema

            from .connection import authenticate

            bifrost_auth_token = authenticate()
            client = GraphqlClient(endpoint=BIFROST_HIVE_ENDPOINT)

            introspection_dict = bifrost.api.schema.schema.introspect()
            introspection_data = json.dumps(introspection_dict)

            query = """
                mutation heimdallGeneration($introspectionData: JSONString!, $licenseKey: String!) {
                    heimdallGeneration(introspectionData: $introspectionData, licenseKey: $licenseKey) {
                        taskId
                        remainingUses
                    }
                }
            """

            heimdall_generation_data = client.execute(
                query=query,
                variables={
                    "introspectionData": introspection_data,
                    "licenseKey": BIFROST_HIVE_HEIMDALL_LICENSE,
                },
                headers={"Authorization": f"JWT {bifrost_auth_token}"},
            )

            if "errors" in heimdall_generation_data:
                raise GraphQLError(heimdall_generation_data["errors"][0]["message"])

            task_id = heimdall_generation_data["data"]["heimdallGeneration"]["taskId"]
            remaining_uses = heimdall_generation_data["data"]["heimdallGeneration"][
                "remainingUses"
            ]

            return HiveHeimdallGeneration(
                task_id=task_id, remaining_uses=remaining_uses
            )
        except Exception as ex:
            raise GraphQLError(ex)


class Mutation(graphene.ObjectType):
    hive_heimdall_generation = HiveHeimdallGeneration.Field()


class OnNewHiveHeimdallGeneration(channels_graphql_ws.Subscription):
    """Simple GraphQL subscription."""

    # Subscription payload.
    state = GenerationTypes.HiveState(required=True)
    url = graphene.String()

    class Arguments:
        """That is how subscription arguments are defined."""

    @staticmethod
    @superuser_required
    def subscribe(root, info):
        """Called when user subscribes."""

        # Return the list of subscription group names.
        return ["heimdall_generation"]

    @staticmethod
    def publish(payload, info):
        """Called to notify the client."""

        # Here `payload` contains the `payload` from the `broadcast()`
        # invocation (see below). You can return `MySubscription.SKIP`
        # if you wish to suppress the notification to a particular
        # client. For example, this allows to avoid notifications for
        # the actions made by this particular client.

        state = payload["state"]
        url = payload["url"]

        return OnNewHiveHeimdallGeneration(
            state=GenerationTypes.HiveState.get(state), url=url
        )

    @classmethod
    async def new_hive_heimdall_generation(cls, state, url):
        """Auxiliary function to send subscription notifications.
        It is generally a good idea to encapsulate broadcast invocation
        inside auxiliary class methods inside the subscription class.
        That allows to consider a structure of the `payload` as an
        implementation details.
        """
        await cls.broadcast(
            group="heimdall_generation", payload={"state": state, "url": url}
        )


class Subscription(graphene.ObjectType):
    """Root GraphQL subscription."""

    on_new_hive_heimdall_generation = OnNewHiveHeimdallGeneration.Field()
