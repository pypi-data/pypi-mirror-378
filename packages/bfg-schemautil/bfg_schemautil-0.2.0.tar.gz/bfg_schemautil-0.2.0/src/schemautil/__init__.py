from schemautil.make import make_object


def object_schema(obj):
    return make_object(obj, False)


__all__ = ["object_schema"]
