import base64

from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from graphene_file_upload.django import FileUploadGraphQLView
from private_storage.views import PrivateStorageView

from .files.models import BifrostFile

SHOULD_EXPOSE_GRAPHIQL = settings.DEBUG or getattr(
    settings, "BIFROST_EXPOSE_GRAPHIQL", False
)


class BifrostView(View):
    playground = SHOULD_EXPOSE_GRAPHIQL

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        if self.playground:
            return render(
                request,
                "bifrost/playground.html",
                {"url": request.build_absolute_uri()},
            )

        raise Http404()

    @method_decorator(ensure_csrf_cookie)
    def post(self, request):
        return FileUploadGraphQLView.as_view(graphiql=False)(request)


class BifrostFileView(PrivateStorageView):
    model = BifrostFile
    model_file_field = "file"

    def can_access_file(self, private_file):
        # Bypass if superuser
        if self.request.user.is_superuser:
            return True

        # Get AUTH header
        if "HTTP_AUTHORIZATION" in self.request.META:
            auth = self.request.META["HTTP_AUTHORIZATION"]
            auth = auth.split(" ")

            if len(auth) == 2:
                if auth[0].lower() == "basic":
                    access_token = (
                        base64.b64decode(auth[1]).decode("utf-8").split(":")[0]
                    )

                    try:
                        BifrostFile.objects.get(
                            access_token=access_token, file=private_file.relative_name
                        )

                        return True

                    except BifrostFile.DoesNotExist:
                        return False

        return False
