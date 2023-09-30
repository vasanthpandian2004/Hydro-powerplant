"""
The ``power_output`` module contains functions to calculate the power output
of a hydropower plant.

"""

import numpy as np
import pandas as pd
import os
import logging
import sys

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"


def eta_g_eff(dV_pu, eta_g_n):
    r"""
    Determine efficiency of generator based on the part load and the nominal efficiency.

    Parameters
    ----------
    dV_pu : pd.Series
        load of the generator in values of P_n
    eta_g_n : float
        nominal efficiency of the generator

    Returns
    -------
    eta_g_eff : pd.Series

    References
    ----------
    [1] Bundesamt für Konjunkturfragen. Wahl, Dimensionierung und Abnahme einer Kleinturbine, 1995.

    """
    return pd.Series(np.interp(dV_pu, [0.1, 0.25, 0.5], [0.85, 0.95, 1.], left=0.85, right=1.) * eta_g_n, dV_pu.index)


def characteristic_equation(hpp, dV):
    r"""
    Calculates the plant power output.

    Parameters
    ----------
    hpp : instance of the :class:`~.hydropower_plant.HydropowerPlant` class
        Specifications of the hydropower plant
    dV : pandas.Series
        Water flow in m3/s.

    Returns
    -------
    pandas.Series
        Electrical power output of the hydropower plant in W.

    Notes
    -----
    The following equation is used [1]_:

    .. math:: P=\eta_{turbine}\cdot\eta_{generator}\cdot g\cdot\rho_{water}\cdot min(dV,dV_{n})\cdot h_{n}


    with:
        P: power [W], :math:`\rho_{water}`: density [kg/m³], g: standard gravity [m/s2],
        dV: water flow [m3/s], :math:`dV_{n}`: nominal water flow [m3/s],
        :math:`h_{n}`: nominal head of water [m], :math:`\eta_{turbine}`: efficiency of the turbine [],
        :math:`\eta_{generator}`: efficiency of the generator []

    It is assumed that the efficiency for water flows above the maximum
    water flow given in the efficiency curve is the nominal efficiency
    (the water surplus will be drained over the dam)

    References
    ----------
    .. [1] Quaschning, V.: "Regenerative Energiesysteme". 9. Auflage, München,
           Hanser, 2015, page 333


    """

    dV = (dV - hpp.dV_res).clip(lower=0.)

    dV_pu = dV / hpp.dV_n
    eta_g = eta_g_eff(dV_pu, hpp.eta_g_n)

    a1, a2, a3 = hpp.turb_params.loc[["a1", "a2", "a3"]]
    eta_t = dV_pu / (a1 + a2 * dV_pu + a3 * dV_pu**2)

    power_output = (eta_t * eta_g * 9.81 * 1000 * dV * hpp.h_n).where(dV_pu < 1., other=hpp.P_n)

    return power_output.rename("feedin_hydropower_plant")

