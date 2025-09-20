"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.utility.databases._2027 import ConnectionState
    from mastapy._private.utility.databases._2028 import Database
    from mastapy._private.utility.databases._2029 import DatabaseConnectionSettings
    from mastapy._private.utility.databases._2030 import DatabaseKey
    from mastapy._private.utility.databases._2031 import DatabaseSettings
    from mastapy._private.utility.databases._2032 import NamedDatabase
    from mastapy._private.utility.databases._2033 import NamedDatabaseItem
    from mastapy._private.utility.databases._2034 import NamedKey
    from mastapy._private.utility.databases._2035 import (
        NetworkDatabaseConnectionSettingsItem,
    )
    from mastapy._private.utility.databases._2036 import SQLDatabase
    from mastapy._private.utility.databases._2037 import VersionUpdater
    from mastapy._private.utility.databases._2038 import VersionUpdaterSelectableItem
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.utility.databases._2027": ["ConnectionState"],
        "_private.utility.databases._2028": ["Database"],
        "_private.utility.databases._2029": ["DatabaseConnectionSettings"],
        "_private.utility.databases._2030": ["DatabaseKey"],
        "_private.utility.databases._2031": ["DatabaseSettings"],
        "_private.utility.databases._2032": ["NamedDatabase"],
        "_private.utility.databases._2033": ["NamedDatabaseItem"],
        "_private.utility.databases._2034": ["NamedKey"],
        "_private.utility.databases._2035": ["NetworkDatabaseConnectionSettingsItem"],
        "_private.utility.databases._2036": ["SQLDatabase"],
        "_private.utility.databases._2037": ["VersionUpdater"],
        "_private.utility.databases._2038": ["VersionUpdaterSelectableItem"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ConnectionState",
    "Database",
    "DatabaseConnectionSettings",
    "DatabaseKey",
    "DatabaseSettings",
    "NamedDatabase",
    "NamedDatabaseItem",
    "NamedKey",
    "NetworkDatabaseConnectionSettingsItem",
    "SQLDatabase",
    "VersionUpdater",
    "VersionUpdaterSelectableItem",
)
