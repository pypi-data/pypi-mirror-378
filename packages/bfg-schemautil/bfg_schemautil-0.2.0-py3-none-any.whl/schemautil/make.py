primitives = ["string", "number", "boolean", "null"]


def make_union(input, nullable):
    if not nullable:
        type_ = input
    elif isinstance(input, list):
        type_ = input + ["null"]
    else:
        type_ = [input, "null"]
    return {"type": type_}


def make_complex_union(input, nullable):
    union = [make_type(i, False) for i in input]
    if nullable:
        union.append({"type": "null"})
    return {"anyOf": union}


def make_enum(input, nullable):
    enum = list(input)
    if nullable:
        enum.append(None)
    return {"enum": enum}


def make_array(input, nullable):
    return make_union("array", nullable) | {
        "items": make_type(input, False),
    }


def make_object(input, nullable):
    props = {
        key.removesuffix("?"): make_type(val, key.endswith("?"))
        for key, val in input.items()
    }
    return make_union("object", nullable) | {
        "properties": props,
        "required": list(props.keys()),
        "additionalProperties": False,
    }


def make_type(input, nullable):
    assert isinstance(nullable, bool)

    if isinstance(input, str):
        if input not in primitives:
            raise ValueError(f"expected a primitive type: {input}")
        return make_union(input, nullable)

    if isinstance(input, set):
        if len(input) == 0:
            raise ValueError("cannot be empty set")
        for i in input:
            if not isinstance(i, (str, int, float, bool, None)):
                raise ValueError(f"bad value: {i}")
        return make_enum(input, nullable)

    if isinstance(input, dict):
        if len(input) == 0:
            raise ValueError("cannot be empty dict")
        for key in input:
            if not isinstance(key, str):
                raise ValueError(f"key must be str: {key}")
        return make_object(input, nullable)

    if isinstance(input, list):
        if len(input) == 0:
            raise ValueError("cannot be empty list")
        if len(input) == 1:
            return make_array(input[0], nullable)

        if all(i in primitives for i in input):
            return make_union(input, nullable)
        else:
            return make_complex_union(input, nullable)

    raise ValueError(f"bad input: {input}")
