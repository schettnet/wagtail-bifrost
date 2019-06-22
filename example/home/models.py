from django.db import models

from wagtail.core.models import Page
from wagtail.core.fields import StreamField
from wagtail.core import blocks
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.snippets.edit_handlers import SnippetChooserPanel

from bifrost.models import (
    GraphQLField, 
    GraphQLString, 
    GraphQLSnippet, 
    BifrostPageMixin,
    GraphQLStreamfield, 
)

class HomePage(Page):
    pass

class BlogPage(BifrostPageMixin, Page):
    author = models.CharField(max_length=255)
    date = models.DateField("Post date")
    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paraagraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('decimal', blocks.DecimalBlock()),
        ('date', blocks.DateBlock()),
        ('datetime', blocks.DateTimeBlock()),
        ('quote', blocks.BlockQuoteBlock()),
        ('drink', blocks.ChoiceBlock(choices=[
            ('tea', 'Tea'),
            ('coffee', 'Coffee'),
        ], icon='time')),
        ('somepage', blocks.PageChooserBlock()),
        ('static', blocks.StaticBlock(
            admin_text='Latest posts: no configuration needed.',
        )),
        ('person', blocks.StructBlock([
            ('first_name', blocks.CharBlock()),
            ('surname', blocks.CharBlock()),
            ('photo', ImageChooserBlock(required=False)),
            ('biography', blocks.RichTextBlock()),
        ], icon='user')),
        ('video', EmbedBlock()),
        ('carousel', blocks.StreamBlock(
            [
                ('image', ImageChooserBlock()),
                ('quotation', blocks.StructBlock([
                    ('text', blocks.TextBlock()),
                    ('author', blocks.CharBlock()),
                ])),
            ],
            icon='cogs'
        )),
        ('doc', DocumentChooserBlock()),
        ('ingredients_list', blocks.ListBlock(blocks.StructBlock([
            ('ingredient', blocks.CharBlock()),
            ('amount', blocks.CharBlock(required=False)),
        ]))),
    ])

    content_panels = Page.content_panels + [
        FieldPanel('author'),
        FieldPanel('date'),
        StreamFieldPanel('body')
    ]

    graphql_fields = [
        GraphQLString('heading'),
        GraphQLString('date'),
        GraphQLString('author'),
        GraphQLStreamfield('body')
    ]