from typing import get_args

import pytest
from pydantic import BaseModel

from pydantic_fabricated._class_model_generator import create_class_definition_model


def test_create_class_definition_model_basic():
    class_name = 'Person'

    class SampleParams(BaseModel):
        name: str
        age: int

    result_model = create_class_definition_model(class_name, SampleParams)

    assert result_model.__name__ == 'PersonDefinitionModel'

    assert issubclass(result_model, SampleParams)

    type_field = result_model.model_fields['type']
    literal_args = get_args(type_field.annotation)
    assert len(literal_args) == 1
    assert literal_args[0] == class_name


def test_create_class_definition_model_instantiation():
    class_name = 'Counter'

    class SampleParams(BaseModel):
        count: int

    result_model = create_class_definition_model(class_name, SampleParams)

    # Test valid instantiation
    instance = result_model(count=42, type=class_name)
    assert instance.model_dump() == {'count': 42, 'type': 'Counter'}

    # Test type validation
    with pytest.raises(ValueError, match='1 validation error'):
        result_model(count=42, type='WrongType')

    # Test parameter validation
    with pytest.raises(ValueError, match='1 validation error'):
        result_model(count='not_an_int', type='Counter')
