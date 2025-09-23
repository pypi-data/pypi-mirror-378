from typing import Literal

import pytest
from pydantic import BaseModel, TypeAdapter, ValidationError

from pydantic_fabricated._union_generator import create_discriminated_union


class DogModel(BaseModel):
    type: Literal['DogModel']
    name: str
    breed: str


class CatModel(BaseModel):
    type: Literal['CatModel']
    name: str
    lives_left: int


class BirdModel(BaseModel):
    type: Literal['BirdModel']
    name: str
    can_fly: bool


def test_create_discriminated_union_multiple_models():
    """Test creating a discriminated union with multiple models."""
    animal_type = TypeAdapter(create_discriminated_union((DogModel, CatModel)))

    # Create and validate a dog instance
    dog_data = {'type': 'DogModel', 'name': 'Rex', 'breed': 'German Shepherd'}
    animal = animal_type.validate_python(dog_data)
    assert isinstance(animal, DogModel)
    assert animal.name == 'Rex'
    assert animal.breed == 'German Shepherd'

    # Create and validate a cat instance
    cat_data = {'type': 'CatModel', 'name': 'Whiskers', 'lives_left': 9}
    animal = animal_type.validate_python(cat_data)
    assert isinstance(animal, CatModel)
    assert animal.name == 'Whiskers'
    assert animal.lives_left == 9


def test_create_discriminated_union_custom_discriminator():
    """Test creating a discriminated union with a custom discriminator field."""

    class CustomDogModel(BaseModel):
        animal_type: Literal['DogModel'] = 'DogModel'
        name: str
        breed: str

    class CustomCatModel(BaseModel):
        animal_type: Literal['CatModel'] = 'CatModel'
        name: str
        lives_left: int

    animal_type = TypeAdapter(
        create_discriminated_union(
            (CustomDogModel, CustomCatModel),
            discriminator_field='animal_type',
        ),
    )

    # Validate using custom discriminator
    dog_data = {'animal_type': 'DogModel', 'name': 'Rex', 'breed': 'German Shepherd'}
    animal = animal_type.validate_python(dog_data)
    assert isinstance(animal, CustomDogModel)
    assert animal.name == 'Rex'
    assert animal.breed == 'German Shepherd'


def test_create_discriminated_union_single_model():
    """Test creating a discriminated union with a single model returns the model itself."""
    result = create_discriminated_union((DogModel,))
    assert result == DogModel

    # Verify it works as expected
    dog_data = {'type': 'DogModel', 'name': 'Rex', 'breed': 'German Shepherd'}
    dog = result.model_validate(dog_data)
    assert isinstance(dog, DogModel)


def test_create_discriminated_union_empty_models():
    """Test that creating a discriminated union with no models raises ValueError."""
    with pytest.raises(ValueError, match='At least one class model is required'):
        create_discriminated_union(())


def test_create_discriminated_union_validation_error():
    """Test validation errors with discriminated unions."""
    animal_type = TypeAdapter(create_discriminated_union((DogModel, CatModel, BirdModel)))

    # Test with missing required field
    invalid_data = {'type': 'DogModel', 'name': 'Rex'}  # Missing 'breed'
    with pytest.raises(ValidationError, match='breed'):
        animal_type.validate_python(invalid_data)

    # Test with invalid discriminator value
    invalid_type_data = {'type': 'HamsterModel', 'name': 'Hammy'}
    with pytest.raises(ValidationError, match=r'HamsterModel'):
        animal_type.validate_python(invalid_type_data)
