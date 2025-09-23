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
"""Testing utilities."""

from typing import Any, ClassVar

from . import _ffi_api
from .core import Object
from .dataclasses import c_class, field
from .registry import register_object


@register_object("testing.TestObjectBase")
class TestObjectBase(Object):
    """Test object base class."""


@register_object("testing.TestIntPair")
class TestIntPair(Object):
    """Test Int Pair."""

    def __init__(self, a: int, b: int) -> None:
        """Construct the object."""
        self.__ffi_init__(a, b)


@register_object("testing.TestObjectDerived")
class TestObjectDerived(TestObjectBase):
    """Test object derived class."""


def create_object(type_key: str, **kwargs: Any) -> Object:
    """Make an object by reflection.

    Parameters
    ----------
    type_key : str
        The type key of the object.
    kwargs : dict
        The keyword arguments to the object.

    Returns
    -------
    obj : object
        The created object.

    Note
    ----
    This function is only used for testing purposes and should
    not be used in other cases.

    """
    args = [type_key]
    for k, v in kwargs.items():
        args.append(k)
        args.append(v)
    return _ffi_api.MakeObjectFromPackedArgs(*args)


@c_class("testing.TestCxxClassBase")
class _TestCxxClassBase:
    v_i64: int
    v_i32: int
    not_field_1 = 1
    not_field_2: ClassVar[int] = 2

    def __init__(self, v_i64: int, v_i32: int) -> None:
        self.__ffi_init__(v_i64 + 1, v_i32 + 2)


@c_class("testing.TestCxxClassDerived")
class _TestCxxClassDerived(_TestCxxClassBase):
    v_f64: float
    v_f32: float = 8


@c_class("testing.TestCxxClassDerivedDerived")
class _TestCxxClassDerivedDerived(_TestCxxClassDerived):
    v_str: str = field(default_factory=lambda: "default")
    v_bool: bool
