"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.bearings.roller_bearing_profiles._2135 import ProfileDataToUse
    from mastapy._private.bearings.roller_bearing_profiles._2136 import ProfileSet
    from mastapy._private.bearings.roller_bearing_profiles._2137 import ProfileToFit
    from mastapy._private.bearings.roller_bearing_profiles._2138 import (
        RollerBearingConicalProfile,
    )
    from mastapy._private.bearings.roller_bearing_profiles._2139 import (
        RollerBearingCrownedProfile,
    )
    from mastapy._private.bearings.roller_bearing_profiles._2140 import (
        RollerBearingDinLundbergProfile,
    )
    from mastapy._private.bearings.roller_bearing_profiles._2141 import (
        RollerBearingFlatProfile,
    )
    from mastapy._private.bearings.roller_bearing_profiles._2142 import (
        RollerBearingFujiwaraKawaseProfile,
    )
    from mastapy._private.bearings.roller_bearing_profiles._2143 import (
        RollerBearingJohnsGoharProfile,
    )
    from mastapy._private.bearings.roller_bearing_profiles._2144 import (
        RollerBearingLoadDependentProfile,
    )
    from mastapy._private.bearings.roller_bearing_profiles._2145 import (
        RollerBearingLundbergProfile,
    )
    from mastapy._private.bearings.roller_bearing_profiles._2146 import (
        RollerBearingProfile,
    )
    from mastapy._private.bearings.roller_bearing_profiles._2147 import (
        RollerBearingTangentialCrownedProfile,
    )
    from mastapy._private.bearings.roller_bearing_profiles._2148 import (
        RollerBearingUserSpecifiedProfile,
    )
    from mastapy._private.bearings.roller_bearing_profiles._2149 import (
        RollerRaceProfilePoint,
    )
    from mastapy._private.bearings.roller_bearing_profiles._2150 import (
        UserSpecifiedProfilePoint,
    )
    from mastapy._private.bearings.roller_bearing_profiles._2151 import (
        UserSpecifiedRollerRaceProfilePoint,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.bearings.roller_bearing_profiles._2135": ["ProfileDataToUse"],
        "_private.bearings.roller_bearing_profiles._2136": ["ProfileSet"],
        "_private.bearings.roller_bearing_profiles._2137": ["ProfileToFit"],
        "_private.bearings.roller_bearing_profiles._2138": [
            "RollerBearingConicalProfile"
        ],
        "_private.bearings.roller_bearing_profiles._2139": [
            "RollerBearingCrownedProfile"
        ],
        "_private.bearings.roller_bearing_profiles._2140": [
            "RollerBearingDinLundbergProfile"
        ],
        "_private.bearings.roller_bearing_profiles._2141": ["RollerBearingFlatProfile"],
        "_private.bearings.roller_bearing_profiles._2142": [
            "RollerBearingFujiwaraKawaseProfile"
        ],
        "_private.bearings.roller_bearing_profiles._2143": [
            "RollerBearingJohnsGoharProfile"
        ],
        "_private.bearings.roller_bearing_profiles._2144": [
            "RollerBearingLoadDependentProfile"
        ],
        "_private.bearings.roller_bearing_profiles._2145": [
            "RollerBearingLundbergProfile"
        ],
        "_private.bearings.roller_bearing_profiles._2146": ["RollerBearingProfile"],
        "_private.bearings.roller_bearing_profiles._2147": [
            "RollerBearingTangentialCrownedProfile"
        ],
        "_private.bearings.roller_bearing_profiles._2148": [
            "RollerBearingUserSpecifiedProfile"
        ],
        "_private.bearings.roller_bearing_profiles._2149": ["RollerRaceProfilePoint"],
        "_private.bearings.roller_bearing_profiles._2150": [
            "UserSpecifiedProfilePoint"
        ],
        "_private.bearings.roller_bearing_profiles._2151": [
            "UserSpecifiedRollerRaceProfilePoint"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ProfileDataToUse",
    "ProfileSet",
    "ProfileToFit",
    "RollerBearingConicalProfile",
    "RollerBearingCrownedProfile",
    "RollerBearingDinLundbergProfile",
    "RollerBearingFlatProfile",
    "RollerBearingFujiwaraKawaseProfile",
    "RollerBearingJohnsGoharProfile",
    "RollerBearingLoadDependentProfile",
    "RollerBearingLundbergProfile",
    "RollerBearingProfile",
    "RollerBearingTangentialCrownedProfile",
    "RollerBearingUserSpecifiedProfile",
    "RollerRaceProfilePoint",
    "UserSpecifiedProfilePoint",
    "UserSpecifiedRollerRaceProfilePoint",
)
