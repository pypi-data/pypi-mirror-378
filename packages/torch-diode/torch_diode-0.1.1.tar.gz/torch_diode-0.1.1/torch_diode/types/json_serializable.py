import json
import logging
from collections import OrderedDict as CollectionsOrderedDict
from dataclasses import dataclass, fields
from typing import Any, get_args, get_origin, OrderedDict, TypeVar, Union

import msgpack
import torch
from typing_extensions import Self

logger = logging.getLogger(__name__)

T = TypeVar("T", bound="JSONSerializable")
LeafType = Union[
    None, bool, int, float, str, OrderedDict[str, Any], torch.dtype, list[Any]
]
JSONType = Union[T, LeafType]


@dataclass(kw_only=True)
class JSONSerializable:
    """
    This class implements a system similar to Pydantic Models for validating and serializing dataclasses.
    """

    # Incrementing version will invalidate all LUT entries, in the case of major perf update or
    # changes to the Ontology.
    version: int = 1

    @classmethod
    def from_dict(cls, inp: OrderedDict[str, Any] | str) -> Self:
        """
        Convert a dictionary representation of the object.
        """
        try:
            ret = OrderedDict()
            if isinstance(inp, str):
                raise NotImplementedError(
                    f"String representation not implemented for base {cls.__name__}"
                )
            for k, v in inp.items():
                v_type = cls.__dataclass_fields__[k].type
                if (
                    get_origin(v_type) is OrderedDict
                    or get_origin(v_type) is CollectionsOrderedDict
                ):
                    k1_type, v1_type = get_args(v_type)
                    if isinstance(k1_type, type) and issubclass(
                        k1_type, JSONSerializable
                    ):

                        def kp(tmpk: Any) -> Any:
                            # Keys are serialized as strings, so parse them back
                            if isinstance(tmpk, str):
                                return k1_type.parse(tmpk)
                            else:
                                return k1_type.from_dict(tmpk)

                        k_process = kp
                    else:

                        def k_process(tmpk: Any) -> Any:
                            return tmpk

                    if isinstance(v1_type, type) and issubclass(
                        v1_type, JSONSerializable
                    ):

                        def vp(tmpv: Any) -> Any:
                            return v1_type.from_dict(tmpv)

                        v_process = vp
                    else:

                        def v_process(tmpv: Any) -> Any:
                            return tmpv

                    v_new: Any = OrderedDict(
                        (k_process(key), v_process(val)) for key, val in v.items()
                    )

                elif get_origin(v_type) is list:
                    elem_type = get_args(v_type)[0]
                    if isinstance(elem_type, type) and issubclass(
                        elem_type, JSONSerializable
                    ):
                        v_new = [elem_type.from_dict(x) for x in v]
                    else:
                        v_new = v
                elif isinstance(v_type, type) and issubclass(v_type, JSONSerializable):
                    v_new = v_type.from_dict(v)
                else:
                    v_new = v
                ret[k] = v_new
            return cls(**ret)  # type: ignore[arg-type]
        except Exception as e:
            logger.error("Failed to deserialize %s from dict: %s", cls.__name__, e)
            raise ValueError(f"Malformed data for {cls.__name__}: {e}") from e

    def to_dict(self) -> OrderedDict[str, Any]:
        """
        Convert the object to a dictionary representation.
        Will be written to and from using json.dumps and json.loads.
        """
        # get the fields of the dataclass
        field_list = fields(self)
        # filter out the _ fields
        field_list = [field for field in field_list if not field.name.startswith("_")]
        # ensure the fields are sorted for consistent serialization
        field_list.sort(key=lambda x: x.name)
        ret: OrderedDict[str, Any] = OrderedDict()
        for field_obj in field_list:
            field_val = getattr(self, field_obj.name)
            if isinstance(field_val, JSONSerializable):
                ret[field_obj.name] = field_val.to_dict()
            elif isinstance(field_val, list):
                if len(field_val) == 0:
                    ret[field_obj.name] = []
                elif isinstance(field_val[0], JSONSerializable):
                    ret[field_obj.name] = [x.to_dict() for x in field_val]
                else:
                    ret[field_obj.name] = field_val
            elif isinstance(field_val, OrderedDict):
                tmp: OrderedDict[Any, Any] = OrderedDict()
                for k, v in field_val.items():
                    if isinstance(v, JSONSerializable):
                        new_v: Any = v.to_dict()
                    else:
                        new_v = v
                    if isinstance(k, JSONSerializable):
                        # Use string representation for JSONSerializable keys to maintain hashability
                        new_k: Any = str(k)
                    else:
                        new_k = k
                    tmp[new_k] = new_v
                ret[field_obj.name] = tmp
            else:
                ret[field_obj.name] = field_val
        return ret

    def __str__(self) -> str:
        """
        Return a string representation of the object.
        """
        return json.dumps(self.to_dict())

    @classmethod
    def parse(cls, string: str) -> Self:
        """
        Parse the string representaiton of the object. Only reqiured for leaf nodes.
        """
        raise NotImplementedError(
            f"String representation not implemented for base {cls.__name__}"
        )

    def to_msgpack(self) -> bytes:
        """
        Convert the object to MessagePack format.
        Returns bytes that can be written to a file or transmitted over a network.
        """
        try:
            # Convert to dict first, then make it MessagePack-compatible
            data_dict = self.to_dict()
            msgpack_compatible_dict = self._make_msgpack_compatible(data_dict)
            return msgpack.packb(msgpack_compatible_dict, use_bin_type=True)
        except Exception as e:
            logger.error(
                "Failed to serialize %s to MessagePack: %s", self.__class__.__name__, e
            )
            raise ValueError(
                f"Failed to serialize {self.__class__.__name__} to MessagePack: {e}"
            ) from e

    def _make_msgpack_compatible(self, obj: Any) -> Any:
        """
        Convert objects to MessagePack-compatible format.
        Recursively processes nested structures.
        """
        if isinstance(obj, torch.dtype):
            # Convert torch.dtype to string representation
            return {"__torch_dtype__": str(obj).split(".")[-1]}
        elif isinstance(obj, dict):
            return {k: self._make_msgpack_compatible(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._make_msgpack_compatible(item) for item in obj]
        else:
            return obj

    @classmethod
    def from_msgpack(cls, data: bytes) -> Self:
        """
        Create an object from MessagePack data.
        Takes bytes and returns an instance of the class.
        """
        try:
            decoded_dict = msgpack.unpackb(data, raw=False, strict_map_key=False)
            # Convert MessagePack-specific formats back to original objects
            restored_dict = cls._restore_from_msgpack(decoded_dict)
            return cls.from_dict(restored_dict)
        except Exception as e:
            logger.error(
                "Failed to deserialize %s from MessagePack: %s", cls.__name__, e
            )
            raise ValueError(
                f"Failed to deserialize {cls.__name__} from MessagePack: {e}"
            ) from e

    @classmethod
    def _restore_from_msgpack(cls, obj: Any) -> Any:
        """
        Restore objects from MessagePack-compatible format.
        Recursively processes nested structures.
        """
        if isinstance(obj, dict):
            # Check if this is a torch.dtype marker
            if len(obj) == 1 and "__torch_dtype__" in obj:
                dtype_name = obj["__torch_dtype__"]
                try:
                    return getattr(torch, dtype_name)
                except AttributeError:
                    raise ValueError(f"Invalid torch dtype: {dtype_name}")
            else:
                return {k: cls._restore_from_msgpack(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [cls._restore_from_msgpack(item) for item in obj]
        else:
            return obj

    def serialize_msgpack(self) -> bytes:
        """
        Serialize the object to MessagePack format.
        Alias for to_msgpack() for consistency with existing serialize() method.
        """
        return self.to_msgpack()

    @classmethod
    def deserialize_msgpack(cls, data: bytes) -> Self:
        """
        Deserialize an object from MessagePack format.
        Alias for from_msgpack() for consistency with existing deserialize() method.
        """
        return cls.from_msgpack(data)
