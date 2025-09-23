import json
from collections.abc import Callable
from typing import Any

import pydantic_core
from pydantic import BaseModel, GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue

from pydantic_fabricated._class_model_generator import create_class_definition_model
from pydantic_fabricated._params_model_generator import create_constructor_params_model
from pydantic_fabricated._union_generator import create_discriminated_union


class PydanticFabricated(type):
    """
    Metaclass that generates Pydantic models for constructor parameters and class definitions.
    """

    def __init__(
        cls,
        name: str,
        bases: tuple[type[Any], ...],
        namespace: dict[str, Any],
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        super().__init__(name, bases, namespace, **kwargs)
        match sum(isinstance(base, PydanticFabricated) for base in bases):
            case 0:
                is_new_hierarchy = True
            case 1:
                is_new_hierarchy = False
            case _:
                msg = 'Multiple inheritance from PydanticFabricated is not allowed'
                raise TypeError(msg)
        if is_new_hierarchy:
            cls.REGISTER_CONSTRAINTS: tuple[Callable[[PydanticFabricated], bool], ...] = getattr(
                cls,
                'REGISTER_CONSTRAINTS',
                (),
            )
            cls.IMPLEMENTATIONS: dict[str, PydanticFabricated] = {}
            return
        if any(not constraint(cls) for constraint in cls.REGISTER_CONSTRAINTS):
            return
        cls.IMPLEMENTATIONS[name] = cls
        cls.CONSTRUCTOR_PARAMS_MODEL = create_constructor_params_model(cls)
        cls.DEFINITION_MODEL = create_class_definition_model(name, cls.CONSTRUCTOR_PARAMS_MODEL)

    def fabricate_from_type(cls, type_: str, params: dict[str, Any]) -> Any:  # noqa: ANN401
        """
        Fabricate an instance of a subclass based on the provided type and parameters.

        :param type_: The type of the subclass to instantiate
        :param params: The constructor parameters for the subclass
        :return: An instance of the specified subclass
        :raises ValueError: If the type is not registered or parameters are invalid
        """
        if type_ not in cls.IMPLEMENTATIONS:
            msg = f'Type {type_} is not registered. Available types: {list(cls.IMPLEMENTATIONS.keys())}'
            raise ValueError(msg)
        implementation = cls.IMPLEMENTATIONS[type_]
        try:
            constructor_params = implementation.CONSTRUCTOR_PARAMS_MODEL(**params)
        except Exception as e:
            msg = f'Invalid parameters for type {type_}: {e}'
            raise ValueError(msg) from e
        return implementation(**constructor_params.model_dump())

    def fabricate_from_model(cls, model: BaseModel) -> Any:  # noqa: ANN401
        """
        Fabricate an instance of a subclass based on the provided Pydantic model.

        :param model: A Pydantic model instance representing the class definition
        :return: An instance of the specified subclass
        """
        model_dict = model.model_dump()
        type_ = model_dict.pop('type')
        return cls.fabricate_from_type(type_, model_dict)

    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,  # noqa: ANN401
        handler: GetCoreSchemaHandler,
    ) -> pydantic_core.CoreSchema:
        inner_schema = handler.generate_schema(
            create_discriminated_union(
                tuple(implementation.DEFINITION_MODEL for implementation in cls.IMPLEMENTATIONS.values()),
            ),
        )
        return pydantic_core.core_schema.union_schema(
            [
                pydantic_core.core_schema.is_instance_schema(cls),
                pydantic_core.core_schema.chain_schema(
                    [
                        pydantic_core.core_schema.no_info_plain_validator_function(
                            lambda v: json.loads(v) if isinstance(v, str) else v,
                        ),
                        inner_schema,
                        pydantic_core.core_schema.no_info_plain_validator_function(
                            lambda v: cls.fabricate_from_model(v),
                        ),
                    ],
                ),
            ],
        )

    def __get_pydantic_json_schema__(
        cls,
        core_schema: pydantic_core.CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        json_schema = handler(core_schema['choices'][1]['steps'][1])
        return handler.resolve_ref_schema(json_schema)
