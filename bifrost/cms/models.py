from django.dispatch import receiver
from wagtail.core.models import Site
from wagtail.core.signals import page_published

from .utils.index_tree import generate_index_tree


@receiver(page_published)
def update_index_tree(sender, **kwargs):
    root_page = Site.objects.filter(is_default_site=True).first().root_page.specific
    generate_index_tree(root_page, force=True)
