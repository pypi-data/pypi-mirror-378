import json
import os

import pytest
from pydantic import BaseModel, TypeAdapter
from pydantic_settings import BaseSettings, SettingsConfigDict

from pydantic_fabricated.metaclass import PydanticFabricated


_REGISTER_CONSTRAINTS = (lambda cls: getattr(cls, 'IS_REGISTERED', False),)


class ValidBaseClass(metaclass=PydanticFabricated):
    REGISTER_CONSTRAINTS = _REGISTER_CONSTRAINTS


class ValidImplementation(ValidBaseClass):
    IS_REGISTERED = True

    def __init__(self, value: int):
        self.value = value


class AnotherValidImplementation(ValidBaseClass):
    IS_REGISTERED = True

    def __init__(self, name: str):
        self.name = name


def test_base_metaclass_initialization() -> None:
    """Test that basic metaclass initialization works correctly."""
    assert ValidBaseClass.REGISTER_CONSTRAINTS is _REGISTER_CONSTRAINTS
    assert isinstance(ValidBaseClass.IMPLEMENTATIONS, dict)


def test_base_metaclass_initialization_without_constraints() -> None:
    """Test that basic metaclass initialization without constraints works correctly."""

    class ValidBaseClassWithoutConstraints(metaclass=PydanticFabricated): ...

    assert ValidBaseClassWithoutConstraints.REGISTER_CONSTRAINTS == ()
    assert ValidBaseClassWithoutConstraints.IMPLEMENTATIONS == {}


def test_implementation_registration() -> None:
    """Test that implementations are properly registered."""
    assert {
        'ValidImplementation': ValidImplementation,
        'AnotherValidImplementation': AnotherValidImplementation,
    } == ValidBaseClass.IMPLEMENTATIONS
    assert issubclass(ValidImplementation.CONSTRUCTOR_PARAMS_MODEL, BaseModel)
    assert issubclass(ValidImplementation.DEFINITION_MODEL, BaseModel)


def test_multiple_inheritance() -> None:
    """Test that multiple inheritance from PydanticFabricated classes is not allowed."""

    class AnotherValidBaseClass(metaclass=PydanticFabricated): ...

    with pytest.raises(TypeError, match='Multiple inheritance from PydanticFabricated is not allowed'):

        class InvalidMultipleInheritance(ValidBaseClass, AnotherValidBaseClass): ...


def test_registration_constraints() -> None:
    """Test that registration constraints are properly enforced."""

    class UnregisteredImplementation(ValidBaseClass): ...

    assert 'UnregisteredImplementation' not in ValidBaseClass.IMPLEMENTATIONS


def test_fabricate_from_type_valid() -> None:
    """Test fabricating an instance from a valid type and parameters."""
    instance = ValidBaseClass.fabricate_from_type('ValidImplementation', {'value': 42})
    assert isinstance(instance, ValidImplementation)
    assert instance.value == 42


def test_fabricate_from_type_invalid_type() -> None:
    """Test fabricating an instance with an invalid type."""
    with pytest.raises(ValueError, match='Type NonexistentType is not registered'):
        ValidBaseClass.fabricate_from_type('NonexistentType', {'value': 42})


def test_fabricate_from_type_invalid_params() -> None:
    """Test fabricating an instance with invalid parameters."""
    with pytest.raises(ValueError, match='Invalid parameters for type'):
        ValidBaseClass.fabricate_from_type('ValidImplementation', {'invalid_param': 42})


def test_fabricate_from_model() -> None:
    """Test fabricating an instance from a Pydantic model."""

    class TestModel(BaseModel):
        type: str
        value: int

    model = TestModel(type='ValidImplementation', value=42)
    instance = ValidBaseClass.fabricate_from_model(model)

    assert isinstance(instance, ValidImplementation)
    assert instance.value == 42


def test_pydantic_core_schema_json() -> None:
    """Test that the Pydantic core schema handles JSON string input."""

    class TestModel(BaseModel):
        implementation: ValidBaseClass

    # Test raw JSON string input
    json_data = r'{"type": "ValidImplementation", "value": 42}'
    model = TestModel.model_validate_json(f'{{"implementation": {json_data}}}')
    instance = model.implementation

    assert isinstance(instance, ValidImplementation)
    assert instance.value == 42


def test_pydantic_core_schema_dict() -> None:
    """Test that the Pydantic core schema handles dictionary input."""

    class TestModel(BaseModel):
        implementation: ValidBaseClass

    model = TestModel.model_validate(
        {
            'implementation': {
                'type': 'ValidImplementation',
                'value': 42,
            },
        },
    )

    instance = model.implementation
    assert isinstance(instance, ValidImplementation)
    assert instance.value == 42


def test_pydantic_core_schema_model() -> None:
    """Test that the Pydantic core schema handles model input."""

    class TestModel(BaseModel):
        implementation: ValidBaseClass

    model = TestModel.model_validate(
        {
            'implementation': ValidImplementation(42),
        },
    )

    instance = model.implementation
    assert isinstance(instance, ValidImplementation)
    assert instance.value == 42


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='my_prefix_')
    implementation: ValidBaseClass


def test_settings_integration() -> None:
    """Test integration with Pydantic Settings."""
    os.environ['MY_PREFIX_IMPLEMENTATION'] = json.dumps(
        {
            'type': 'ValidImplementation',
            'value': 42,
        },
    )
    try:
        settings = Settings()  # type: ignore[call-arg]
        instance = settings.implementation

        assert isinstance(instance, ValidImplementation)
        assert instance.value == 42
    finally:
        del os.environ['MY_PREFIX_IMPLEMENTATION']


def test_json_schema() -> None:
    """Test that the generated JSON schema is correct."""
    schema = TypeAdapter(ValidBaseClass).json_schema()
    assert schema == {
        '$defs': {
            'AnotherValidImplementationDefinitionModel': {
                'properties': {
                    'name': {
                        'title': 'Name',
                        'type': 'string',
                    },
                    'type': {
                        'const': 'AnotherValidImplementation',
                        'title': 'Type',
                        'type': 'string',
                    },
                },
                'required': [
                    'name',
                    'type',
                ],
                'title': 'AnotherValidImplementationDefinitionModel',
                'type': 'object',
            },
            'ValidImplementationDefinitionModel': {
                'properties': {
                    'type': {
                        'const': 'ValidImplementation',
                        'title': 'Type',
                        'type': 'string',
                    },
                    'value': {
                        'title': 'Value',
                        'type': 'integer',
                    },
                },
                'required': [
                    'value',
                    'type',
                ],
                'title': 'ValidImplementationDefinitionModel',
                'type': 'object',
            },
        },
        'discriminator': {
            'mapping': {
                'AnotherValidImplementation': '#/$defs/AnotherValidImplementationDefinitionModel',
                'ValidImplementation': '#/$defs/ValidImplementationDefinitionModel',
            },
            'propertyName': 'type',
        },
        'oneOf': [
            {
                '$ref': '#/$defs/ValidImplementationDefinitionModel',
            },
            {
                '$ref': '#/$defs/AnotherValidImplementationDefinitionModel',
            },
        ],
    }
