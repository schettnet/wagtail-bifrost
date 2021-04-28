import graphene
import graphql_jwt
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType

from bifrost.decorators import login_required

# Create your registration related graphql schemes here.


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ("id", "username")


class ObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    user = graphene.Field(UserType)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        user = info.context.user

        return cls(user=user)


class Query(graphene.ObjectType):
    me = graphene.Field(UserType, token=graphene.String(required=False))

    @login_required
    def resolve_me(self, info, **kwargs):
        user = info.context.user

        return user
