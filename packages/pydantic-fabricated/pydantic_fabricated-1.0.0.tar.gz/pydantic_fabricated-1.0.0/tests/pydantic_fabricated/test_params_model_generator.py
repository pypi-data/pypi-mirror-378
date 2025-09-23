from typing import Annotated, Any

from annotated_types import Ge, Le, MinLen
from pydantic import BaseModel, Field

from pydantic_fabricated._params_model_generator import create_constructor_params_model


def test_simple_class_params():
    class SimpleClass:
        def __init__(self, name: str, age: int): ...

    params_model = create_constructor_params_model(SimpleClass)

    assert issubclass(params_model, BaseModel)
    assert params_model.__name__ == 'SimpleClassConstructorParamsModel'
    fields = params_model.model_fields
    assert set(fields.keys()) == {'name', 'age'}
    assert fields['name'].annotation is str
    assert fields['name'].is_required()
    assert fields['age'].annotation is int
    assert fields['age'].is_required()


def test_class_with_optional_params():
    class ClassWithOptional:
        def __init__(self, required: str, optional: int | None = None): ...

    params_model = create_constructor_params_model(ClassWithOptional)

    assert issubclass(params_model, BaseModel)
    fields = params_model.model_fields
    assert set(fields.keys()) == {'required', 'optional'}
    assert fields['required'].annotation is str
    assert fields['required'].is_required()
    assert fields['optional'].annotation == int | None  # Union types need == comparison
    assert fields['optional'].default is None


def test_class_with_any_type():
    class ClassWithAny:
        def __init__(self, data: Any): ...

    params_model = create_constructor_params_model(ClassWithAny)

    assert issubclass(params_model, BaseModel)
    fields = params_model.model_fields
    assert set(fields.keys()) == {'data'}
    assert fields['data'].annotation is Any
    assert fields['data'].is_required()


def test_class_with_default_values():
    class ClassWithDefaults:
        def __init__(self, name: str = 'default', count: int = 0): ...

    params_model = create_constructor_params_model(ClassWithDefaults)

    assert issubclass(params_model, BaseModel)
    fields = params_model.model_fields
    assert set(fields.keys()) == {'name', 'count'}
    assert fields['name'].annotation is str
    assert fields['name'].default == 'default'
    assert fields['count'].annotation is int
    assert fields['count'].default == 0


def test_class_with_mixed_params():
    class MixedParamsClass:
        def __init__(self, required: str, optional: int | None = None, default: str = 'test'):
            self.required = required
            self.optional = optional
            self.default = default

    params_model = create_constructor_params_model(MixedParamsClass)

    assert issubclass(params_model, BaseModel)
    fields = params_model.model_fields
    assert set(fields.keys()) == {'required', 'optional', 'default'}
    assert fields['required'].annotation is str
    assert fields['required'].is_required()
    assert fields['optional'].annotation == int | None
    assert fields['optional'].default is None
    assert fields['default'].annotation is str
    assert fields['default'].default == 'test'


def test_class_with_complex_annotations():
    json_field_type = Annotated[dict[str, Any], Field(description='A JSON object')]
    int_range_type = Annotated[int, Field(ge=1, le=10)]

    class ClassWithComplexAnnotations:
        def __init__(
            self,
            data: json_field_type,
            tags: Annotated[list[str], Field(min_length=1, default_factory=lambda: ['default'])],
            count: int_range_type = 5,
        ):
            self.data = data
            self.count = count
            self.tags = tags

    params_model = create_constructor_params_model(ClassWithComplexAnnotations)
    assert issubclass(params_model, BaseModel)

    fields = params_model.model_fields
    assert set(fields.keys()) == {'data', 'count', 'tags'}

    # Check data field
    data_field = fields['data']
    assert data_field.annotation == dict[str, Any]
    assert data_field.is_required()
    assert data_field.description == 'A JSON object'

    # Check count field
    count_field = fields['count']
    assert count_field.annotation is int
    assert not count_field.is_required()
    assert count_field.default == 5
    assert count_field.metadata[0] == Ge(1)
    assert count_field.metadata[1] == Le(10)

    # Check tags field
    tags_field = fields['tags']
    assert tags_field.annotation == list[str]
    assert not tags_field.is_required()
    default_factory = tags_field.default_factory
    assert callable(default_factory)
    assert default_factory() == ['default']  # type: ignore[call-arg]
    assert tags_field.metadata[0] == MinLen(1)
