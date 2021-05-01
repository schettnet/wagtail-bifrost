import graphene
from graphene.types.generic import GenericScalar
from wagtail.core.models import Site

from bifrost.decorators import superuser_required

from .utils.index_tree import generate_index_tree


class PageTree(graphene.ObjectType):
    tree = graphene.Field(GenericScalar)
    has_updated = graphene.Boolean()
    checksum = graphene.String()


class Query(graphene.ObjectType):
    pages_index_tree = graphene.Field(PageTree, checksum=graphene.String(required=True))

    @superuser_required
    def resolve_pages_index_tree(root, info, checksum, **kwargs):

        root_page = Site.objects.filter(is_default_site=True).first().root_page.specific
        tree, checksum, has_updated = generate_index_tree(root_page, checksum)

        return {"tree": tree, "has_updated": has_updated, "checksum": checksum}
