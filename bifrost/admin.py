from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)

from .files import BifrostFile


class BifrostFileAdmin(ModelAdmin):
    model = BifrostFile
    menu_label = "Files"
    menu_icon = "fa-file"
    menu_order = 290
    add_to_settings_menu = False
    exclude_from_explorer = False


class BifrostAdmin(ModelAdminGroup):
    menu_label = "Bifrost"
    menu_icon = "fa-circle-o-notch"
    menu_order = 110
    add_to_settings_menu = False
    exclude_from_explorer = False
    items = (BifrostFileAdmin,)


modeladmin_register(BifrostAdmin)
