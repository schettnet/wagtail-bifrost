from django.conf import settings
from graphene_django import DjangoObjectType
from wagtailmedia.models import Media

from bifrost.decorators import login_required


class MediaObjectType(DjangoObjectType):
    class Meta:
        """Can change over time."""

        model = Media
        exclude = ("tags",)

    @login_required
    def resolve_file(self, info, **kwargs):
        if self.file.url[0] == "/":
            return settings.BASE_URL + self.file.url
        return self.file.url
