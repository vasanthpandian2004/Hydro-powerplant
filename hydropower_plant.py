"""
The ``hydropower_plant`` module contains the class HydropowerPlant that implements
a run-of-the-river hydropower plant in the hydropowerlib and functions needed for the modelling of a
hydropower plant.

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"

import os
import pandas as pd

from pkg_resources import resource_stream

class HydropowerPlant(object):
    r"""
    Defines a standard set of hydropower plant attributes.

    Parameters
    ----------
    name : string
        Name of the plant
    P_n : float
        Nominal power of the plant in W
        In case of multiple turbines, this is the sum of the nominal power of each turbine.
    dV_n : float
        Nominal water flow entering the plant in m3/s.
        In case of multiple turbines, this is the sum of the nominal inflows in each turbine.
    h_n : float
        Nominal head of water in m.
    dV_res : float
        Part of the water flow that cannot be used (fish ladder, compulsory minimal water flow leaving the plant...)
    turb_type : string
        Type of the turbine(s). All turbines of the same plant have to be the same type.
    turb_num : int
        Number of turbines in the power plant. Default : 1


    Attributes
    ----------
    name : string
        Name of the plant
    P_n : float
        Nominal power of the turbine
    dV_n : float
        Nominal water flow entering the plant in m3/s.
    h_n : float
        Nominal head of water in m.
    dV_res : float
        Part of the water flow that cannot be used (fish ladder, compulsory minimal water flow leaving the plant...)
    turb_type : string
        Type of the turbine.
    turb_num : int
        Number of turbines in the power plant. Default : 1
    power_output : pandas.Series
        The calculated power output of the hydropower plant.

    Examples
    --------
    >>> from hydropowerlib import HydropowerPlant
    >>> example_plant = {
    ...    'name': 'Raon',
    ...    'h_n': 4.23,
    ...    'dV_n': 12,
    ...    'turbine_type': 'Kaplan'}
    >>> example = HydropowerPlant(**example_plant)
    >>> print(example.dV_n)
    12

    """

    def __init__(self, name, P_n=None, dV_n=None, h_n=None, dV_res=None, turb_type=None, turb_num=1):

        self.name = name
        self.P_n = P_n
        self.dV_n = dV_n
        self.h_n = h_n
        self.dV_res = dV_res
        self.turb_type = turb_type
        self.turb_num = turb_num
        self.turb_params = None

        self.power_output = None

    def load_turb_params(self, file_turb_eff=None):
        """

        """
        if file_turb_eff is None:
            file_turb_eff = resource_stream(__name__, 'data/turbine_type.csv')
        else:
            file_turb_eff = os.path.join(os.path.dirname(__file__), 'data', file_turb_eff)

        df = pd.read_csv(file_turb_eff, index_col=0)
        try:
            self.turb_params = df.loc[self.turb_type]
        except KeyError:
            available_types = ", ".join(df.index)
            raise KeyError(f"Turbine type {self.turb_type} is not in {file_turb_eff} ({available_types})")
