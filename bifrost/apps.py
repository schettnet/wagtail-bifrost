import os
import sys

from django.apps import AppConfig


class Bifrost(AppConfig):
    name = "bifrost"

    def ready(self):
        """
        Import all the django apps defined in django settings then process each model
        in these apps and create graphql node types from them. Then the schema file
        of all apps are imported.
        """
        from .actions import import_app_schema, import_apps, load_type_fields
        from .dropper import connect
        from .types.streamfield import register_streamfield_blocks

        import_apps()
        load_type_fields()
        register_streamfield_blocks()
        import_app_schema()

        # Init dropper websocket connection
        if os.environ.get("RUN_MAIN", None) != "true" and (
            "manage.py" not in sys.argv or "runserver" in sys.argv
        ):
            connect()
