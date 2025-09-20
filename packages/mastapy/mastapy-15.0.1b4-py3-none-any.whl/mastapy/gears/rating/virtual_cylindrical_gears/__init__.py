"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.rating.virtual_cylindrical_gears._470 import (
        BevelVirtualCylindricalGearISO10300MethodB2,
    )
    from mastapy._private.gears.rating.virtual_cylindrical_gears._471 import (
        BevelVirtualCylindricalGearSetISO10300MethodB1,
    )
    from mastapy._private.gears.rating.virtual_cylindrical_gears._472 import (
        BevelVirtualCylindricalGearSetISO10300MethodB2,
    )
    from mastapy._private.gears.rating.virtual_cylindrical_gears._473 import (
        HypoidVirtualCylindricalGearISO10300MethodB2,
    )
    from mastapy._private.gears.rating.virtual_cylindrical_gears._474 import (
        HypoidVirtualCylindricalGearSetISO10300MethodB1,
    )
    from mastapy._private.gears.rating.virtual_cylindrical_gears._475 import (
        HypoidVirtualCylindricalGearSetISO10300MethodB2,
    )
    from mastapy._private.gears.rating.virtual_cylindrical_gears._476 import (
        KlingelnbergHypoidVirtualCylindricalGear,
    )
    from mastapy._private.gears.rating.virtual_cylindrical_gears._477 import (
        KlingelnbergSpiralBevelVirtualCylindricalGear,
    )
    from mastapy._private.gears.rating.virtual_cylindrical_gears._478 import (
        KlingelnbergVirtualCylindricalGear,
    )
    from mastapy._private.gears.rating.virtual_cylindrical_gears._479 import (
        KlingelnbergVirtualCylindricalGearSet,
    )
    from mastapy._private.gears.rating.virtual_cylindrical_gears._480 import (
        VirtualCylindricalGear,
    )
    from mastapy._private.gears.rating.virtual_cylindrical_gears._481 import (
        VirtualCylindricalGearBasic,
    )
    from mastapy._private.gears.rating.virtual_cylindrical_gears._482 import (
        VirtualCylindricalGearISO10300MethodB1,
    )
    from mastapy._private.gears.rating.virtual_cylindrical_gears._483 import (
        VirtualCylindricalGearISO10300MethodB2,
    )
    from mastapy._private.gears.rating.virtual_cylindrical_gears._484 import (
        VirtualCylindricalGearSet,
    )
    from mastapy._private.gears.rating.virtual_cylindrical_gears._485 import (
        VirtualCylindricalGearSetISO10300MethodB1,
    )
    from mastapy._private.gears.rating.virtual_cylindrical_gears._486 import (
        VirtualCylindricalGearSetISO10300MethodB2,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.rating.virtual_cylindrical_gears._470": [
            "BevelVirtualCylindricalGearISO10300MethodB2"
        ],
        "_private.gears.rating.virtual_cylindrical_gears._471": [
            "BevelVirtualCylindricalGearSetISO10300MethodB1"
        ],
        "_private.gears.rating.virtual_cylindrical_gears._472": [
            "BevelVirtualCylindricalGearSetISO10300MethodB2"
        ],
        "_private.gears.rating.virtual_cylindrical_gears._473": [
            "HypoidVirtualCylindricalGearISO10300MethodB2"
        ],
        "_private.gears.rating.virtual_cylindrical_gears._474": [
            "HypoidVirtualCylindricalGearSetISO10300MethodB1"
        ],
        "_private.gears.rating.virtual_cylindrical_gears._475": [
            "HypoidVirtualCylindricalGearSetISO10300MethodB2"
        ],
        "_private.gears.rating.virtual_cylindrical_gears._476": [
            "KlingelnbergHypoidVirtualCylindricalGear"
        ],
        "_private.gears.rating.virtual_cylindrical_gears._477": [
            "KlingelnbergSpiralBevelVirtualCylindricalGear"
        ],
        "_private.gears.rating.virtual_cylindrical_gears._478": [
            "KlingelnbergVirtualCylindricalGear"
        ],
        "_private.gears.rating.virtual_cylindrical_gears._479": [
            "KlingelnbergVirtualCylindricalGearSet"
        ],
        "_private.gears.rating.virtual_cylindrical_gears._480": [
            "VirtualCylindricalGear"
        ],
        "_private.gears.rating.virtual_cylindrical_gears._481": [
            "VirtualCylindricalGearBasic"
        ],
        "_private.gears.rating.virtual_cylindrical_gears._482": [
            "VirtualCylindricalGearISO10300MethodB1"
        ],
        "_private.gears.rating.virtual_cylindrical_gears._483": [
            "VirtualCylindricalGearISO10300MethodB2"
        ],
        "_private.gears.rating.virtual_cylindrical_gears._484": [
            "VirtualCylindricalGearSet"
        ],
        "_private.gears.rating.virtual_cylindrical_gears._485": [
            "VirtualCylindricalGearSetISO10300MethodB1"
        ],
        "_private.gears.rating.virtual_cylindrical_gears._486": [
            "VirtualCylindricalGearSetISO10300MethodB2"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "BevelVirtualCylindricalGearISO10300MethodB2",
    "BevelVirtualCylindricalGearSetISO10300MethodB1",
    "BevelVirtualCylindricalGearSetISO10300MethodB2",
    "HypoidVirtualCylindricalGearISO10300MethodB2",
    "HypoidVirtualCylindricalGearSetISO10300MethodB1",
    "HypoidVirtualCylindricalGearSetISO10300MethodB2",
    "KlingelnbergHypoidVirtualCylindricalGear",
    "KlingelnbergSpiralBevelVirtualCylindricalGear",
    "KlingelnbergVirtualCylindricalGear",
    "KlingelnbergVirtualCylindricalGearSet",
    "VirtualCylindricalGear",
    "VirtualCylindricalGearBasic",
    "VirtualCylindricalGearISO10300MethodB1",
    "VirtualCylindricalGearISO10300MethodB2",
    "VirtualCylindricalGearSet",
    "VirtualCylindricalGearSetISO10300MethodB1",
    "VirtualCylindricalGearSetISO10300MethodB2",
)
