from abc import ABC
from typing import Self, Tuple, Optional
from dataclasses_avroschema import AvroModel
from busline.event.message.message import Message
from busline.utils.serde import SerdableMixin


AVRO_FORMAT_TYPE = "avro"


class AvroMessageMixin(Message, SerdableMixin, AvroModel, ABC):
    """
    Avro implementation for serialize/deserialize

    Author: Nicola Ricciardi
    """

    def serialize(self, *, format_type: Optional[str] = None) -> Tuple[str, bytes]:
        if format_type is not None and format_type != AVRO_FORMAT_TYPE:
            raise ValueError(f"{format_type} != {AVRO_FORMAT_TYPE}")

        return AVRO_FORMAT_TYPE, AvroModel.serialize(self, serialization_type=AVRO_FORMAT_TYPE)

    @classmethod
    def deserialize(cls, format_type: str, serialized_data: bytes) -> Self:
        if format_type != AVRO_FORMAT_TYPE:
            raise ValueError(f"{format_type} != {AVRO_FORMAT_TYPE}")

        return AvroModel.deserialize.__func__(cls, serialized_data, serialization_type=AVRO_FORMAT_TYPE)
        # __func__ instead of __call__ because `AvroModel.deserialize` is a classmethod