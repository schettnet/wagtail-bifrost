import json

import channels_graphql_ws
import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import superuser_required
from python_graphql_client import GraphqlClient

from ..settings import BIFROST_DROPPER_ENDPOINT, BIFROST_DROPPER_HEIMDALL_LICENSE
from .types import GenerationTypes


class DropperHeimdallGeneration(graphene.Mutation):
    taskId = graphene.String()

    class Arguments:
        token = graphene.String(required=False)

    @superuser_required
    def mutate(self, info, **kwargs):
        try:
            import bifrost.api.schema

            from .connection import authenticate

            bifrost_auth_token = authenticate()
            client = GraphqlClient(endpoint=BIFROST_DROPPER_ENDPOINT)

            introspection_dict = bifrost.api.schema.schema.introspect()
            introspection_data = json.dumps(introspection_dict)

            query = """
                mutation heimdallGeneration($introspectionData: JSONString!, $licenseKey: String!) {
                    heimdallGeneration(introspectionData: $introspectionData, licenseKey: $licenseKey) {
                        taskId
                    }
                }
            """

            heimdall_generation_data = client.execute(
                query=query,
                variables={
                    "introspectionData": introspection_data,
                    "licenseKey": BIFROST_DROPPER_HEIMDALL_LICENSE,
                },
                headers={"Authorization": f"JWT {bifrost_auth_token}"},
            )

            if "errors" in heimdall_generation_data:
                raise GraphQLError(heimdall_generation_data["errors"][0]["message"])

            taskId = heimdall_generation_data["data"]["heimdallGeneration"]["taskId"]

            return DropperHeimdallGeneration(taskId=taskId)
        except Exception as ex:
            raise GraphQLError(ex)


class Mutation(graphene.ObjectType):
    dropper_heimdall_generation = DropperHeimdallGeneration.Field()


class OnNewDropperHeimdallGeneration(channels_graphql_ws.Subscription):
    """Simple GraphQL subscription."""

    # Subscription payload.
    state = GenerationTypes.DropperState(required=True)
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

        return OnNewDropperHeimdallGeneration(
            state=GenerationTypes.DropperState.get(state), url=url
        )

    @classmethod
    async def new_dropper_heimdall_generation(cls, state, url):
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

    on_new_dropper_heimdall_generation = OnNewDropperHeimdallGeneration.Field()
