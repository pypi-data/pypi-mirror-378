"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.utility.scripting._1939 import ScriptingSetup
    from mastapy._private.utility.scripting._1940 import UserDefinedPropertyKey
    from mastapy._private.utility.scripting._1941 import UserSpecifiedData
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.utility.scripting._1939": ["ScriptingSetup"],
        "_private.utility.scripting._1940": ["UserDefinedPropertyKey"],
        "_private.utility.scripting._1941": ["UserSpecifiedData"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ScriptingSetup",
    "UserDefinedPropertyKey",
    "UserSpecifiedData",
)
