#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.


"""Readout noise model."""

import numpy as np

from pyxel.detectors import CMOS
from pyxel.util import set_random_seed


def create_noise_cmos(
    shape: tuple[int, int],
    readout_noise: float,
    readout_noise_std: float,
    charge_readout_sensitivity: float | np.ndarray,
) -> np.ndarray:
    """Create noise to signal array for :term:`CMOS` detectors.

    Parameters
    ----------
    shape : tuple[int, int]
        The shape of the detector array (rows, columns).
    readout_noise : float
        The mean readout noise level per pixel.
    readout_noise_std : float
        The standard deviation of the readout noise
    charge_readout_sensitivity : float | dict[str, float]
        Charge readout sensitivity could be a scalar or a 2D array.

    Returns
    -------
    ndarray
        The generated 2D noise array.
    """
    # Create an array for sensitivities that matches the detector's shape
    if not isinstance(charge_readout_sensitivity, np.ndarray):
        sensitivity_2d = np.full(shape=shape, fill_value=charge_readout_sensitivity)
    else:
        sensitivity_2d = charge_readout_sensitivity

    # Generate the noise based on the calculated sensitivities
    noise_mean_2d = readout_noise * sensitivity_2d
    noise_std_2d = readout_noise_std * sensitivity_2d

    # Generate the noise with Gaussian distribution
    sigma_2d = np.random.normal(loc=noise_mean_2d, scale=noise_std_2d, size=shape)
    sigma_2d = sigma_2d.clip(min=0.0)  # Ensure noise values are non-negative

    # TODO: Is it correct ?
    noise_2d = np.random.normal(scale=sigma_2d)

    return noise_2d


def output_node_noise_cmos(
    detector: CMOS,
    readout_noise: float,
    readout_noise_std: float,
    seed: int | None = None,
) -> None:
    """Output node noise model for :term:`CMOS` detectors where readout is statistically independent for each pixel.

    Parameters
    ----------
    detector : CMOS
        Pyxel :term:`CMOS` object.
    readout_noise : float
        Mean readout noise for the array in units of electrons. Unit: electron
    readout_noise_std : float
        Readout noise standard deviation in units of electrons. Unit: electron
    seed : int, optional
        Random seed.

    Raises
    ------
    TypeError
        Raised if the 'detector' is not a :term:`CMOS` object.
    ValueError
        Raised if 'readout_noise_std' is negative.
    """
    if not isinstance(detector, CMOS):
        raise TypeError("Expecting a 'CMOS' detector object.")

    if readout_noise_std < 0.0:
        raise ValueError("'readout_noise_std' must be positive.")

    charge_readout_sensitivity = detector.characteristics.channels_gain
    # if isinstance(detector.characteristics.charge_to_volt_conversion, (float, int)):
    #     charge_readout_sensitivity[:] = detector.characteristics.charge_to_volt_conversion
    # elif isinstance(detector.characteristics.charge_to_volt_conversion, dict):
    #     # Apply channel-specific sensitivities
    #     for channel, gain in detector.characteristics.charge_to_volt_conversion.items():
    #         slice_y, slice_x = detector.geometry.get_channel_coord(channel)
    #         charge_readout_sensitivity[slice_y, slice_x] = gain
    # else:
    #     raise NotImplementedError(
    #         "Expecting a float or dict for charge_to_volt_conversion; got unexpected type."
    #     )

    with set_random_seed(seed):
        noise_2d: np.ndarray = create_noise_cmos(
            shape=detector.signal.shape,
            readout_noise=readout_noise,
            readout_noise_std=readout_noise_std,
            charge_readout_sensitivity=charge_readout_sensitivity,
        )

    detector.signal.array += noise_2d
