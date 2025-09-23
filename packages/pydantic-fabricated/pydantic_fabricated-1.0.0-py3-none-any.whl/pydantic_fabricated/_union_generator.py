from typing import Annotated, Union

from pydantic import BaseModel, Field


def create_discriminated_union(
    models: tuple[type[BaseModel], ...],
    discriminator_field: str = 'type',
) -> type[BaseModel]:
    """
    Create a Pydantic-compatible type representing a discriminated union of multiple class models.

    :param models: models to include in the union
    :param discriminator_field: The field used to discriminate between different models
    :return: A Pydantic-comaptible type representing the discriminated union
    """
    match len(models):
        case 0:
            msg = 'At least one class model is required'
            raise ValueError(msg)
        case 1:
            return models[0]
    return Annotated[Union[tuple(models)], Field(discriminator=discriminator_field)]  # type: ignore [return-value]  # noqa: UP007
