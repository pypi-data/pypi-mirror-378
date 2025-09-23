from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, List, Type, get_args, get_origin

from pydantic import BaseModel

from nlbone.utils.context import current_request


class ResponsePreference(str, Enum):
    minimal = "minimal"
    lite = "lite"
    full = "full"


class AdaptiveSchemaBase(ABC):
    @classmethod
    @abstractmethod
    def minimal(cls) -> Type:
        pass

    @classmethod
    @abstractmethod
    def lite(cls) -> Type:
        pass

    @classmethod
    @abstractmethod
    def full(cls) -> Type:
        pass

    @classmethod
    def choose(cls, preference: ResponsePreference) -> Type:
        if preference == ResponsePreference.minimal:
            return cls.minimal()
        elif preference == ResponsePreference.lite:
            return cls.lite()
        elif preference == ResponsePreference.full:
            return cls.full()
        return cls.lite()

    @classmethod
    def serialize(cls, obj: Any, preference: ResponsePreference = None) -> Any:
        if not preference:
            preference = current_request().state.response_preference

        schema = cls.choose(preference)

        if isinstance(obj, list):
            return [cls._recursive_serialize(schema, item) for item in obj]

        return cls._recursive_serialize(schema, obj)

    @classmethod
    def _recursive_serialize(cls, schema_cls: type[BaseModel], item: Any) -> dict:
        # Create base dict from ORM model
        raw_data = schema_cls.model_validate(item).model_dump()

        # Check each field to see if it needs nested serialization
        annotations = schema_cls.__annotations__

        for field_name, field_type in annotations.items():
            field_value = getattr(item, field_name, None)

            if field_value is None:
                continue

            # Check for nested AdaptiveSchemaBase (single object)
            if isinstance(field_type, type) and issubclass(field_type, AdaptiveSchemaBase):
                raw_data[field_name] = field_type.serialize(field_value)

            # Check for list[AdaptiveSchemaBase]
            elif get_origin(field_type) in (list, List):
                sub_type = get_args(field_type)[0]
                if isinstance(sub_type, type) and issubclass(sub_type, AdaptiveSchemaBase):
                    raw_data[field_name] = sub_type.serialize(field_value)

        return raw_data
