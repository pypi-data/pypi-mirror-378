"""ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.gears.gear_set_pareto_optimiser import _1030

_PARETO_CYLINDRICAL_GEAR_SET_DUTY_CYCLE_OPTIMISATION_STRATEGY_DATABASE = (
    python_net_import(
        "SMT.MastaAPI.Gears.GearSetParetoOptimiser",
        "ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase",
    )
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.math_utility.optimisation import _1728, _1741
    from mastapy._private.utility.databases import _2028, _2032, _2036

    Self = TypeVar(
        "Self", bound="ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase"
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase._Cast_ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase:
    """Special nested class for casting ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase to subclasses."""

    __parent__: "ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase"

    @property
    def pareto_cylindrical_rating_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1030.ParetoCylindricalRatingOptimisationStrategyDatabase":
        return self.__parent__._cast(
            _1030.ParetoCylindricalRatingOptimisationStrategyDatabase
        )

    @property
    def pareto_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1741.ParetoOptimisationStrategyDatabase":
        from mastapy._private.math_utility.optimisation import _1741

        return self.__parent__._cast(_1741.ParetoOptimisationStrategyDatabase)

    @property
    def design_space_search_strategy_database(
        self: "CastSelf",
    ) -> "_1728.DesignSpaceSearchStrategyDatabase":
        from mastapy._private.math_utility.optimisation import _1728

        return self.__parent__._cast(_1728.DesignSpaceSearchStrategyDatabase)

    @property
    def named_database(self: "CastSelf") -> "_2032.NamedDatabase":
        pass

        from mastapy._private.utility.databases import _2032

        return self.__parent__._cast(_2032.NamedDatabase)

    @property
    def sql_database(self: "CastSelf") -> "_2036.SQLDatabase":
        pass

        from mastapy._private.utility.databases import _2036

        return self.__parent__._cast(_2036.SQLDatabase)

    @property
    def database(self: "CastSelf") -> "_2028.Database":
        pass

        from mastapy._private.utility.databases import _2028

        return self.__parent__._cast(_2028.Database)

    @property
    def pareto_cylindrical_gear_set_duty_cycle_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase":
        return self.__parent__

    def __getattr__(self: "CastSelf", name: str) -> "Any":
        try:
            return self.__getattribute__(name)
        except AttributeError:
            class_name = utility.camel(name)
            raise CastException(
                f'Detected an invalid cast. Cannot cast to type "{class_name}"'
            ) from None


@extended_dataclass(frozen=True, slots=True, weakref_slot=True, eq=False)
class ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase(
    _1030.ParetoCylindricalRatingOptimisationStrategyDatabase
):
    """ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _PARETO_CYLINDRICAL_GEAR_SET_DUTY_CYCLE_OPTIMISATION_STRATEGY_DATABASE
    )

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase":
        """Cast to another type.

        Returns:
            _Cast_ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase
        """
        return _Cast_ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase(self)
