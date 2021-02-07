from bifrost.registry import registry
import graphene
from .models import CustomImage
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User


class Test(graphene.Mutation):
    member = graphene.Field(
        registry.models[get_user_model()], token=graphene.String(required=False)
    )
    generated_password = graphene.String()

    class Arguments:
        token = graphene.String(required=False)

    def mutate(self, info, **kwargs):
        return Test(
            member=get_user_model().objects.first(), generated_password="password"
        )


class Mutation(graphene.ObjectType):
    test = Test.Field()


class Query(graphene.ObjectType):
    test = graphene.Field(
        registry.models[get_user_model()], token=graphene.String(required=False)
    )

    def resolve_test(self, info, **kwargs):
        return get_user_model().objects.first()