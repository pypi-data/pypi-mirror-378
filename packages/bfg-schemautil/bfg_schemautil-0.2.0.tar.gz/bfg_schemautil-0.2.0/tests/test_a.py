from schemautil.make import (
    make_array,
    make_complex_union,
    make_enum,
    make_object,
    make_type,
    make_union,
)


def test_make_union():
    """Test make_union function with primitive types."""
    # Non-nullable string
    result = make_union("string", False)
    expected = {"type": "string"}
    assert result == expected

    # Nullable string
    result = make_union("string", True)
    expected = {"type": ["string", "null"]}
    assert result == expected

    # Non-nullable list of primitives
    result = make_union(["string", "number"], False)
    expected = {"type": ["string", "number"]}
    assert result == expected

    # Nullable list of primitives
    result = make_union(["string", "number"], True)
    expected = {"type": ["string", "number", "null"]}
    assert result == expected


def test_make_complex_union():
    """Test make_complex_union function with mixed types."""
    # Non-nullable complex union: number and object
    input_types = ["number", {"z": "string"}]
    result = make_complex_union(input_types, False)
    expected = {
        "anyOf": [
            {"type": "number"},
            {
                "type": "object",
                "properties": {"z": {"type": "string"}},
                "required": ["z"],
                "additionalProperties": False,
            },
        ]
    }
    assert result == expected

    # Nullable complex union
    result = make_complex_union(input_types, True)
    expected = {
        "anyOf": [
            {"type": "number"},
            {
                "type": "object",
                "properties": {"z": {"type": "string"}},
                "required": ["z"],
                "additionalProperties": False,
            },
            {"type": "null"},
        ]
    }
    assert result == expected


def test_make_enum():
    """Test make_enum function with set input."""
    # Non-nullable enum with mixed types
    input_set = {1, 2, 3, "unknown"}
    result = make_enum(input_set, False)
    expected = {"enum": [1, 2, 3, "unknown"]}  # Order may vary but content is correct
    assert set(result["enum"]) == input_set

    # Nullable enum
    result = make_enum(input_set, True)
    expected_values = {1, 2, 3, "unknown", None}
    assert set(result["enum"]) == expected_values


def test_make_array():
    """Test make_array function."""
    # Non-nullable array of strings
    result = make_array("string", False)
    expected = {"type": "array", "items": {"type": "string"}}
    assert result == expected

    # Nullable array of numbers
    result = make_array("number", True)
    expected = {"type": ["array", "null"], "items": {"type": "number"}}
    assert result == expected


def test_make_object():
    """Test make_object function with required and nullable fields."""
    # Object with required and nullable fields
    input_obj = {"x": "string", "y?": "number"}
    result = make_object(input_obj, False)
    expected = {
        "type": "object",
        "properties": {"x": {"type": "string"}, "y": {"type": ["number", "null"]}},
        "required": ["x", "y"],
        "additionalProperties": False,
    }
    assert result == expected

    # Nullable object
    result = make_object(input_obj, True)
    expected = {
        "type": ["object", "null"],
        "properties": {"x": {"type": "string"}, "y": {"type": ["number", "null"]}},
        "required": ["x", "y"],
        "additionalProperties": False,
    }
    assert result == expected


def test_make_type():
    """Test make_type function with various input types."""
    # Primitive string
    result = make_type("string", False)
    expected = {"type": "string"}
    assert result == expected

    # Set (enum)
    result = make_type({1, 2, 3}, False)
    expected_values = {1, 2, 3}
    assert set(result["enum"]) == expected_values

    # Dict (object)
    result = make_type({"x": "string"}, False)
    expected = {
        "type": "object",
        "properties": {"x": {"type": "string"}},
        "required": ["x"],
        "additionalProperties": False,
    }
    assert result == expected

    # List with single element (array)
    result = make_type(["string"], False)
    expected = {"type": "array", "items": {"type": "string"}}
    assert result == expected

    # List with multiple primitives (union)
    result = make_type(["string", "number"], False)
    expected = {"type": ["string", "number"]}
    assert result == expected
