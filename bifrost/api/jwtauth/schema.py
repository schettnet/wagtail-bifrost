import graphene
import graphql_jwt
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType

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
