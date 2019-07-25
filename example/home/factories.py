import datetime

import factory
import wagtail_factories
from home.blocks import (ImageGalleryBlock, ImageGalleryImage,
                         ImageGalleryImages)
from home.models import BlogPage
from wagtail.core import blocks


# START: Block Factories
class DateBlockFactory(wagtail_factories.blocks.BlockFactory):
    class Meta:
        model = blocks.DateBlock


class DateTimeBlockFactory(wagtail_factories.blocks.BlockFactory):
    class Meta:
        model = blocks.DateTimeBlock


class DecimalBlockFactory(wagtail_factories.blocks.BlockFactory):
    class Meta:
        model = blocks.DecimalBlock


class RichTextBlockFactory(wagtail_factories.blocks.BlockFactory):
    class Meta:
        model = blocks.RichTextBlock


class StreamBlockFactory(wagtail_factories.blocks.BlockFactory):
    class Meta:
        model = blocks.StreamBlock


class ImageGalleryImageFactory(wagtail_factories.StructBlockFactory):
    image = factory.SubFactory(wagtail_factories.ImageChooserBlockFactory)

    class Meta:
        model = ImageGalleryImage


class ImageGalleryImagesFactory(StreamBlockFactory):
    class Meta:
        model = ImageGalleryImages


class ImageGalleryBlockFactory(wagtail_factories.StructBlockFactory):
    title = factory.Sequence(lambda n: f"Image gallery {n}")
    images = factory.SubFactory(ImageGalleryImagesFactory)

    class Meta:
        model = ImageGalleryBlock
# END: Block Factories


# START: Page Factories
class BlogPageFactory(wagtail_factories.PageFactory):
    author = factory.Sequence(lambda n: f"Author Name{n}")
    date = datetime.date.today()
    body = wagtail_factories.StreamFieldFactory({
        "heading": wagtail_factories.CharBlockFactory,
        "paragraph": RichTextBlockFactory,
        "image": wagtail_factories.ImageChooserBlockFactory,
        "decimal": DecimalBlockFactory,
        "date": DateBlockFactory,
        "datetime": DateTimeBlockFactory,
        "gallery": ImageGalleryBlockFactory,
    })

    class Meta:
        model = BlogPage
# END: Page Factories
