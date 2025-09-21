#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Avalanche Photodiode (APD) models and utilities."""

from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING

import numpy as np
from typing_extensions import Self, deprecated

from pyxel.util import get_size, get_uninitialized_error

if TYPE_CHECKING:
    from pyxel.detectors import APDGeometry


def detector_gain(capacitance: float, roic_gain: float) -> float:
    """Compute the effective gain of an APD detector.

    The gain is calculated from the ROIC gain and the pixel capacitance.

    Parameters
    ----------
    capacitance : float
        Pixel capacitance in Farads.
    roic_gain : float
        Gain of the readout circuit in V/electron.

    Returns
    -------
    float
        Effective detector gain.
    """
    # Late import to speedup start-up time
    import astropy.constants as const

    return roic_gain * (const.e.value / capacitance)


def create_func_interpolate(xp: np.ndarray, yp: np.ndarray) -> Callable[[float], float]:
    """Create a 1D linear interpolation function.

    Parameters
    ----------
    xp : ndarray
        Array of x-coordinates (must be monotonic increasing).
    yp : ndarray:
        Array of y-coordinates corresponding to `xp`.

    Returns
    -------
    Callable[[float], float]
        Function that interpolates a single float value.
    """
    import numpy as np

    def _func_interpolate(x: float) -> float:
        return float(
            np.interp(
                x,
                xp=np.asarray(xp, dtype=float),
                fp=np.asarray(yp, dtype=float),
            )
        )

    return _func_interpolate


class ConverterValues:
    """Callable converter using an interpolation from a provided list of `(x, y)` pairs.

    Parameters
    ----------
    values : list[tuple[float, float]]
        List of `(x, y)` pairs used for interpolation. The first element in each
        tuple is the input value, and the second is the corresponding output value.

    Raises
    ------
    ValueError
        If the list cannot be converted to a 2-column DataFrame, is empty,
        does not have exactly 2 columns, or if the first column is not monotonic.

    Examples
    --------
    >>> func = ConverterValues(
    ...     values=[
    ...         (1.0, 46.5),
    ...         (1.5, 41.3),
    ...         (2.5, 37.3),
    ...         (3.5, 34.8),
    ...         (4.5, 33.2),
    ...         (6.5, 31.4),
    ...         (8.5, 30.7),
    ...         (10.5, 30.4),
    ...     ]
    ... )

    >>> func(1.0)
    46.5
    >>> func(2.0)
    39.3
    """

    def __init__(self, values: list[tuple[float, float]]):
        self._values: list[tuple[float, float]] = values

        # Late import
        import pandas as pd

        try:
            df = pd.DataFrame(self._values)
        except Exception as exc:
            raise ValueError("Failed to convert a list of values") from exc

        if len(df.columns) != 2:
            raise ValueError("Values must have 2-columns")

        # TODO: Check that the first column on 'df' is monotonic
        first_column: pd.Series = df.iloc[:, 0]
        second_column: pd.Series = df.iloc[:, 1]

        if (
            not first_column.is_monotonic_increasing
            and not first_column.is_monotonic_decreasing
        ):
            raise ValueError("Values are not monotonic !")

        self._func: Callable[[float], float] = create_func_interpolate(
            xp=np.asarray(first_column, dtype=float),
            yp=np.asarray(second_column, dtype=float),
        )

    def __eq__(self, other) -> bool:
        return type(self) is type(other) and np.allclose(
            np.asarray(self._values), np.asarray(other._values)
        )

    def __call__(self, x: float) -> float:
        # TODO: Add valid min_range and max_range
        return self._func(x)

    def to_dict(self) -> dict:
        return {"values": self._values}


class ConverterTable:
    """Callable converter that reads table from a filename."""

    def __init__(self, filename: str, with_header: bool = False):
        self._filename: str = filename
        self._with_header: bool = with_header

        from pyxel.inputs import load_table_v2

        try:
            df = load_table_v2(filename, header=self._with_header)
        except Exception as exc:
            raise ValueError(f"Failed to convert {self._filename!r}") from exc

        if len(df.columns) != 2:
            raise ValueError(f"File {self._filename!r} must have exactly two columns")

        if df.empty:
            raise ValueError(f"File {self._filename!r} is empty")

        self._func: Callable[[float], float] = create_func_interpolate(
            xp=np.asarray(df.iloc[:, 0], dtype=float),
            yp=np.asarray(df.iloc[:, 1], dtype=float),
        )

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return f"{cls_name}(filename={self._filename!r}, with_header={self._with_header!r})"

    def __eq__(self, other) -> bool:
        return (
            type(self) is type(other)
            and self._filename == other._filename
            and self._with_header == other._with_header
        )

    def __call__(self, x: float) -> float:
        return self._func(x)

    def to_dict(self) -> dict:
        return {"filename": self._filename, "with_header": self._with_header}


class ConverterFunction:
    """A callable converter that wraps a mathematical function."""

    def __init__(self, function: str | Callable[[float], float]):
        self._function: str | Callable[[float], float] = function

        if isinstance(function, str):
            import math

            # TODO: Check this, this is security-sensitive
            # TODO: Check that it's a 'Callable[[float], float]'
            try:
                func = eval(function, {"math": math})
            except Exception as exc:
                raise ValueError(f"Cannot use {function=}") from exc

        elif callable(function):
            # TODO: Check that it's a 'Callable[[float], float]'
            func = function
        else:
            raise TypeError("Invalid function specification")

        if not callable(func):
            raise TypeError(f"{func=} is not a callable")

        self._func = func

    def __eq__(self, other) -> bool:
        if callable(self._function):
            raise NotImplementedError("Cannot compare with a callable")

        return type(self) is type(other) and (
            isinstance(self._function, str) and self._function == other._function
        )

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return f"{cls_name}({self._function!r})"

    def __call__(self, x: float) -> float:
        try:
            return self._func(x)
        except Exception as exc:
            raise ValueError(
                f"Failed to execute function {self._function!r} with {x=}"
            ) from exc

    def to_dict(self) -> dict:
        # Late import
        import cloudpickle

        return {"function": str(cloudpickle.dumps(self._function))}

    @classmethod
    def from_dict(cls, dct: Mapping) -> Self:
        # Late import
        import cloudpickle

        if "function" not in dct:
            raise KeyError("Missing key 'function'")

        func = dct["function"]

        if isinstance(func, bytes):
            func_callable = cloudpickle.loads(func)
            return cls(function=func_callable)
        elif isinstance(func, str) or callable(func):
            if func.startswith("b'\\"):
                evaluated_func: bytes = eval(func)
                func_callable = cloudpickle.loads(evaluated_func)
                return cls(function=func_callable)
            else:
                return cls(function=func)
        else:
            raise TypeError(f"Expecting a callable, str or bytes. Got {func=!r}")


class AvalancheSettings:
    """Class to store and compute Avalanche Photodiode (APD) gain/bias settings.

    This class encapsulates the relationship between avalanche gain, pixel
    reset voltage, common voltage, and the avalanche bias. Conversions between
    gain and bias can be done using provided converter functions, tables, or
    value mappings.

    Parameters
    ----------
    avalanche_gain : float
        Gain of the avalanche multiplication stage.
    pixel_reset_voltage : float
        Pixel reset voltage in V.
    common_voltage : float
        Commonn voltage in V.
    gain_to_bias : callable, optional
        Function to convert from 'avalanche gain' to 'avalanche bias' (in V).
    bias_to_gain : callable, optional
        Function to convert from 'avalanche bias' (in V) to 'avalanche gain'.

    Examples
    --------
    >>> from pyxel.detectors.apd import AvalancheSettings
    >>> gain_to_bias = lambda gain: 0.5 * gain  # Dummy conversion
    >>> bias_to_gain = lambda bias: bias / 0.5
    >>> settings = AvalancheSettings(
    ...     avalanche_gain=10.0,
    ...     pixel_reset_voltage=3.0,
    ...     common_voltage=2.0,
    ...     gain_to_bias=gain_to_bias,
    ...     bias_to_gain=bias_to_gain,
    ... )
    >>> settings.avalanche_bias
    1.0
    >>> settings.avalanche_gain = 100.0
    >>> settings.avalanche_bias
    50.0
    """

    def __init__(
        self,
        gain_to_bias: (
            ConverterValues
            | ConverterTable
            | ConverterFunction
            | Callable[[float], float]
        ),
        bias_to_gain: (
            ConverterValues
            | ConverterTable
            | ConverterFunction
            | Callable[[float], float]
        ),
        avalanche_gain: float | None = None,
        pixel_reset_voltage: float | None = None,
        common_voltage: float | None = None,
    ):
        # Ensure that 'gain_to_bias' and 'bias_to_gain' are valid converter functions
        if isinstance(
            gain_to_bias, ConverterValues | ConverterTable | ConverterFunction
        ):
            gain_to_bias_func = gain_to_bias
        else:
            gain_to_bias_func = ConverterFunction(gain_to_bias)

        if isinstance(
            bias_to_gain, ConverterValues | ConverterTable | ConverterFunction
        ):
            bias_to_gain_func = bias_to_gain
        else:
            bias_to_gain_func = ConverterFunction(bias_to_gain)

        self._gain_to_bias: ConverterValues | ConverterTable | ConverterFunction = (
            gain_to_bias_func
        )
        self._bias_to_gain: ConverterValues | ConverterTable | ConverterFunction = (
            bias_to_gain_func
        )

        # Case 1: 'avalanche_gain' is provided
        if avalanche_gain is not None:
            if not (1.0 <= avalanche_gain <= 1000.0):
                raise ValueError(
                    f"Invalid '{avalanche_gain=}'. Value must be between 1.0 and 1000.0."
                )

            # Provided 'avalanche_gain'
            self._avalanche_gain: float = avalanche_gain
            self._avalanche_bias: float = gain_to_bias(avalanche_gain)

            if pixel_reset_voltage is not None:
                if common_voltage is None:
                    # Missing 'common_voltage'
                    self._pixel_reset_voltage: float | None = pixel_reset_voltage
                    self._common_voltage: float | None = None
                else:
                    # Too many parameters
                    raise ValueError(
                        "Too many parameters. Only two of these parameters must "
                        "be provided: 'avalanche_gain', 'pixel_reset_voltage', 'common_voltage'"
                    )
            else:
                # Missing 'pixel_reset_voltage'
                if common_voltage is not None:
                    self._pixel_reset_voltage = None
                    self._common_voltage = common_voltage

                else:
                    # Missing too many parameters
                    raise ValueError(
                        "'avalanche_gain' provided. Missing one of these parameters: "
                        "'pixel_reset_voltage', 'common_voltage'"
                    )
        else:
            # Missing 'avalanche_gain'
            if pixel_reset_voltage is not None:
                if common_voltage is None:
                    raise ValueError(
                        "'avalanche_gain' not provided and missing 'pixel_reset_voltage'. Parameter "
                        "'common_voltage' must be provided"
                    )

                self._pixel_reset_voltage = pixel_reset_voltage
                self._common_voltage = common_voltage

            else:
                if common_voltage is None:
                    # Missing 'common_voltage'
                    raise ValueError(
                        "Missing parameters. Two of these parameters must "
                        "be provided: 'avalanche_gain', 'pixel_reset_voltage', 'common_voltage'"
                    )
                else:
                    raise ValueError(
                        "'avalanche_gain' not provided and missing 'pixel_reset_voltage'. Parameter "
                        "'common_voltage' must be provided"
                    )
            self._avalanche_bias = self._pixel_reset_voltage - self._common_voltage
            self._avalanche_gain = bias_to_gain(self._avalanche_bias)

    def __eq__(self, other) -> bool:
        return (
            type(self) is type(other)
            and self._gain_to_bias == other._gain_to_bias
            and self._bias_to_gain == other._bias_to_gain
            and self._avalanche_gain == other._avalanche_gain
            and self._pixel_reset_voltage == other._pixel_reset_voltage
            and self._common_voltage == other._common_voltage
        )

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return (
            f"{cls_name}(avalanche_gain={self._avalanche_gain}, "
            f"pixel_reset_voltage={self._pixel_reset_voltage}, common_voltage={self._common_voltage}, "
            f"gain_to_bias={self._gain_to_bias!r}, bias_to_gain={self._bias_to_gain!r}"
        )

    @property
    def avalanche_gain(self) -> float:
        """Avalanche gain in e-/e-."""
        return self._avalanche_gain

    @avalanche_gain.setter
    def avalanche_gain(self, value: float) -> None:
        if not (1.0 <= value <= 1000.0):
            raise ValueError(
                f"Invalid 'avalanche_gain={value!r}'. "
                f"Value must be between 1.0 and 1000.0."
            )

        self._avalanche_gain = value
        self._avalanche_bias = self._gain_to_bias(value)
        self._common_voltage = self.pixel_reset_voltage - self.avalanche_gain

    @property
    def pixel_reset_voltage(self) -> float:
        """Pixel reset voltage in V."""
        if self._pixel_reset_voltage is not None:
            return self._pixel_reset_voltage

        return self.common_voltage + self.avalanche_bias

    @pixel_reset_voltage.setter
    def pixel_reset_voltage(self, value: float) -> None:
        self._pixel_reset_voltage = value

        self._avalanche_bias = value - self.common_voltage
        self._avalanche_gain = self._bias_to_gain(self.avalanche_bias)

    @property
    def common_voltage(self) -> float:
        """Common voltage in V."""
        if self._common_voltage is not None:
            return self._common_voltage

        return self.pixel_reset_voltage - self.avalanche_bias

    @common_voltage.setter
    def common_voltage(self, value: float) -> None:
        # bias = prv - common
        self._common_voltage = value

        self._avalanche_bias = self.pixel_reset_voltage - value
        self._avalanche_gain = self._bias_to_gain(self.avalanche_bias)

    @property
    def avalanche_bias(self) -> float:
        """Avalanche bias in V."""
        return self._avalanche_bias

    def to_dict(self) -> dict:
        return {
            "avalanche_gain": self._avalanche_gain,
            "pixel_reset_voltage": self._pixel_reset_voltage,
            "common_voltage": self._common_voltage,
            "gain_to_bias": self._gain_to_bias.to_dict(),
            "bias_to_gain": self._bias_to_gain.to_dict(),
        }

    @classmethod
    def from_dict(cls, dct: dict) -> Self:
        """Build an 'AvalancheSettings' instance from a dictionary."""
        # Late import
        from pyxel.configuration.configuration import build_converter

        avalanche_gain: float | None = dct.get("avalanche_gain")
        pixel_reset_voltage: float | None = dct.get("pixel_reset_voltage")
        common_voltage: float | None = dct.get("common_voltage")

        if "gain_to_bias" not in dct:
            raise ValueError(
                "Missing required key: 'gain_to_bias' in settings dictionary."
            )
        if "bias_to_gain" not in dct:
            raise ValueError(
                "Missing required key: 'bias_to_gain' in settings dictionary."
            )

        gain_to_bias: dict = dct["gain_to_bias"]
        bias_to_gain: dict = dct["bias_to_gain"]

        gain_to_bias_func: ConverterValues | ConverterTable | ConverterFunction = (
            build_converter(gain_to_bias)
        )
        bias_to_gain_func: ConverterValues | ConverterTable | ConverterFunction = (
            build_converter(bias_to_gain)
        )

        return cls(
            avalanche_gain=avalanche_gain,
            pixel_reset_voltage=pixel_reset_voltage,
            common_voltage=common_voltage,
            gain_to_bias=gain_to_bias_func,
            bias_to_gain=bias_to_gain_func,
        )


class APDCharacteristics:
    """Characteristic attributes of the APD detector.

    Parameters
    ----------
    roic_gain : float
        Gain of the read-out integrated circuit. Unit: V/V
    bias_to_node : ConverterValues, ConverterTable, ConverterFunction
    avalanche_settings : AvalancheSettings
    quantum_efficiency : float, optional
        Quantum efficiency.
    full_well_capacity : float, optional
        Full well capacity. Unit: e-
    adc_bit_resolution : int, optional
        ADC bit resolution.
    adc_voltage_range : tuple of floats, optional
        ADC voltage range. Unit: V
    """

    def __init__(
        self,
        roic_gain: float,  # unit: V
        bias_to_node: ConverterValues | ConverterTable | ConverterFunction,
        avalanche_settings: AvalancheSettings,
        #####################
        # Common parameters #
        #####################
        quantum_efficiency: float | None = None,  # unit: NA
        full_well_capacity: float | None = None,  # unit: electron
        adc_bit_resolution: int | None = None,
        adc_voltage_range: tuple[float, float] | None = None,  # unit: V
    ):
        self._avalanche_settings: AvalancheSettings = avalanche_settings
        self._bias_to_node: ConverterValues | ConverterTable | ConverterFunction = (
            bias_to_node
        )

        if quantum_efficiency and not (0.0 <= quantum_efficiency <= 1.0):
            raise ValueError("'quantum_efficiency' must be between 0.0 and 1.0.")

        if adc_bit_resolution and not (4 <= adc_bit_resolution <= 64):
            raise ValueError("'adc_bit_resolution' must be between 4 and 64.")
        if adc_voltage_range and not len(adc_voltage_range) == 2:
            raise ValueError("Voltage range must have length of 2.")
        if full_well_capacity and not (0.0 <= full_well_capacity <= 1.0e7):
            raise ValueError("'full_well_capacity' must be between 0 and 1e7.")

        self._quantum_efficiency: float | None = quantum_efficiency
        self._full_well_capacity: float | None = full_well_capacity
        self._adc_voltage_range: tuple[float, float] | None = adc_voltage_range
        self._adc_bit_resolution: int | None = adc_bit_resolution
        self._node_capacitance: float = self.bias_to_node_capacitance(
            self.avalanche_settings.avalanche_bias
        )
        self._roic_gain: float = roic_gain

        # TODO: Is it really needed ? or property 'charge_to_volt_conversion' is enough ?
        self._charge_to_volt_conversion: float = detector_gain(
            capacitance=self._node_capacitance,
            roic_gain=self.roic_gain,
        )

        # TODO: This variable is available in class 'Characteristics' and 'APDCharacteristics'
        #       Refactor this
        self._channels_gain: float | np.ndarray | None = None

        # Late binding
        self._geometry: "APDGeometry" | None = None

        self._numbytes = 0

    def __eq__(self, other) -> bool:
        return (
            type(self) is type(other)
            and self._roic_gain == other._roic_gain
            and self._bias_to_node == other._bias_to_node
            and self._avalanche_settings == other._avalanche_settings
            and self._quantum_efficiency == other._quantum_efficiency
            and self._full_well_capacity == other._full_well_capacity
            and self._adc_bit_resolution == other._adc_bit_resolution
            and self._adc_voltage_range == other._adc_voltage_range
            and self._avalanche_settings == other._avalanche_settings
        )

    # TODO: This method exists in class 'Characteristics' and 'APDCharacteristics'
    #       Refactor this
    def _build_channels_gain(self, value: float | dict[str, float] | None):
        if value is None:
            self._channels_gain = None
            return

        if isinstance(value, float):
            if not (0.0 <= value <= 100.0):
                raise ValueError(
                    "'charge_to_volt_conversion' must be between 0.0 and 100.0."
                )
            self._channels_gain = value
            return

        if isinstance(value, dict):
            if self._geometry is None:
                raise ValueError(
                    "Geometry must be initialized before setting channel gains."
                )

            if self._geometry.channels is None:
                raise ValueError("Missing parameter '.channels' in Geometry.")

            value_2d = np.zeros(shape=self._geometry.shape, dtype=float)

            for channel, gain in value.items():
                if not (0.0 <= gain <= 100.0):
                    raise ValueError(
                        f"Gain for channel {channel} must be between 0.0 and 100.0."
                    )
                slice_y, slice_x = self._geometry.get_channel_coord(channel)
                value_2d[slice_y, slice_x] = gain

            self._channels_gain = value_2d

            # Perform channel mismatch check after processing all gains
            defined_channels = set(self._geometry.channels.readout_position.keys())
            input_channels = set(value.keys())
            if defined_channels != input_channels:
                raise ValueError(
                    "Mismatch between the defined channels in geometry and provided channel gains."
                )
            return

        raise TypeError(
            "Invalid type for 'charge_to_volt_conversion'; expected float or dict."
        )

    # TODO: This method is similar in 'APDCharacteristics and 'Characteristics'
    #       Refactor these methods
    def initialize(self, geometry: "APDGeometry"):
        self._geometry = geometry
        charge_to_volt = self.charge_to_volt_conversion
        if charge_to_volt is not None:
            self._build_channels_gain(value=charge_to_volt)

    @property
    def quantum_efficiency(self) -> float:
        """Get Quantum efficiency."""
        if self._quantum_efficiency is None:
            raise ValueError(
                get_uninitialized_error(
                    name="quantum_efficiency",
                    parent_name="characteristics",
                )
            )

        return self._quantum_efficiency

    @quantum_efficiency.setter
    def quantum_efficiency(self, value: float) -> None:
        """Set Quantum efficiency."""
        if np.min(value) < 0.0 or np.max(value) > 1.0:
            raise ValueError("'quantum_efficiency' values must be between 0.0 and 1.0.")

        self._quantum_efficiency = value

    @property
    def avalanche_settings(self) -> AvalancheSettings:
        return self._avalanche_settings

    @property
    @deprecated("Use '.avalanche_settings.avalanche_gain")
    def avalanche_gain(self) -> float:
        """Get APD gain."""
        return self.avalanche_settings.avalanche_gain

    @avalanche_gain.setter
    def avalanche_gain(self, value: float) -> None:
        """Set APD gain."""
        self.avalanche_settings.avalanche_gain = value

    @property
    @deprecated("Use '.avalanche_settings.pixel_reset_voltage")
    def pixel_reset_voltage(self) -> float:
        """Get pixel reset voltage."""
        return self.avalanche_settings.pixel_reset_voltage

    @pixel_reset_voltage.setter
    def pixel_reset_voltage(self, value: float) -> None:
        """Set pixel reset voltage."""
        self.avalanche_settings.pixel_reset_voltage = value

    @property
    @deprecated("Use '.avalanche_settings.common_voltage")
    def common_voltage(self) -> float:
        """Get common voltage."""
        return self.avalanche_settings.common_voltage

    @common_voltage.setter
    def common_voltage(self, value: float) -> None:
        """Set common voltage."""
        self.avalanche_settings.common_voltage = value

    @property
    @deprecated("Use '.avalanche_settings.avalanche_bias")
    def avalanche_bias(self) -> float:
        """Get avalanche bias."""
        return self.avalanche_settings.avalanche_bias

    @property
    def roic_gain(self) -> float:
        """Get roic gain."""
        return self._roic_gain

    @property
    def node_capacitance(self) -> float:
        """Compute node capacitance dynamically from avalanche bias."""
        return self.bias_to_node_capacitance(self.avalanche_settings.avalanche_bias)

    @property
    def charge_to_volt_conversion(self) -> float:
        """Compute charge-to-voltage conversion factor."""
        capacitance = self.bias_to_node_capacitance(
            self.avalanche_settings.avalanche_bias
        )
        return detector_gain(capacitance=capacitance, roic_gain=self.roic_gain)

    @property
    def adc_bit_resolution(self) -> int:
        """Get bit resolution of the Analog-Digital Converter."""
        if self._adc_bit_resolution is None:
            raise ValueError(
                get_uninitialized_error(
                    name="adc_bit_resolution",
                    parent_name="characteristics",
                )
            )

        return self._adc_bit_resolution

    @adc_bit_resolution.setter
    def adc_bit_resolution(self, value: int) -> None:
        """Set bit resolution of the Analog-Digital Converter."""
        if not (4 <= value <= 64):
            raise ValueError("'adc_bit_resolution' must be between 4 and 64.")

        self._adc_bit_resolution = value

    @property
    def adc_voltage_range(self) -> tuple[float, float]:
        """Get voltage range of the Analog-Digital Converter."""
        if self._adc_voltage_range is None:
            raise ValueError(
                get_uninitialized_error(
                    name="adc_voltage_range",
                    parent_name="characteristics",
                )
            )
        return self._adc_voltage_range

    @adc_voltage_range.setter
    def adc_voltage_range(self, value: tuple[float, float]) -> None:
        """Set voltage range of the Analog-Digital Converter."""
        self._adc_voltage_range = value

    @property
    def full_well_capacity(self) -> float:
        """Get Full well capacity."""
        if self._full_well_capacity is None:
            raise ValueError(
                get_uninitialized_error(
                    name="full_well_capacity",
                    parent_name="characteristics",
                )
            )
        return self._full_well_capacity

    @full_well_capacity.setter
    def full_well_capacity(self, value: float) -> None:
        """Set Full well capacity."""
        if not (0.0 <= value <= 1.0e7):
            raise ValueError("'full_well_capacity' must be between 0 and 1e+7.")

        self._full_well_capacity = value

    @property
    def system_gain(self) -> float:
        """Compute the full system gain based on detector type."""
        return (
            self.quantum_efficiency
            * self.avalanche_settings.avalanche_gain
            * self.charge_to_volt_conversion
            * 2**self.adc_bit_resolution
        ) / (max(self.adc_voltage_range) - min(self.adc_voltage_range))

    @property
    def numbytes(self) -> int:
        """Recursively calculates object size in bytes using Pympler library.

        Returns
        -------
        int
            Size of the object in bytes.
        """
        self._numbytes = get_size(self)
        return self._numbytes

    def bias_to_node_capacitance(self, bias: float) -> float:
        """Compute node capacitance from bias voltage using user-provided function.

        Parameters
        ----------
        bias : float
            Detector bias voltage in V

        Returns
        -------
        float
        Capacitance in F
        """
        if self._bias_to_node is None:
            raise ValueError("'bias_to_node_func' must be provided.")

        return self._bias_to_node(bias)

    def to_dict(self) -> Mapping:
        """Get the attributes of this instance as a `dict`."""
        dct = {
            "roic_gain": self._roic_gain,
            "bias_to_node": self._bias_to_node.to_dict(),  # TODO: FIx this
            "avalanche_settings": self._avalanche_settings.to_dict(),
            "quantum_efficiency": self._quantum_efficiency,
            "full_well_capacity": self._full_well_capacity,
            "adc_bit_resolution": self._adc_bit_resolution,
            "adc_voltage_range": self._adc_voltage_range,
        }
        return dct

    @classmethod
    def from_dict(cls, dct: Mapping) -> Self:
        """Create a new instance from a `dict`."""
        # Late import to speedup start-up time
        from toolz import dicttoolz

        from pyxel.configuration.configuration import build_converter

        adc_voltage_range = dct["adc_voltage_range"]

        if adc_voltage_range is not None:
            adc_voltage_range = tuple(adc_voltage_range)

        bias_to_node = build_converter(dct["bias_to_node"])
        avalanche_settings: AvalancheSettings = AvalancheSettings.from_dict(
            dct["avalanche_settings"]
        )

        new_dct: Mapping = dicttoolz.dissoc(
            dct, "adc_voltage_range", "bias_to_node", "avalanche_settings"
        )

        return cls(
            adc_voltage_range=adc_voltage_range,
            bias_to_node=bias_to_node,
            avalanche_settings=avalanche_settings,
            **new_dct,
        )
