def get_related_fields(model):
    """
    Return a list of RelatedObject records for all relations of the given model,
    including ones attached to ancestors of the model
    """

    return [field for field in model._meta.get_fields() if field.is_relation]


def get_foreign_related_fields(model):
    """
    Return a list of RelatedObject records for all relations of the given model,
    including ones attached to ancestors of the model
    """

    fields = []

    for field in model._meta.get_fields():
        try:
            if field.remote_field.is_relation:
                fields.append(field.remote_field)

        except AttributeError:
            pass

    return fields
