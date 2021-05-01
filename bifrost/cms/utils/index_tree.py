import json
from hashlib import sha256
from typing import Tuple

from wagtail.core.models import Page

index_tree = {}
index_tree_checksum = ""


def generate_index_tree(
    root_page, checksum: str = "", force=False
) -> Tuple[dict, str, bool]:
    global index_tree
    global index_tree_checksum

    if not force:
        has_updated = False

        if index_tree and index_tree_checksum:
            if index_tree_checksum != checksum:
                has_updated = True

            return index_tree, index_tree_checksum, has_updated

    def build_node(page: Page):
        index = {
            "id": page.id,
            "fields": {
                "type": page._meta.object_name,
                "slug": page.slug,
                "title": page.title,
            },
            "nodes": [],
        }

        for page in page.get_children().specific():
            index["nodes"].append(build_node(page))

        return index

    site_index = build_node(root_page)

    index_tree = site_index
    index_tree_checksum = sha256(
        json.dumps(site_index, sort_keys=True).encode()
    ).hexdigest()

    return index_tree, index_tree_checksum, True
