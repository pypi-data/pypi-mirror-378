"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.scripting._7910 import ApiEnumForAttribute
    from mastapy._private.scripting._7911 import ApiVersion
    from mastapy._private.scripting._7912 import SMTBitmap
    from mastapy._private.scripting._7914 import MastaPropertyAttribute
    from mastapy._private.scripting._7915 import PythonCommand
    from mastapy._private.scripting._7916 import ScriptingCommand
    from mastapy._private.scripting._7917 import ScriptingExecutionCommand
    from mastapy._private.scripting._7918 import ScriptingObjectCommand
    from mastapy._private.scripting._7919 import ApiVersioning
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.scripting._7910": ["ApiEnumForAttribute"],
        "_private.scripting._7911": ["ApiVersion"],
        "_private.scripting._7912": ["SMTBitmap"],
        "_private.scripting._7914": ["MastaPropertyAttribute"],
        "_private.scripting._7915": ["PythonCommand"],
        "_private.scripting._7916": ["ScriptingCommand"],
        "_private.scripting._7917": ["ScriptingExecutionCommand"],
        "_private.scripting._7918": ["ScriptingObjectCommand"],
        "_private.scripting._7919": ["ApiVersioning"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ApiEnumForAttribute",
    "ApiVersion",
    "SMTBitmap",
    "MastaPropertyAttribute",
    "PythonCommand",
    "ScriptingCommand",
    "ScriptingExecutionCommand",
    "ScriptingObjectCommand",
    "ApiVersioning",
)
