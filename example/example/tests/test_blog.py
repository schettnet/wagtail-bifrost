import datetime
import decimal

import wagtail_factories
from home.blocks import ImageGalleryImages, ImageGalleryImage
from home.factories import BlogPageFactory, ImageGalleryImageFactory
from wagtail.core.blocks import StreamValue, StructValue, BoundBlock
from wagtail.core.rich_text import RichText

from .test_bifrost import BaseBifrostTest


class BlogTest(BaseBifrostTest):
    def setUp(self):
        super().setUp()

        self.blog_page = BlogPageFactory(
            body=[
                ("heading", "Test heading 1"),
                ("paragraph", RichText("This is a paragraph.")),
                ("heading", "Test heading 2"),
                ("image", wagtail_factories.ImageFactory()),
                ("decimal", decimal.Decimal(1.2)),
                ("date", datetime.date.today()),
                ("datetime", datetime.datetime.now()),
                ("gallery", {
                    "title": "Gallery title",
                    "images": StreamValue(
                        stream_block=ImageGalleryImages(),
                        stream_data=[
                            (
                                "image", {
                                    "image": wagtail_factories.ImageChooserBlockFactory(),
                                },
                            ),
                            (
                                "image", {
                                    "image": wagtail_factories.ImageChooserBlockFactory(),
                                },
                            ),
                        ],
                    ),
                }),
            ],
        )

    def test_blog_page(self):
        query = '''
        {
            page(id:%s) {
                title
                ... on BlogPage {
                    body {
                        id
                        blockType
                        ... on CharBlock {
                            rawValue
                        }
                        ... on RichTextBlock {
                            rawValue
                        }
                        ... on ImageChooserBlock {
                            image {
                                id
                                src
                            }
                        }
                        ... on DecimalBlock {
                            rawValue
                        }
                        ... on DateBlock {
                            rawValue
                        }
                        ... on DateTimeBlock {
                            rawValue
                        }
                        ... on ImageGalleryBlock {
                            value
                        }
                    }
                }
            }
        }
        ''' % (self.blog_page.id)


        executed = self.client.execute(query)

        from pprint import pprint
        pprint(executed)
