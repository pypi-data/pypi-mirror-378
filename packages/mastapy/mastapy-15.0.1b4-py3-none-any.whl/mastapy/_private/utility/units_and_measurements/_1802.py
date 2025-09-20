"""MeasurementBase"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private import _0
from mastapy._private._internal import constructor, conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.implicit import list_with_selected_item, overridable
from mastapy._private._internal.list_with_selected_item import (
    promote_to_list_with_selected_item,
)
from mastapy._private._internal.overridable_constructor import _unpack_overridable
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.sentinels import ListWithSelectedItem_None
from mastapy._private._internal.type_enforcement import enforce_parameter_types
from mastapy._private.utility.units_and_measurements import _1807

_MEASUREMENT_BASE = python_net_import(
    "SMT.MastaAPI.Utility.UnitsAndMeasurements", "MeasurementBase"
)

if TYPE_CHECKING:
    from typing import Any, List, Tuple, Type, TypeVar, Union

    from mastapy._private._internal.typing import PathLike
    from mastapy._private.utility import _1794
    from mastapy._private.utility.units_and_measurements.measurements import (
        _1809,
        _1810,
        _1811,
        _1812,
        _1813,
        _1814,
        _1815,
        _1816,
        _1817,
        _1818,
        _1819,
        _1820,
        _1821,
        _1822,
        _1823,
        _1824,
        _1825,
        _1826,
        _1827,
        _1828,
        _1829,
        _1830,
        _1831,
        _1832,
        _1833,
        _1834,
        _1835,
        _1836,
        _1837,
        _1838,
        _1839,
        _1840,
        _1841,
        _1842,
        _1843,
        _1844,
        _1845,
        _1846,
        _1847,
        _1848,
        _1849,
        _1850,
        _1851,
        _1852,
        _1853,
        _1854,
        _1855,
        _1856,
        _1857,
        _1858,
        _1859,
        _1860,
        _1861,
        _1862,
        _1863,
        _1864,
        _1865,
        _1866,
        _1867,
        _1868,
        _1869,
        _1870,
        _1871,
        _1872,
        _1873,
        _1874,
        _1875,
        _1876,
        _1877,
        _1878,
        _1879,
        _1880,
        _1881,
        _1882,
        _1883,
        _1884,
        _1885,
        _1886,
        _1887,
        _1888,
        _1889,
        _1890,
        _1891,
        _1892,
        _1893,
        _1894,
        _1895,
        _1896,
        _1897,
        _1898,
        _1899,
        _1900,
        _1901,
        _1902,
        _1903,
        _1904,
        _1905,
        _1906,
        _1907,
        _1908,
        _1909,
        _1910,
        _1911,
        _1912,
        _1913,
        _1914,
        _1915,
        _1916,
        _1917,
        _1918,
        _1919,
        _1920,
        _1921,
        _1922,
        _1923,
        _1924,
        _1925,
        _1926,
        _1927,
        _1928,
        _1929,
        _1930,
        _1931,
        _1932,
        _1933,
        _1934,
        _1935,
        _1936,
        _1937,
        _1938,
    )

    Self = TypeVar("Self", bound="MeasurementBase")
    CastSelf = TypeVar("CastSelf", bound="MeasurementBase._Cast_MeasurementBase")


__docformat__ = "restructuredtext en"
__all__ = ("MeasurementBase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_MeasurementBase:
    """Special nested class for casting MeasurementBase to subclasses."""

    __parent__: "MeasurementBase"

    @property
    def acceleration(self: "CastSelf") -> "_1809.Acceleration":
        from mastapy._private.utility.units_and_measurements.measurements import _1809

        return self.__parent__._cast(_1809.Acceleration)

    @property
    def angle(self: "CastSelf") -> "_1810.Angle":
        from mastapy._private.utility.units_and_measurements.measurements import _1810

        return self.__parent__._cast(_1810.Angle)

    @property
    def angle_per_unit_temperature(self: "CastSelf") -> "_1811.AnglePerUnitTemperature":
        from mastapy._private.utility.units_and_measurements.measurements import _1811

        return self.__parent__._cast(_1811.AnglePerUnitTemperature)

    @property
    def angle_small(self: "CastSelf") -> "_1812.AngleSmall":
        from mastapy._private.utility.units_and_measurements.measurements import _1812

        return self.__parent__._cast(_1812.AngleSmall)

    @property
    def angle_very_small(self: "CastSelf") -> "_1813.AngleVerySmall":
        from mastapy._private.utility.units_and_measurements.measurements import _1813

        return self.__parent__._cast(_1813.AngleVerySmall)

    @property
    def angular_acceleration(self: "CastSelf") -> "_1814.AngularAcceleration":
        from mastapy._private.utility.units_and_measurements.measurements import _1814

        return self.__parent__._cast(_1814.AngularAcceleration)

    @property
    def angular_compliance(self: "CastSelf") -> "_1815.AngularCompliance":
        from mastapy._private.utility.units_and_measurements.measurements import _1815

        return self.__parent__._cast(_1815.AngularCompliance)

    @property
    def angular_jerk(self: "CastSelf") -> "_1816.AngularJerk":
        from mastapy._private.utility.units_and_measurements.measurements import _1816

        return self.__parent__._cast(_1816.AngularJerk)

    @property
    def angular_stiffness(self: "CastSelf") -> "_1817.AngularStiffness":
        from mastapy._private.utility.units_and_measurements.measurements import _1817

        return self.__parent__._cast(_1817.AngularStiffness)

    @property
    def angular_velocity(self: "CastSelf") -> "_1818.AngularVelocity":
        from mastapy._private.utility.units_and_measurements.measurements import _1818

        return self.__parent__._cast(_1818.AngularVelocity)

    @property
    def area(self: "CastSelf") -> "_1819.Area":
        from mastapy._private.utility.units_and_measurements.measurements import _1819

        return self.__parent__._cast(_1819.Area)

    @property
    def area_small(self: "CastSelf") -> "_1820.AreaSmall":
        from mastapy._private.utility.units_and_measurements.measurements import _1820

        return self.__parent__._cast(_1820.AreaSmall)

    @property
    def carbon_emission_factor(self: "CastSelf") -> "_1821.CarbonEmissionFactor":
        from mastapy._private.utility.units_and_measurements.measurements import _1821

        return self.__parent__._cast(_1821.CarbonEmissionFactor)

    @property
    def current_density(self: "CastSelf") -> "_1822.CurrentDensity":
        from mastapy._private.utility.units_and_measurements.measurements import _1822

        return self.__parent__._cast(_1822.CurrentDensity)

    @property
    def current_per_length(self: "CastSelf") -> "_1823.CurrentPerLength":
        from mastapy._private.utility.units_and_measurements.measurements import _1823

        return self.__parent__._cast(_1823.CurrentPerLength)

    @property
    def cycles(self: "CastSelf") -> "_1824.Cycles":
        from mastapy._private.utility.units_and_measurements.measurements import _1824

        return self.__parent__._cast(_1824.Cycles)

    @property
    def damage(self: "CastSelf") -> "_1825.Damage":
        from mastapy._private.utility.units_and_measurements.measurements import _1825

        return self.__parent__._cast(_1825.Damage)

    @property
    def damage_rate(self: "CastSelf") -> "_1826.DamageRate":
        from mastapy._private.utility.units_and_measurements.measurements import _1826

        return self.__parent__._cast(_1826.DamageRate)

    @property
    def data_size(self: "CastSelf") -> "_1827.DataSize":
        from mastapy._private.utility.units_and_measurements.measurements import _1827

        return self.__parent__._cast(_1827.DataSize)

    @property
    def decibel(self: "CastSelf") -> "_1828.Decibel":
        from mastapy._private.utility.units_and_measurements.measurements import _1828

        return self.__parent__._cast(_1828.Decibel)

    @property
    def density(self: "CastSelf") -> "_1829.Density":
        from mastapy._private.utility.units_and_measurements.measurements import _1829

        return self.__parent__._cast(_1829.Density)

    @property
    def electrical_resistance(self: "CastSelf") -> "_1830.ElectricalResistance":
        from mastapy._private.utility.units_and_measurements.measurements import _1830

        return self.__parent__._cast(_1830.ElectricalResistance)

    @property
    def electrical_resistivity(self: "CastSelf") -> "_1831.ElectricalResistivity":
        from mastapy._private.utility.units_and_measurements.measurements import _1831

        return self.__parent__._cast(_1831.ElectricalResistivity)

    @property
    def electric_current(self: "CastSelf") -> "_1832.ElectricCurrent":
        from mastapy._private.utility.units_and_measurements.measurements import _1832

        return self.__parent__._cast(_1832.ElectricCurrent)

    @property
    def energy(self: "CastSelf") -> "_1833.Energy":
        from mastapy._private.utility.units_and_measurements.measurements import _1833

        return self.__parent__._cast(_1833.Energy)

    @property
    def energy_per_unit_area(self: "CastSelf") -> "_1834.EnergyPerUnitArea":
        from mastapy._private.utility.units_and_measurements.measurements import _1834

        return self.__parent__._cast(_1834.EnergyPerUnitArea)

    @property
    def energy_per_unit_area_small(self: "CastSelf") -> "_1835.EnergyPerUnitAreaSmall":
        from mastapy._private.utility.units_and_measurements.measurements import _1835

        return self.__parent__._cast(_1835.EnergyPerUnitAreaSmall)

    @property
    def energy_small(self: "CastSelf") -> "_1836.EnergySmall":
        from mastapy._private.utility.units_and_measurements.measurements import _1836

        return self.__parent__._cast(_1836.EnergySmall)

    @property
    def enum(self: "CastSelf") -> "_1837.Enum":
        from mastapy._private.utility.units_and_measurements.measurements import _1837

        return self.__parent__._cast(_1837.Enum)

    @property
    def flow_rate(self: "CastSelf") -> "_1838.FlowRate":
        from mastapy._private.utility.units_and_measurements.measurements import _1838

        return self.__parent__._cast(_1838.FlowRate)

    @property
    def flow_resistance(self: "CastSelf") -> "_1839.FlowResistance":
        from mastapy._private.utility.units_and_measurements.measurements import _1839

        return self.__parent__._cast(_1839.FlowResistance)

    @property
    def force(self: "CastSelf") -> "_1840.Force":
        from mastapy._private.utility.units_and_measurements.measurements import _1840

        return self.__parent__._cast(_1840.Force)

    @property
    def force_per_unit_length(self: "CastSelf") -> "_1841.ForcePerUnitLength":
        from mastapy._private.utility.units_and_measurements.measurements import _1841

        return self.__parent__._cast(_1841.ForcePerUnitLength)

    @property
    def force_per_unit_pressure(self: "CastSelf") -> "_1842.ForcePerUnitPressure":
        from mastapy._private.utility.units_and_measurements.measurements import _1842

        return self.__parent__._cast(_1842.ForcePerUnitPressure)

    @property
    def force_per_unit_temperature(self: "CastSelf") -> "_1843.ForcePerUnitTemperature":
        from mastapy._private.utility.units_and_measurements.measurements import _1843

        return self.__parent__._cast(_1843.ForcePerUnitTemperature)

    @property
    def fraction_measurement_base(self: "CastSelf") -> "_1844.FractionMeasurementBase":
        from mastapy._private.utility.units_and_measurements.measurements import _1844

        return self.__parent__._cast(_1844.FractionMeasurementBase)

    @property
    def fraction_per_temperature(self: "CastSelf") -> "_1845.FractionPerTemperature":
        from mastapy._private.utility.units_and_measurements.measurements import _1845

        return self.__parent__._cast(_1845.FractionPerTemperature)

    @property
    def frequency(self: "CastSelf") -> "_1846.Frequency":
        from mastapy._private.utility.units_and_measurements.measurements import _1846

        return self.__parent__._cast(_1846.Frequency)

    @property
    def fuel_consumption_engine(self: "CastSelf") -> "_1847.FuelConsumptionEngine":
        from mastapy._private.utility.units_and_measurements.measurements import _1847

        return self.__parent__._cast(_1847.FuelConsumptionEngine)

    @property
    def fuel_efficiency_vehicle(self: "CastSelf") -> "_1848.FuelEfficiencyVehicle":
        from mastapy._private.utility.units_and_measurements.measurements import _1848

        return self.__parent__._cast(_1848.FuelEfficiencyVehicle)

    @property
    def gradient(self: "CastSelf") -> "_1849.Gradient":
        from mastapy._private.utility.units_and_measurements.measurements import _1849

        return self.__parent__._cast(_1849.Gradient)

    @property
    def heat_conductivity(self: "CastSelf") -> "_1850.HeatConductivity":
        from mastapy._private.utility.units_and_measurements.measurements import _1850

        return self.__parent__._cast(_1850.HeatConductivity)

    @property
    def heat_transfer(self: "CastSelf") -> "_1851.HeatTransfer":
        from mastapy._private.utility.units_and_measurements.measurements import _1851

        return self.__parent__._cast(_1851.HeatTransfer)

    @property
    def heat_transfer_coefficient_for_plastic_gear_tooth(
        self: "CastSelf",
    ) -> "_1852.HeatTransferCoefficientForPlasticGearTooth":
        from mastapy._private.utility.units_and_measurements.measurements import _1852

        return self.__parent__._cast(_1852.HeatTransferCoefficientForPlasticGearTooth)

    @property
    def heat_transfer_resistance(self: "CastSelf") -> "_1853.HeatTransferResistance":
        from mastapy._private.utility.units_and_measurements.measurements import _1853

        return self.__parent__._cast(_1853.HeatTransferResistance)

    @property
    def impulse(self: "CastSelf") -> "_1854.Impulse":
        from mastapy._private.utility.units_and_measurements.measurements import _1854

        return self.__parent__._cast(_1854.Impulse)

    @property
    def index(self: "CastSelf") -> "_1855.Index":
        from mastapy._private.utility.units_and_measurements.measurements import _1855

        return self.__parent__._cast(_1855.Index)

    @property
    def inductance(self: "CastSelf") -> "_1856.Inductance":
        from mastapy._private.utility.units_and_measurements.measurements import _1856

        return self.__parent__._cast(_1856.Inductance)

    @property
    def integer(self: "CastSelf") -> "_1857.Integer":
        from mastapy._private.utility.units_and_measurements.measurements import _1857

        return self.__parent__._cast(_1857.Integer)

    @property
    def inverse_short_length(self: "CastSelf") -> "_1858.InverseShortLength":
        from mastapy._private.utility.units_and_measurements.measurements import _1858

        return self.__parent__._cast(_1858.InverseShortLength)

    @property
    def inverse_short_time(self: "CastSelf") -> "_1859.InverseShortTime":
        from mastapy._private.utility.units_and_measurements.measurements import _1859

        return self.__parent__._cast(_1859.InverseShortTime)

    @property
    def jerk(self: "CastSelf") -> "_1860.Jerk":
        from mastapy._private.utility.units_and_measurements.measurements import _1860

        return self.__parent__._cast(_1860.Jerk)

    @property
    def kinematic_viscosity(self: "CastSelf") -> "_1861.KinematicViscosity":
        from mastapy._private.utility.units_and_measurements.measurements import _1861

        return self.__parent__._cast(_1861.KinematicViscosity)

    @property
    def length_long(self: "CastSelf") -> "_1862.LengthLong":
        from mastapy._private.utility.units_and_measurements.measurements import _1862

        return self.__parent__._cast(_1862.LengthLong)

    @property
    def length_medium(self: "CastSelf") -> "_1863.LengthMedium":
        from mastapy._private.utility.units_and_measurements.measurements import _1863

        return self.__parent__._cast(_1863.LengthMedium)

    @property
    def length_per_unit_temperature(
        self: "CastSelf",
    ) -> "_1864.LengthPerUnitTemperature":
        from mastapy._private.utility.units_and_measurements.measurements import _1864

        return self.__parent__._cast(_1864.LengthPerUnitTemperature)

    @property
    def length_short(self: "CastSelf") -> "_1865.LengthShort":
        from mastapy._private.utility.units_and_measurements.measurements import _1865

        return self.__parent__._cast(_1865.LengthShort)

    @property
    def length_to_the_fourth(self: "CastSelf") -> "_1866.LengthToTheFourth":
        from mastapy._private.utility.units_and_measurements.measurements import _1866

        return self.__parent__._cast(_1866.LengthToTheFourth)

    @property
    def length_very_long(self: "CastSelf") -> "_1867.LengthVeryLong":
        from mastapy._private.utility.units_and_measurements.measurements import _1867

        return self.__parent__._cast(_1867.LengthVeryLong)

    @property
    def length_very_short(self: "CastSelf") -> "_1868.LengthVeryShort":
        from mastapy._private.utility.units_and_measurements.measurements import _1868

        return self.__parent__._cast(_1868.LengthVeryShort)

    @property
    def length_very_short_per_length_short(
        self: "CastSelf",
    ) -> "_1869.LengthVeryShortPerLengthShort":
        from mastapy._private.utility.units_and_measurements.measurements import _1869

        return self.__parent__._cast(_1869.LengthVeryShortPerLengthShort)

    @property
    def linear_angular_damping(self: "CastSelf") -> "_1870.LinearAngularDamping":
        from mastapy._private.utility.units_and_measurements.measurements import _1870

        return self.__parent__._cast(_1870.LinearAngularDamping)

    @property
    def linear_angular_stiffness_cross_term(
        self: "CastSelf",
    ) -> "_1871.LinearAngularStiffnessCrossTerm":
        from mastapy._private.utility.units_and_measurements.measurements import _1871

        return self.__parent__._cast(_1871.LinearAngularStiffnessCrossTerm)

    @property
    def linear_damping(self: "CastSelf") -> "_1872.LinearDamping":
        from mastapy._private.utility.units_and_measurements.measurements import _1872

        return self.__parent__._cast(_1872.LinearDamping)

    @property
    def linear_flexibility(self: "CastSelf") -> "_1873.LinearFlexibility":
        from mastapy._private.utility.units_and_measurements.measurements import _1873

        return self.__parent__._cast(_1873.LinearFlexibility)

    @property
    def linear_stiffness(self: "CastSelf") -> "_1874.LinearStiffness":
        from mastapy._private.utility.units_and_measurements.measurements import _1874

        return self.__parent__._cast(_1874.LinearStiffness)

    @property
    def magnetic_field_strength(self: "CastSelf") -> "_1875.MagneticFieldStrength":
        from mastapy._private.utility.units_and_measurements.measurements import _1875

        return self.__parent__._cast(_1875.MagneticFieldStrength)

    @property
    def magnetic_flux(self: "CastSelf") -> "_1876.MagneticFlux":
        from mastapy._private.utility.units_and_measurements.measurements import _1876

        return self.__parent__._cast(_1876.MagneticFlux)

    @property
    def magnetic_flux_density(self: "CastSelf") -> "_1877.MagneticFluxDensity":
        from mastapy._private.utility.units_and_measurements.measurements import _1877

        return self.__parent__._cast(_1877.MagneticFluxDensity)

    @property
    def magnetic_vector_potential(self: "CastSelf") -> "_1878.MagneticVectorPotential":
        from mastapy._private.utility.units_and_measurements.measurements import _1878

        return self.__parent__._cast(_1878.MagneticVectorPotential)

    @property
    def magnetomotive_force(self: "CastSelf") -> "_1879.MagnetomotiveForce":
        from mastapy._private.utility.units_and_measurements.measurements import _1879

        return self.__parent__._cast(_1879.MagnetomotiveForce)

    @property
    def mass(self: "CastSelf") -> "_1880.Mass":
        from mastapy._private.utility.units_and_measurements.measurements import _1880

        return self.__parent__._cast(_1880.Mass)

    @property
    def mass_per_unit_length(self: "CastSelf") -> "_1881.MassPerUnitLength":
        from mastapy._private.utility.units_and_measurements.measurements import _1881

        return self.__parent__._cast(_1881.MassPerUnitLength)

    @property
    def mass_per_unit_time(self: "CastSelf") -> "_1882.MassPerUnitTime":
        from mastapy._private.utility.units_and_measurements.measurements import _1882

        return self.__parent__._cast(_1882.MassPerUnitTime)

    @property
    def moment_of_inertia(self: "CastSelf") -> "_1883.MomentOfInertia":
        from mastapy._private.utility.units_and_measurements.measurements import _1883

        return self.__parent__._cast(_1883.MomentOfInertia)

    @property
    def moment_of_inertia_per_unit_length(
        self: "CastSelf",
    ) -> "_1884.MomentOfInertiaPerUnitLength":
        from mastapy._private.utility.units_and_measurements.measurements import _1884

        return self.__parent__._cast(_1884.MomentOfInertiaPerUnitLength)

    @property
    def moment_per_unit_pressure(self: "CastSelf") -> "_1885.MomentPerUnitPressure":
        from mastapy._private.utility.units_and_measurements.measurements import _1885

        return self.__parent__._cast(_1885.MomentPerUnitPressure)

    @property
    def number(self: "CastSelf") -> "_1886.Number":
        from mastapy._private.utility.units_and_measurements.measurements import _1886

        return self.__parent__._cast(_1886.Number)

    @property
    def percentage(self: "CastSelf") -> "_1887.Percentage":
        from mastapy._private.utility.units_and_measurements.measurements import _1887

        return self.__parent__._cast(_1887.Percentage)

    @property
    def power(self: "CastSelf") -> "_1888.Power":
        from mastapy._private.utility.units_and_measurements.measurements import _1888

        return self.__parent__._cast(_1888.Power)

    @property
    def power_per_small_area(self: "CastSelf") -> "_1889.PowerPerSmallArea":
        from mastapy._private.utility.units_and_measurements.measurements import _1889

        return self.__parent__._cast(_1889.PowerPerSmallArea)

    @property
    def power_per_unit_time(self: "CastSelf") -> "_1890.PowerPerUnitTime":
        from mastapy._private.utility.units_and_measurements.measurements import _1890

        return self.__parent__._cast(_1890.PowerPerUnitTime)

    @property
    def power_small(self: "CastSelf") -> "_1891.PowerSmall":
        from mastapy._private.utility.units_and_measurements.measurements import _1891

        return self.__parent__._cast(_1891.PowerSmall)

    @property
    def power_small_per_area(self: "CastSelf") -> "_1892.PowerSmallPerArea":
        from mastapy._private.utility.units_and_measurements.measurements import _1892

        return self.__parent__._cast(_1892.PowerSmallPerArea)

    @property
    def power_small_per_mass(self: "CastSelf") -> "_1893.PowerSmallPerMass":
        from mastapy._private.utility.units_and_measurements.measurements import _1893

        return self.__parent__._cast(_1893.PowerSmallPerMass)

    @property
    def power_small_per_unit_area_per_unit_time(
        self: "CastSelf",
    ) -> "_1894.PowerSmallPerUnitAreaPerUnitTime":
        from mastapy._private.utility.units_and_measurements.measurements import _1894

        return self.__parent__._cast(_1894.PowerSmallPerUnitAreaPerUnitTime)

    @property
    def power_small_per_unit_time(self: "CastSelf") -> "_1895.PowerSmallPerUnitTime":
        from mastapy._private.utility.units_and_measurements.measurements import _1895

        return self.__parent__._cast(_1895.PowerSmallPerUnitTime)

    @property
    def power_small_per_volume(self: "CastSelf") -> "_1896.PowerSmallPerVolume":
        from mastapy._private.utility.units_and_measurements.measurements import _1896

        return self.__parent__._cast(_1896.PowerSmallPerVolume)

    @property
    def pressure(self: "CastSelf") -> "_1897.Pressure":
        from mastapy._private.utility.units_and_measurements.measurements import _1897

        return self.__parent__._cast(_1897.Pressure)

    @property
    def pressure_per_unit_time(self: "CastSelf") -> "_1898.PressurePerUnitTime":
        from mastapy._private.utility.units_and_measurements.measurements import _1898

        return self.__parent__._cast(_1898.PressurePerUnitTime)

    @property
    def pressure_small(self: "CastSelf") -> "_1899.PressureSmall":
        from mastapy._private.utility.units_and_measurements.measurements import _1899

        return self.__parent__._cast(_1899.PressureSmall)

    @property
    def pressure_velocity_product(self: "CastSelf") -> "_1900.PressureVelocityProduct":
        from mastapy._private.utility.units_and_measurements.measurements import _1900

        return self.__parent__._cast(_1900.PressureVelocityProduct)

    @property
    def pressure_viscosity_coefficient(
        self: "CastSelf",
    ) -> "_1901.PressureViscosityCoefficient":
        from mastapy._private.utility.units_and_measurements.measurements import _1901

        return self.__parent__._cast(_1901.PressureViscosityCoefficient)

    @property
    def price(self: "CastSelf") -> "_1902.Price":
        from mastapy._private.utility.units_and_measurements.measurements import _1902

        return self.__parent__._cast(_1902.Price)

    @property
    def price_per_unit_mass(self: "CastSelf") -> "_1903.PricePerUnitMass":
        from mastapy._private.utility.units_and_measurements.measurements import _1903

        return self.__parent__._cast(_1903.PricePerUnitMass)

    @property
    def quadratic_angular_damping(self: "CastSelf") -> "_1904.QuadraticAngularDamping":
        from mastapy._private.utility.units_and_measurements.measurements import _1904

        return self.__parent__._cast(_1904.QuadraticAngularDamping)

    @property
    def quadratic_drag(self: "CastSelf") -> "_1905.QuadraticDrag":
        from mastapy._private.utility.units_and_measurements.measurements import _1905

        return self.__parent__._cast(_1905.QuadraticDrag)

    @property
    def rescaled_measurement(self: "CastSelf") -> "_1906.RescaledMeasurement":
        from mastapy._private.utility.units_and_measurements.measurements import _1906

        return self.__parent__._cast(_1906.RescaledMeasurement)

    @property
    def rotatum(self: "CastSelf") -> "_1907.Rotatum":
        from mastapy._private.utility.units_and_measurements.measurements import _1907

        return self.__parent__._cast(_1907.Rotatum)

    @property
    def safety_factor(self: "CastSelf") -> "_1908.SafetyFactor":
        from mastapy._private.utility.units_and_measurements.measurements import _1908

        return self.__parent__._cast(_1908.SafetyFactor)

    @property
    def specific_acoustic_impedance(
        self: "CastSelf",
    ) -> "_1909.SpecificAcousticImpedance":
        from mastapy._private.utility.units_and_measurements.measurements import _1909

        return self.__parent__._cast(_1909.SpecificAcousticImpedance)

    @property
    def specific_heat(self: "CastSelf") -> "_1910.SpecificHeat":
        from mastapy._private.utility.units_and_measurements.measurements import _1910

        return self.__parent__._cast(_1910.SpecificHeat)

    @property
    def square_root_of_unit_force_per_unit_area(
        self: "CastSelf",
    ) -> "_1911.SquareRootOfUnitForcePerUnitArea":
        from mastapy._private.utility.units_and_measurements.measurements import _1911

        return self.__parent__._cast(_1911.SquareRootOfUnitForcePerUnitArea)

    @property
    def stiffness_per_unit_face_width(
        self: "CastSelf",
    ) -> "_1912.StiffnessPerUnitFaceWidth":
        from mastapy._private.utility.units_and_measurements.measurements import _1912

        return self.__parent__._cast(_1912.StiffnessPerUnitFaceWidth)

    @property
    def stress(self: "CastSelf") -> "_1913.Stress":
        from mastapy._private.utility.units_and_measurements.measurements import _1913

        return self.__parent__._cast(_1913.Stress)

    @property
    def temperature(self: "CastSelf") -> "_1914.Temperature":
        from mastapy._private.utility.units_and_measurements.measurements import _1914

        return self.__parent__._cast(_1914.Temperature)

    @property
    def temperature_difference(self: "CastSelf") -> "_1915.TemperatureDifference":
        from mastapy._private.utility.units_and_measurements.measurements import _1915

        return self.__parent__._cast(_1915.TemperatureDifference)

    @property
    def temperature_per_unit_time(self: "CastSelf") -> "_1916.TemperaturePerUnitTime":
        from mastapy._private.utility.units_and_measurements.measurements import _1916

        return self.__parent__._cast(_1916.TemperaturePerUnitTime)

    @property
    def text(self: "CastSelf") -> "_1917.Text":
        from mastapy._private.utility.units_and_measurements.measurements import _1917

        return self.__parent__._cast(_1917.Text)

    @property
    def thermal_contact_coefficient(
        self: "CastSelf",
    ) -> "_1918.ThermalContactCoefficient":
        from mastapy._private.utility.units_and_measurements.measurements import _1918

        return self.__parent__._cast(_1918.ThermalContactCoefficient)

    @property
    def thermal_expansion_coefficient(
        self: "CastSelf",
    ) -> "_1919.ThermalExpansionCoefficient":
        from mastapy._private.utility.units_and_measurements.measurements import _1919

        return self.__parent__._cast(_1919.ThermalExpansionCoefficient)

    @property
    def thermal_resistance(self: "CastSelf") -> "_1920.ThermalResistance":
        from mastapy._private.utility.units_and_measurements.measurements import _1920

        return self.__parent__._cast(_1920.ThermalResistance)

    @property
    def thermo_elastic_factor(self: "CastSelf") -> "_1921.ThermoElasticFactor":
        from mastapy._private.utility.units_and_measurements.measurements import _1921

        return self.__parent__._cast(_1921.ThermoElasticFactor)

    @property
    def time(self: "CastSelf") -> "_1922.Time":
        from mastapy._private.utility.units_and_measurements.measurements import _1922

        return self.__parent__._cast(_1922.Time)

    @property
    def time_short(self: "CastSelf") -> "_1923.TimeShort":
        from mastapy._private.utility.units_and_measurements.measurements import _1923

        return self.__parent__._cast(_1923.TimeShort)

    @property
    def time_very_short(self: "CastSelf") -> "_1924.TimeVeryShort":
        from mastapy._private.utility.units_and_measurements.measurements import _1924

        return self.__parent__._cast(_1924.TimeVeryShort)

    @property
    def torque(self: "CastSelf") -> "_1925.Torque":
        from mastapy._private.utility.units_and_measurements.measurements import _1925

        return self.__parent__._cast(_1925.Torque)

    @property
    def torque_converter_inverse_k(self: "CastSelf") -> "_1926.TorqueConverterInverseK":
        from mastapy._private.utility.units_and_measurements.measurements import _1926

        return self.__parent__._cast(_1926.TorqueConverterInverseK)

    @property
    def torque_converter_k(self: "CastSelf") -> "_1927.TorqueConverterK":
        from mastapy._private.utility.units_and_measurements.measurements import _1927

        return self.__parent__._cast(_1927.TorqueConverterK)

    @property
    def torque_per_current(self: "CastSelf") -> "_1928.TorquePerCurrent":
        from mastapy._private.utility.units_and_measurements.measurements import _1928

        return self.__parent__._cast(_1928.TorquePerCurrent)

    @property
    def torque_per_square_root_of_power(
        self: "CastSelf",
    ) -> "_1929.TorquePerSquareRootOfPower":
        from mastapy._private.utility.units_and_measurements.measurements import _1929

        return self.__parent__._cast(_1929.TorquePerSquareRootOfPower)

    @property
    def torque_per_unit_temperature(
        self: "CastSelf",
    ) -> "_1930.TorquePerUnitTemperature":
        from mastapy._private.utility.units_and_measurements.measurements import _1930

        return self.__parent__._cast(_1930.TorquePerUnitTemperature)

    @property
    def velocity(self: "CastSelf") -> "_1931.Velocity":
        from mastapy._private.utility.units_and_measurements.measurements import _1931

        return self.__parent__._cast(_1931.Velocity)

    @property
    def velocity_small(self: "CastSelf") -> "_1932.VelocitySmall":
        from mastapy._private.utility.units_and_measurements.measurements import _1932

        return self.__parent__._cast(_1932.VelocitySmall)

    @property
    def viscosity(self: "CastSelf") -> "_1933.Viscosity":
        from mastapy._private.utility.units_and_measurements.measurements import _1933

        return self.__parent__._cast(_1933.Viscosity)

    @property
    def voltage(self: "CastSelf") -> "_1934.Voltage":
        from mastapy._private.utility.units_and_measurements.measurements import _1934

        return self.__parent__._cast(_1934.Voltage)

    @property
    def voltage_per_angular_velocity(
        self: "CastSelf",
    ) -> "_1935.VoltagePerAngularVelocity":
        from mastapy._private.utility.units_and_measurements.measurements import _1935

        return self.__parent__._cast(_1935.VoltagePerAngularVelocity)

    @property
    def volume(self: "CastSelf") -> "_1936.Volume":
        from mastapy._private.utility.units_and_measurements.measurements import _1936

        return self.__parent__._cast(_1936.Volume)

    @property
    def wear_coefficient(self: "CastSelf") -> "_1937.WearCoefficient":
        from mastapy._private.utility.units_and_measurements.measurements import _1937

        return self.__parent__._cast(_1937.WearCoefficient)

    @property
    def yank(self: "CastSelf") -> "_1938.Yank":
        from mastapy._private.utility.units_and_measurements.measurements import _1938

        return self.__parent__._cast(_1938.Yank)

    @property
    def measurement_base(self: "CastSelf") -> "MeasurementBase":
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
class MeasurementBase(_0.APIBase):
    """MeasurementBase

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _MEASUREMENT_BASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def absolute_tolerance(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "AbsoluteTolerance")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @absolute_tolerance.setter
    @exception_bridge
    @enforce_parameter_types
    def absolute_tolerance(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "AbsoluteTolerance", value)

    @property
    @exception_bridge
    def default_unit(
        self: "Self",
    ) -> "list_with_selected_item.ListWithSelectedItem_Unit":
        """ListWithSelectedItem[mastapy.utility.units_and_measurements.Unit]"""
        temp = pythonnet_property_get(self.wrapped, "DefaultUnit")

        if temp is None:
            return None

        selected_value = temp.SelectedValue

        if selected_value is None:
            return ListWithSelectedItem_None(temp)

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.list_with_selected_item",
            "ListWithSelectedItem_Unit",
        )(temp)

    @default_unit.setter
    @exception_bridge
    @enforce_parameter_types
    def default_unit(self: "Self", value: "_1807.Unit") -> None:
        generic_type = list_with_selected_item.ListWithSelectedItem_Unit.implicit_type()
        value = promote_to_list_with_selected_item(value)
        value = conversion.mp_to_pn_smt_list_with_selected_item(
            self, value, generic_type
        )
        pythonnet_property_set(self.wrapped, "DefaultUnit", value)

    @property
    @exception_bridge
    def name(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Name")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def percentage_tolerance(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "PercentageTolerance")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @percentage_tolerance.setter
    @exception_bridge
    @enforce_parameter_types
    def percentage_tolerance(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "PercentageTolerance", value)

    @property
    @exception_bridge
    def rounding_digits(self: "Self") -> "int":
        """int"""
        temp = pythonnet_property_get(self.wrapped, "RoundingDigits")

        if temp is None:
            return 0

        return temp

    @rounding_digits.setter
    @exception_bridge
    @enforce_parameter_types
    def rounding_digits(self: "Self", value: "int") -> None:
        pythonnet_property_set(
            self.wrapped, "RoundingDigits", int(value) if value is not None else 0
        )

    @property
    @exception_bridge
    def rounding_method(self: "Self") -> "_1794.RoundingMethods":
        """mastapy.utility.RoundingMethods"""
        temp = pythonnet_property_get(self.wrapped, "RoundingMethod")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(temp, "SMT.MastaAPI.Utility.RoundingMethods")

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.utility._1794", "RoundingMethods"
        )(value)

    @rounding_method.setter
    @exception_bridge
    @enforce_parameter_types
    def rounding_method(self: "Self", value: "_1794.RoundingMethods") -> None:
        value = conversion.mp_to_pn_enum(value, "SMT.MastaAPI.Utility.RoundingMethods")
        pythonnet_property_set(self.wrapped, "RoundingMethod", value)

    @property
    @exception_bridge
    def current_unit(self: "Self") -> "_1807.Unit":
        """mastapy.utility.units_and_measurements.Unit

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "CurrentUnit")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def available_units(self: "Self") -> "List[_1807.Unit]":
        """List[mastapy.utility.units_and_measurements.Unit]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AvailableUnits")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def report_names(self: "Self") -> "List[str]":
        """List[str]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ReportNames")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp, str)

        if value is None:
            return None

        return value

    @exception_bridge
    @enforce_parameter_types
    def output_default_report_to(self: "Self", file_path: "PathLike") -> None:
        """Method does not return.

        Args:
            file_path (PathLike)
        """
        file_path = str(file_path)
        pythonnet_method_call(self.wrapped, "OutputDefaultReportTo", file_path)

    @exception_bridge
    def get_default_report_with_encoded_images(self: "Self") -> "str":
        """str"""
        method_result = pythonnet_method_call(
            self.wrapped, "GetDefaultReportWithEncodedImages"
        )
        return method_result

    @exception_bridge
    @enforce_parameter_types
    def output_active_report_to(self: "Self", file_path: "PathLike") -> None:
        """Method does not return.

        Args:
            file_path (PathLike)
        """
        file_path = str(file_path)
        pythonnet_method_call(self.wrapped, "OutputActiveReportTo", file_path)

    @exception_bridge
    @enforce_parameter_types
    def output_active_report_as_text_to(self: "Self", file_path: "PathLike") -> None:
        """Method does not return.

        Args:
            file_path (PathLike)
        """
        file_path = str(file_path)
        pythonnet_method_call(self.wrapped, "OutputActiveReportAsTextTo", file_path)

    @exception_bridge
    def get_active_report_with_encoded_images(self: "Self") -> "str":
        """str"""
        method_result = pythonnet_method_call(
            self.wrapped, "GetActiveReportWithEncodedImages"
        )
        return method_result

    @exception_bridge
    @enforce_parameter_types
    def output_named_report_to(
        self: "Self", report_name: "str", file_path: "PathLike"
    ) -> None:
        """Method does not return.

        Args:
            report_name (str)
            file_path (PathLike)
        """
        report_name = str(report_name)
        file_path = str(file_path)
        pythonnet_method_call(
            self.wrapped,
            "OutputNamedReportTo",
            report_name if report_name else "",
            file_path,
        )

    @exception_bridge
    @enforce_parameter_types
    def output_named_report_as_masta_report(
        self: "Self", report_name: "str", file_path: "PathLike"
    ) -> None:
        """Method does not return.

        Args:
            report_name (str)
            file_path (PathLike)
        """
        report_name = str(report_name)
        file_path = str(file_path)
        pythonnet_method_call(
            self.wrapped,
            "OutputNamedReportAsMastaReport",
            report_name if report_name else "",
            file_path,
        )

    @exception_bridge
    @enforce_parameter_types
    def output_named_report_as_text_to(
        self: "Self", report_name: "str", file_path: "PathLike"
    ) -> None:
        """Method does not return.

        Args:
            report_name (str)
            file_path (PathLike)
        """
        report_name = str(report_name)
        file_path = str(file_path)
        pythonnet_method_call(
            self.wrapped,
            "OutputNamedReportAsTextTo",
            report_name if report_name else "",
            file_path,
        )

    @exception_bridge
    @enforce_parameter_types
    def get_named_report_with_encoded_images(self: "Self", report_name: "str") -> "str":
        """str

        Args:
            report_name (str)
        """
        report_name = str(report_name)
        method_result = pythonnet_method_call(
            self.wrapped,
            "GetNamedReportWithEncodedImages",
            report_name if report_name else "",
        )
        return method_result

    @property
    def cast_to(self: "Self") -> "_Cast_MeasurementBase":
        """Cast to another type.

        Returns:
            _Cast_MeasurementBase
        """
        return _Cast_MeasurementBase(self)
