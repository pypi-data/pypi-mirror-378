# Pydantic Fabricated

A Python package that provides a metaclass for fabricating subclasses from dictionaries inside Pydantic models. This library seamlessly integrates with Pydantic's type system to enable dynamic object creation based on type definitions.

## Installation

```bash
pip install pydantic-fabricated
```

## Features

- Dynamic object creation from type definitions
- Seamless integration with Pydantic models
- Type-safe parameter validation
- Support for JSON serialization/deserialization
- Discriminated unions for type-safe polymorphism

## Quick Start

Here's a simple example of how to use Pydantic Fabricated:

```python
import os

from pydantic_settings import BaseSettings, SettingsConfigDict

from pydantic_fabricated import PydanticFabricated


# Define a base class using the metaclass
class Shape(metaclass=PydanticFabricated):
    pass


# Define concrete implementations
class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height


# Create instances using the fabricate_from_type method
circle = Shape.fabricate_from_type('Circle', {'radius': 5.0})
rectangle = Shape.fabricate_from_type('Rectangle', {'width': 10.0, 'height': 20.0})


# Or use with Pydantic Settings
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='my_prefix_')

    shape: Shape


os.environ['MY_PREFIX_SHAPE'] = r'{"type": "Circle", "radius": 5.0}'
settings = Settings()
```

## Requirements

- Python ≥ 3.13
- Pydantic ≥ 2.11.9

## License

Apache License 2.0

## Links

- [GitHub Repository](https://github.com/KRunchPL/pydantic-fabricated)
- [Documentation](https://github.com/KRunchPL/pydantic-fabricated)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Additional Documentation

- [Development Guide](README-DEV.md)
- [Changelog](CHANGELOG.md)
