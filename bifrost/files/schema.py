import graphene
from graphql_jwt.decorators import superuser_required

from ..files.models import BifrostFile


class Query(graphene.ObjectType):
    bifrost_file = graphene.Field(graphene.String, ubfn=graphene.String(required=True))
    bifrost_files = graphene.List(
        graphene.String, token=graphene.String(required=False)
    )

    @superuser_required
    def resolve_bifrost_file(root, info, ubfn, **kwargs):
        file = BifrostFile.objects.get(ubfn=ubfn)
        return file.secure_url

    @superuser_required
    def resolve_bifrost_files(root, info, **kwargs):
        return [file.secure_url for file in BifrostFile.objects.all()]
