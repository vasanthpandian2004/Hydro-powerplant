"""
The ``modelchain`` module contains functions and classes of the
hydropowerlib. This module makes it easy to get started with the hydropowerlib
and demonstrates standard ways to use the library.

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"

import logging
import sys
import os
import pandas as pd
import numpy as np
import datetime

from . import power_output
from . import estimate

logger = logging.getLogger(__name__)


class Modelchain(object):
    """Model to determine the output of a hydropower plant

    Parameters
    ----------
    hpp : HydropowerPlant
        A :class:`~.hydropower_plant.HydropowerPlant` object representing the hydropower
        plant.
    dV : pandas.DataFrame
        Containing DateTime index and column with water flow `dV` in m3/s over the period to simulate
    dV_hist : pandas.DataFrame
        Containing DateTime index and column with water flow `dV` in m3/s over several past years.
        Used to extrapolate the missing values about the plant.
    file_turb_eff : string
        Name of the file containing parameters about the turbine efficiency.
    file_turb_graph :
        Name of the file containing the characteristic diagrams.

    Attributes
    ----------
    hpp : HydropowerPlant
        A :class:`~.hydropower_plant.HydropowerPlant` object representing the hydropower
        plant.
    dV : pandas.DataFrame
        Containing DateTime index and column with water flow `dV` in m3/s over the period to simulate
    dV_hist : pandas.DataFrame
        Containing DateTime index and column with water flow `dV` in m3/s over several past years.
        Used to extrapolate the missing values about the plant.
    file_turb_eff : string
        Name of the file containing parameters about the turbine efficiency.
    file_turb_graph :
        Name of the file containing the characteristic diagrams.

    Examples
    --------
    >>> from hydropowerlib import modelchain, hydropower_plant
    >>> example_plant = {
    ...    'name': "Raon",
    ...    'H_n': 4.23,
    ...    'Q_n': 12,
    ...    'turbine_type': 'Kaplan'}
    >>> example = HydropowerPlant(**example_plant)
    >>> modelchain_data = {'dV': df_runoff, 'dV_hist': df_dV_hist}
    >>> example_md = modelchain.Modelchain(example, **modelchain_data)
    >>> print(example.H_n)
    4.23

    """

    def __init__(self, hpp, dV, dV_hist=None, file_turb_eff=None, file_turb_graph=None):

        self.hpp = hpp
        self.dV = dV
        self.dV_hist = dV_hist

        self.file_turb_eff = file_turb_eff
        self.file_turb_graph = file_turb_graph


    def run_model(self):
        r"""
        Runs the model and fills power_output on power_output attribute

        Returns
        -------
        self : Modelchain
        """

        estimate.missing_parameters(self.hpp, self.dV_hist, self.file_turb_graph)
        self.hpp.load_turb_params(self.file_turb_eff)

        self.power_output = power_output.characteristic_equation(self.hpp, self.dV)
        return self

