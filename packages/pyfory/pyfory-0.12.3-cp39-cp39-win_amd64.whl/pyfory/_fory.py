# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import enum
import logging
import os
from abc import ABC, abstractmethod
from typing import Union, Iterable, TypeVar

from pyfory.buffer import Buffer
from pyfory.resolver import (
    MapRefResolver,
    NoRefResolver,
    NULL_FLAG,
    NOT_NULL_VALUE_FLAG,
)
from pyfory.util import is_little_endian, set_bit, get_bit, clear_bit
from pyfory.type import TypeId

try:
    import numpy as np
except ImportError:
    np = None


logger = logging.getLogger(__name__)


MAGIC_NUMBER = 0x62D4
DEFAULT_DYNAMIC_WRITE_META_STR_ID = -1
DYNAMIC_TYPE_ID = -1
USE_TYPE_NAME = 0
USE_TYPE_ID = 1
# preserve 0 as flag for type id not set in TypeInfo`
NO_TYPE_ID = 0
INT64_TYPE_ID = TypeId.INT64
FLOAT64_TYPE_ID = TypeId.FLOAT64
BOOL_TYPE_ID = TypeId.BOOL
STRING_TYPE_ID = TypeId.STRING
# `NOT_NULL_VALUE_FLAG` + `TYPE_ID << 1` in little-endian order
NOT_NULL_INT64_FLAG = NOT_NULL_VALUE_FLAG & 0b11111111 | (INT64_TYPE_ID << 8)
NOT_NULL_FLOAT64_FLAG = NOT_NULL_VALUE_FLAG & 0b11111111 | (FLOAT64_TYPE_ID << 8)
NOT_NULL_BOOL_FLAG = NOT_NULL_VALUE_FLAG & 0b11111111 | (BOOL_TYPE_ID << 8)
NOT_NULL_STRING_FLAG = NOT_NULL_VALUE_FLAG & 0b11111111 | (STRING_TYPE_ID << 8)
SMALL_STRING_THRESHOLD = 16


class Language(enum.Enum):
    XLANG = 0
    JAVA = 1
    PYTHON = 2
    CPP = 3
    GO = 4
    JAVA_SCRIPT = 5
    RUST = 6
    DART = 7


class BufferObject(ABC):
    """
    Fory binary representation of an object.
    Note: This class is used for zero-copy out-of-band serialization and shouldn't
     be used for any other cases.
    """

    @abstractmethod
    def total_bytes(self) -> int:
        """total size for serialized bytes of an object"""

    @abstractmethod
    def write_to(self, buffer: "Buffer"):
        """Write serialized object to a buffer."""

    @abstractmethod
    def to_buffer(self) -> "Buffer":
        """Write serialized data as Buffer."""


class Fory:
    __slots__ = (
        "language",
        "is_py",
        "ref_tracking",
        "ref_resolver",
        "type_resolver",
        "require_type_registration",
        "buffer",
        "_buffer_callback",
        "_buffers",
        "metastring_resolver",
        "_unsupported_callback",
        "_unsupported_objects",
        "_peer_language",
        "max_depth",
        "depth",
    )

    def __init__(
        self,
        language=Language.PYTHON,
        ref_tracking: bool = False,
        require_type_registration: bool = True,
        max_depth: int = 50,
    ):
        """
        :param require_type_registration:
         Whether to require registering types for serialization, enabled by default.
          If disabled, unknown insecure types can be deserialized, which can be
          insecure and cause remote code execution attack if the types
          `__new__`/`__init__`/`__eq__`/`__hash__` method contain malicious code.
          Do not disable type registration if you can't ensure your environment are
          *indeed secure*. We are not responsible for security risks if
          you disable this option.
        :param max_depth:
         The maximum depth of the deserialization data.
         If the depth exceeds the maximum depth, an exception will be raised.
         The default value is 50.
        """
        self.language = language
        self.is_py = language == Language.PYTHON
        self.require_type_registration = _ENABLE_TYPE_REGISTRATION_FORCIBLY or require_type_registration
        self.ref_tracking = ref_tracking
        if self.ref_tracking:
            self.ref_resolver = MapRefResolver()
        else:
            self.ref_resolver = NoRefResolver()
        from pyfory._serialization import MetaStringResolver
        from pyfory._registry import TypeResolver

        self.metastring_resolver = MetaStringResolver()
        self.type_resolver = TypeResolver(self)
        self.type_resolver.initialize()
        self.buffer = Buffer.allocate(32)
        self._buffer_callback = None
        self._buffers = None
        self._unsupported_callback = None
        self._unsupported_objects = None
        self._peer_language = None
        self.max_depth = max_depth
        self.depth = 0

    def register(
        self,
        cls: Union[type, TypeVar],
        *,
        type_id: int = None,
        namespace: str = None,
        typename: str = None,
        serializer=None,
    ):
        self.register_type(cls, type_id=type_id, namespace=namespace, typename=typename, serializer=serializer)

    # `Union[type, TypeVar]` is not supported in py3.6
    def register_type(
        self,
        cls: Union[type, TypeVar],
        *,
        type_id: int = None,
        namespace: str = None,
        typename: str = None,
        serializer=None,
    ):
        return self.type_resolver.register_type(
            cls,
            type_id=type_id,
            namespace=namespace,
            typename=typename,
            serializer=serializer,
        )

    def register_serializer(self, cls: type, serializer):
        self.type_resolver.register_serializer(cls, serializer)

    def serialize(
        self,
        obj,
        buffer: Buffer = None,
        buffer_callback=None,
        unsupported_callback=None,
    ) -> Union[Buffer, bytes]:
        try:
            return self._serialize(
                obj,
                buffer,
                buffer_callback=buffer_callback,
                unsupported_callback=unsupported_callback,
            )
        finally:
            self.reset_write()

    def _serialize(
        self,
        obj,
        buffer: Buffer = None,
        buffer_callback=None,
        unsupported_callback=None,
    ) -> Union[Buffer, bytes]:
        self._buffer_callback = buffer_callback
        self._unsupported_callback = unsupported_callback
        if buffer is None:
            self.buffer.writer_index = 0
            buffer = self.buffer
        if self.language == Language.XLANG:
            buffer.write_int16(MAGIC_NUMBER)
        mask_index = buffer.writer_index
        # 1byte used for bit mask
        buffer.grow(1)
        buffer.writer_index = mask_index + 1
        if obj is None:
            set_bit(buffer, mask_index, 0)
        else:
            clear_bit(buffer, mask_index, 0)
        # set endian
        if is_little_endian:
            set_bit(buffer, mask_index, 1)
        else:
            clear_bit(buffer, mask_index, 1)

        if self.language == Language.XLANG:
            # set reader as x_lang.
            set_bit(buffer, mask_index, 2)
            # set writer language.
            buffer.write_int8(Language.PYTHON.value)
        else:
            # set reader as native.
            clear_bit(buffer, mask_index, 2)
        if self._buffer_callback is not None:
            set_bit(buffer, mask_index, 3)
        else:
            clear_bit(buffer, mask_index, 3)
        if self.language == Language.PYTHON:
            self.serialize_ref(buffer, obj)
        else:
            self.xserialize_ref(buffer, obj)
        self.reset_write()
        if buffer is not self.buffer:
            return buffer
        else:
            return buffer.to_bytes(0, buffer.writer_index)

    def serialize_ref(self, buffer, obj, typeinfo=None):
        cls = type(obj)
        if cls is str:
            buffer.write_int16(NOT_NULL_STRING_FLAG)
            buffer.write_string(obj)
            return
        elif cls is int:
            buffer.write_int16(NOT_NULL_INT64_FLAG)
            buffer.write_varint64(obj)
            return
        elif cls is bool:
            buffer.write_int16(NOT_NULL_BOOL_FLAG)
            buffer.write_bool(obj)
            return
        if self.ref_resolver.write_ref_or_null(buffer, obj):
            return
        if typeinfo is None:
            typeinfo = self.type_resolver.get_typeinfo(cls)
        self.type_resolver.write_typeinfo(buffer, typeinfo)
        typeinfo.serializer.write(buffer, obj)

    def serialize_nonref(self, buffer, obj):
        cls = type(obj)
        if cls is str:
            buffer.write_varuint32(STRING_TYPE_ID)
            buffer.write_string(obj)
            return
        elif cls is int:
            buffer.write_varuint32(INT64_TYPE_ID)
            buffer.write_varint64(obj)
            return
        elif cls is bool:
            buffer.write_varuint32(BOOL_TYPE_ID)
            buffer.write_bool(obj)
            return
        else:
            typeinfo = self.type_resolver.get_typeinfo(cls)
            self.type_resolver.write_typeinfo(buffer, typeinfo)
            typeinfo.serializer.write(buffer, obj)

    def xserialize_ref(self, buffer, obj, serializer=None):
        if serializer is None or serializer.need_to_write_ref:
            if not self.ref_resolver.write_ref_or_null(buffer, obj):
                self.xserialize_nonref(buffer, obj, serializer=serializer)
        else:
            if obj is None:
                buffer.write_int8(NULL_FLAG)
            else:
                buffer.write_int8(NOT_NULL_VALUE_FLAG)
                self.xserialize_nonref(buffer, obj, serializer=serializer)

    def xserialize_nonref(self, buffer, obj, serializer=None):
        if serializer is not None:
            serializer.xwrite(buffer, obj)
            return
        cls = type(obj)
        typeinfo = self.type_resolver.get_typeinfo(cls)
        self.type_resolver.write_typeinfo(buffer, typeinfo)
        typeinfo.serializer.xwrite(buffer, obj)

    def deserialize(
        self,
        buffer: Union[Buffer, bytes],
        buffers: Iterable = None,
        unsupported_objects: Iterable = None,
    ):
        try:
            return self._deserialize(buffer, buffers, unsupported_objects)
        finally:
            self.reset_read()

    def _deserialize(
        self,
        buffer: Union[Buffer, bytes],
        buffers: Iterable = None,
        unsupported_objects: Iterable = None,
    ):
        if isinstance(buffer, bytes):
            buffer = Buffer(buffer)
        if unsupported_objects is not None:
            self._unsupported_objects = iter(unsupported_objects)
        if self.language == Language.XLANG:
            magic_numer = buffer.read_int16()
            assert magic_numer == MAGIC_NUMBER, (
                f"The fory xlang serialization must start with magic number {hex(MAGIC_NUMBER)}. "
                "Please check whether the serialization is based on the xlang protocol and the data didn't corrupt."
            )
        reader_index = buffer.reader_index
        buffer.reader_index = reader_index + 1
        if get_bit(buffer, reader_index, 0):
            return None
        is_little_endian_ = get_bit(buffer, reader_index, 1)
        assert is_little_endian_, "Big endian is not supported for now, please ensure peer machine is little endian."
        is_target_x_lang = get_bit(buffer, reader_index, 2)
        if is_target_x_lang:
            self._peer_language = Language(buffer.read_int8())
        else:
            self._peer_language = Language.PYTHON
        is_out_of_band_serialization_enabled = get_bit(buffer, reader_index, 3)
        if is_out_of_band_serialization_enabled:
            assert buffers is not None, "buffers shouldn't be null when the serialized stream is produced with buffer_callback not null."
            self._buffers = iter(buffers)
        else:
            assert buffers is None, "buffers should be null when the serialized stream is produced with buffer_callback null."
        if is_target_x_lang:
            obj = self.xdeserialize_ref(buffer)
        else:
            obj = self.deserialize_ref(buffer)
        return obj

    def deserialize_ref(self, buffer):
        ref_resolver = self.ref_resolver
        ref_id = ref_resolver.try_preserve_ref_id(buffer)
        # indicates that the object is first read.
        if ref_id >= NOT_NULL_VALUE_FLAG:
            typeinfo = self.type_resolver.read_typeinfo(buffer)
            self.depth += 1
            if self.depth > self.max_depth:
                self.throw_depth_limit_exceeded_exception()
            o = typeinfo.serializer.read(buffer)
            self.depth -= 1
            ref_resolver.set_read_object(ref_id, o)
            return o
        else:
            return ref_resolver.get_read_object()

    def deserialize_nonref(self, buffer):
        """Deserialize not-null and non-reference object from buffer."""
        typeinfo = self.type_resolver.read_typeinfo(buffer)
        self.depth += 1
        if self.depth > self.max_depth:
            self.throw_depth_limit_exceeded_exception()
        o = typeinfo.serializer.read(buffer)
        self.depth -= 1
        return o

    def xdeserialize_ref(self, buffer, serializer=None):
        if serializer is None or serializer.need_to_write_ref:
            ref_resolver = self.ref_resolver
            ref_id = ref_resolver.try_preserve_ref_id(buffer)
            # indicates that the object is first read.
            if ref_id >= NOT_NULL_VALUE_FLAG:
                o = self.xdeserialize_nonref(buffer, serializer=serializer)
                ref_resolver.set_read_object(ref_id, o)
                return o
            else:
                return ref_resolver.get_read_object()
        head_flag = buffer.read_int8()
        if head_flag == NULL_FLAG:
            return None
        return self.xdeserialize_nonref(buffer, serializer=serializer)

    def xdeserialize_nonref(self, buffer, serializer=None):
        if serializer is None:
            serializer = self.type_resolver.read_typeinfo(buffer).serializer
        self.depth += 1
        if self.depth > self.max_depth:
            self.throw_depth_limit_exceeded_exception()
        o = serializer.xread(buffer)
        self.depth -= 1
        return o

    def write_buffer_object(self, buffer, buffer_object: BufferObject):
        if self._buffer_callback is None or self._buffer_callback(buffer_object):
            buffer.write_bool(True)
            size = buffer_object.total_bytes()
            # writer length.
            buffer.write_varuint32(size)
            writer_index = buffer.writer_index
            buffer.ensure(writer_index + size)
            buf = buffer.slice(buffer.writer_index, size)
            buffer_object.write_to(buf)
            buffer.writer_index += size
        else:
            buffer.write_bool(False)

    def read_buffer_object(self, buffer) -> Buffer:
        in_band = buffer.read_bool()
        if in_band:
            size = buffer.read_varuint32()
            buf = buffer.slice(buffer.reader_index, size)
            buffer.reader_index += size
            return buf
        else:
            assert self._buffers is not None
            return next(self._buffers)

    def handle_unsupported_write(self, buffer, obj):
        if self._unsupported_callback is None or self._unsupported_callback(obj):
            raise NotImplementedError(f"{type(obj)} is not supported for write")

    def handle_unsupported_read(self, buffer):
        assert self._unsupported_objects is not None
        return next(self._unsupported_objects)

    def write_ref_pyobject(self, buffer, value, typeinfo=None):
        if self.ref_resolver.write_ref_or_null(buffer, value):
            return
        if typeinfo is None:
            typeinfo = self.type_resolver.get_typeinfo(type(value))
        self.type_resolver.write_typeinfo(buffer, typeinfo)
        typeinfo.serializer.write(buffer, value)

    def read_ref_pyobject(self, buffer):
        return self.deserialize_ref(buffer)

    def inc_depth(self):
        self.depth += 1
        if self.depth > self.max_depth:
            self.throw_depth_limit_exceeded_exception()

    def dec_depth(self):
        self.depth -= 1

    def throw_depth_limit_exceeded_exception(self):
        raise Exception(
            f"Read depth exceed max depth: {self.depth}, the deserialization data may be malicious. If it's not malicious, "
            "please increase max read depth by Fory(..., max_depth=...)"
        )

    def reset_write(self):
        self.ref_resolver.reset_write()
        self.type_resolver.reset_write()
        self.metastring_resolver.reset_write()
        self._buffer_callback = None
        self._unsupported_callback = None

    def reset_read(self):
        self.depth = 0
        self.ref_resolver.reset_read()
        self.type_resolver.reset_read()
        self.metastring_resolver.reset_write()
        self._buffers = None
        self._unsupported_objects = None

    def reset(self):
        self.reset_write()
        self.reset_read()


class SerializationContext:
    """
    A context is used to add some context-related information, so that the
    serializers can setup relation between serializing different objects.
    The context will be reset after finished serializing/deserializing the
    object tree.
    """

    __slots__ = ("objects",)

    def __init__(self):
        self.objects = dict()

    def add(self, key, obj):
        self.objects[id(key)] = obj

    def __contains__(self, key):
        return id(key) in self.objects

    def __getitem__(self, key):
        return self.objects[id(key)]

    def get(self, key):
        return self.objects.get(id(key))

    def reset(self):
        if len(self.objects) > 0:
            self.objects.clear()


_ENABLE_TYPE_REGISTRATION_FORCIBLY = os.getenv("ENABLE_TYPE_REGISTRATION_FORCIBLY", "0") in {
    "1",
    "true",
}
