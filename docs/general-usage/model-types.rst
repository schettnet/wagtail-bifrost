Model Types
===========
What do we mean when we say types? Well in a Bifrost context, a type is descriptor
function that tells bifrost what type a Django Models field is represented by 
in GraphQL.

The field types below are simple to use and all work in the same way.
We have created a bunch of built-in types for you to use in but you can always
create your own using [Graphene](https://github.com/graphql-python/graphene) 
(Bifrosts underlying library) and take advantage of Bifrost's generic ``GraphQLField`` type.


GraphQLString
-------------
.. module:: bifrost.models
.. class:: GraphQLString(field_name)

    A basic field type is string. Commonly used for CharField, TextField, 
    UrlField or any other Django field that returns a string as it's value.

    .. attribute:: GraphQLString.field_name

        This is the name of the class property used in your model definition.

    In your models.py:
    ::

        from bifrost.types import GraphQLString

        class BlogPage(Page):
            author = models.CharField(max_length=255)
            
            graphql_fields = [
                GraphQLString("author"),
            ]


    Example query:
    ::
    
        {
            page(slug: "example-blog-page") {
                author
            }
        }


GraphQLInt
----------
.. module:: bifrost.models
.. class:: GraphQLInt(field_name)

    It's all fairly self explanatory but a `GraphQLInt` is used to 
    serialize interger based Django fields such as IntegerField 
    or PositiveSmallIntegerField.


GraphQLFloat
------------
.. module:: bifrost.models
.. class:: GraphQLFloat(field_name)

    Like GraphQLInt, This field is used to serialize Float and Decimal fields.


GraphQLBoolean
--------------
.. module:: bifrost.models
.. class:: GraphQLBoolean(field_name)


GraphQLStreamfield
------------------
.. module:: bifrost.models
.. class:: GraphQLStreamfield(field_name)

This field type supports all built in Streamfield blocks. It also supports 
custom blocks built using StructBlock and the like.


GraphQLSnippet
--------------
.. module:: bifrost.models
.. class:: GraphQLSnippet(field_name, snippet_modal)

    GraphQLSnippet is a little bit more complicated; You first need to define
    a `graphql_field` list on your snippet like you do your page. Then you need
    to reference the snippet in the field type function.

    Your snippet values are then available through a sub-selection query on the
    field name.

    .. attribute:: GraphQLString.field_name

        This is the name of the class property used in your model definition.

    .. attribute:: GraphQLString.snippet_modal

        String which defines the location of the snippet model.


    In your models.py:

    ::

        class BookPage(Page):
            advert = models.ForeignKey(
                'demo.Advert',
                null=True,
                blank=True,
                on_delete=models.SET_NULL,
                related_name='+'
            )

            graphql_fields = [
                GraphQLSnippet('advert', 'demo.Advert'),
            ]

            content_panels = Page.content_panels + [
                SnippetChooserPanel('advert'),
            ]

        @register_snippet
        class Advert(models.Model):
            url = models.URLField(null=True, blank=True)
            text = models.CharField(max_length=255)

            graphql_fields = [
                GraphQLString('url'),
                GraphQLString('text'),
            ]

            panels = [
                FieldPanel('url'),
                FieldPanel('text'),
            ]

            def __str__(self):
                return self.text


    ::

        #Example Query
        {
            page(slug: "some-blog-page") {
                advert {
                    url
                    text
                }
            }
        }


GraphQLForeignKey
-----------------
.. module:: bifrost.models
.. class:: GraphQLForeignKey(field_name, content_type, is_list = False)

    GraphQLForeignKey is similar to GraphQLSnippet in that you pass a 
    ``field_name`` and ``content_type`` but you can also specify that the field
    is a list (for example when using ``Orderable``).

    .. attribute:: GraphQLString.field_name

        This is the name of the class property used in your model definition.

    .. attribute:: GraphQLString.snippet_modal

        String which defines the location of the snippet model you are referencing.

    .. attribute:: GraphQLString.is_list

        Define whether this field should be a list (for example when using ``Orderable``).

    ::

        class BookPage(Page):
            advert = models.ForeignKey(
                'demo.Advert',
                null=True,
                blank=True,
                on_delete=models.SET_NULL,
                related_name='+'
            )

            graphql_fields = [
                GraphQLSnippet('advert', 'demo.Advert'),
            ]

            content_panels = Page.content_panels + [
                SnippetChooserPanel('advert'),
            ]


GraphQLImage
------------

.. module:: bifrost.models
.. class:: GraphQLImage(field_name)

    To serialize the WagtailImages or custom Image model then use this field
    type.


GraphQLDocument
---------------

.. module:: bifrost.models
.. class:: GraphQLDocument(field_name)

    To serialize the WagtailDocuments or custom Document model then use this 
    field type.
    

GraphQLField
------------

.. module:: bifrost.models
.. class:: GraphQLForeignKey(field_name, graphene_type)

    If you want to build your own (or use graphene's built-in types) then 
    ``GraphQLField`` is what you need.

    .. attribute:: GraphQLString.field_name

        This is the name of the class property used in your model definition.

    .. attribute:: GraphQLString.graphene_type

        The graphene type that you want to use.
