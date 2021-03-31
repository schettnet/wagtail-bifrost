import graphene
from graphql_jwt.decorators import superuser_required

from ..files.models import BifrostFile


class Query(graphene.ObjectType):
    bifrost_files = graphene.List(
        graphene.String, token=graphene.String(required=False)
    )

    @superuser_required
    def resolve_bifrost_files(root, info, **kwargs):
        return [file.get_download_url() for file in BifrostFile.objects.all()]
