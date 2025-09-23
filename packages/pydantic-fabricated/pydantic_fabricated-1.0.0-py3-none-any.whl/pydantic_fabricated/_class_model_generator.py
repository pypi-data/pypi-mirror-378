from typing import Literal

from pydantic import BaseModel, create_model


def create_class_definition_model(
    class_name: str,
    constructor_params_model: type[BaseModel],
) -> type[BaseModel]:
    """
    Create a Pydantic model representing a class definition with a single field for constructor parameters.

    :param class_name: The name of the class
    :param constructor_params_model: The Pydantic model representing the constructor parameters
    :return: A Pydantic BaseModel subclass with a single field 'constructor_params'
    """
    return create_model(
        f'{class_name}DefinitionModel',
        __base__=constructor_params_model,
        type=Literal[class_name],
    )
