JSON Schema is good but very verbose. Writing it by hand is hard.
This library defines a simpler version of JSON Schema. It supports only part of the full spec and turns that simpler format into standard JSON Schema.

Examples:

an object

```json
{
    "x": "string",
    "y": "number",
}
```

nullable fields

```json
{
    "x?": "string",
}
```

"x?" is a shortcut for

```json
{
    "x": ["string", "null"],
}
```

union fields

```json
{
    "x": ["string", "number"],
}
```

array

```json
{
    "x": ["string"],
}
```

enum (uses set type in python)

```json
{
    "x": {1,2,3,"unknown",null},
}
```

complex union type

```json
{
    "x": [
        "number",
        { "z": "string" },
    ],
}
```

By default, the object schema is strict: all properties are required, and no extra properties are allowed.

Code example:

```python
from schemautil import object_schema

object_schema({
    "x": "string",
    "y": "number",
})
```
