"""
The ``estimate`` module contains functions used from the modelchain to extend
the parameters of a HydroPowerplant using historical river flow data.
"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"

import logging
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

from pkg_resources import resource_stream

logger = logging.getLogger(__name__)

def missing_parameters(hpp, dV_hist=None, file_turb_graph=None):
    if not can_estimate(hpp, dV_hist):
        logger.error(f'The input data is not sufficient for plant {hpp.name}')
        raise RuntimeError(f'The input data is not sufficient for plant {hpp.name}')

    if hpp.dV_res is None:
        dV_res_from_dV_hist(hpp, dV_hist)
    if hpp.dV_n is None:
        dV_n_from_dV_hist(hpp, dV_hist)
    if hpp.P_n is None != hpp.h_n is None:
        P_n_or_h_n_from_characteristic_equation_at_nominal_load(hpp)
    if hpp.turb_type is None:
        turb_type_from_phase_diagram(hpp, file_turb_graph)

    eta_g_n_from_P_n(hpp)

    logger.debug(f'''
        Plant {hpp.name}
        ----------------
        Nominal water flow  : {hpp.dV_n} m3/s
        Nominal head        : {hpp.h_n} m
        Nominal power       : {hpp.P_n} W
        Residual water flow : {hpp.dV_res} m3/s
        Turbine type        : {hpp.turb_type}
    ''')

def can_estimate(hpp, dV_hist=None):
    """
    Test if the input data is sufficient to simulate the plant

    The simulation is feasible if two parameters among `dV_n`, `h_n` and
    `P_n` are known. If dV_n is not known, it can be extrapolated from
    dV_hist.

    The logical expression verifying the feasibility is
    `(h_n and P_n) or ((h_n or P_n) and (dV_hist or dV_n))`

    """
    return (((hpp.h_n is not None) and (hpp.P_n is not None)) or
            (((hpp.h_n is not None) or (hpp.P_n is not None)) and
             ((dV_hist is not None) or (hpp.dV_n is not None))))

def dV_res_from_dV_hist(hpp, dV_hist):
    """
    Estimate value for residual flow volume dV_res

    dV_res is calculated from the mean flow duration curve over the historic flow volume `dV_hist`.
    If dV_hist is not given, dV_res is set to 0.

    Returns
    -------
    dV_res : float

    References
    ----------
    [1] Bundesamt für Konjunkturfragen. Wahl, Dimensionierung und Abnahme einer Kleinturbine, 1995.
    """
    if dV_hist is None:
        return 0

    # Select last 10 years
    start_from = max(dV_hist.index[0], dV_hist.index[-1] - pd.tseries.offsets.DateOffset(years=10))
    dV_hist = dV_hist.loc[start_from:]

    # Averaged yearly profile
    dV_mean = dV_hist.groupby(dV_hist.index.dayofyear).mean()

    # 0.05 quantile <-> 347 day in flow duration curve
    dV_347 = dV_mean.quantile(0.05)

    if dV_347 <= 0.06:
        hpp.dV_res = 0.05
    elif dV_347 <= 0.16:
        hpp.dV_res = 0.05 + (dV_347 - 0.06) * 8 / 10
    elif dV_347 <= 0.5:
        hpp.dV_res = 0.130 + (dV_347 - 0.16) * 4.4 / 10
    elif dV_347 <= 2.5:
        hpp.dV_res = 0.28 + (dV_347 - 0.5) * 31 / 100
    elif dV_347 <= 10:
        hpp.dV_res = 0.9 + (dV_347 - 2.5) * 21.3 / 100
    elif dV_347 <= 60:
        hpp.dV_res = 2.5 + (dV_347 - 10) * 150 / 1000
    else:
        hpp.dV_res = 10

    return hpp.dV_res

def dV_n_from_dV_hist(hpp, dV_hist):
    """
    Estimate the nominal water flow through the turbine `dV_n`

    dV_n is calculated from the flow duration curve over several years, after
    subtracting dV_res as the the water flow reached or exceeded 20% of the
    time, ie the 0.8 quantile.

    Returns
    -------
    dV_n : float
    """

    hpp.dV_n = (dV_hist - hpp.dV_res).quantile(0.8)

    return hpp.dV_n

def P_n_or_h_n_from_characteristic_equation_at_nominal_load(hpp):
    """
    Estimate value for `P_n` or `h_n` from characteristic equation

    P_n = h_n*dV_n*g*rho*eta_g_n*eta_t_n

    Where g=9.81 m/s², rho=1000 kg/m³,
          eta_g_n=0.95 (nominal generator efficiency) and
          eta_t_n (nominal turbine efficiency)=0.9
    """
    assert (hpp.h_n is not None or hpp.P_n is not None) and hpp.dV_n is None, "h_n and dV_n must be known for estimating P_n"

    eta_g_n = 0.95  # Assumed as 0.95
    eta_t_n = 0.9   # At full load the same for all turbine types

    if hpp.h_n is None:
        hpp.h_n = hpp.P_n/(hpp.dV_n * 9.81 * 1000 * eta_g_n * eta_t_n)
    elif hpp.P_n is None:
        hpp.P_n = hpp.h_n * hpp.dV_n * 9.81 * 1000 * eta_g_n * eta_t_n

def eta_g_n_from_P_n(hpp):
    r"""
    Calculate the nominal efficiency of the generator based on the nominal power of the plant

    References
    ----------
    [1] Bundesamt für Konjunkturfragen. Wahl, Dimensionierung und Abnahme einer Kleinturbine, 1995.
    """
    P_n = hpp.P_n

    if P_n < 1000:
        eta_g_n = 80
    elif P_n < 5000:
        eta_g_n = 80 + (P_n - 1000) / 1000 * 5 / 4
    elif P_n < 20000:
        eta_g_n = 85 + (P_n - 5000) / 1000 * 5 / 15
    elif P_n < 100000:
        eta_g_n = 90 + (P_n - 20000) / 1000 * 5 / 80
    else:
        eta_g_n = 95

    hpp.eta_g_n = eta_g_n / 100

    return hpp.eta_g_n

def turb_type_from_phase_diagram(hpp, file_turb_graph=None):
    """
    Estimate turbine type based on h_n/dV_n characteristic diagram

    Fetches type of the requested hydropower turbine by situating it on a
    h_n/dV_n characteristic diagram of different turbines. The
    characteristic zones of each turbine are polygons in a dV_n / h_n plan
    and are defined by their angles.

    The characteristic diagram is loaded from a geojson file and the first
    matching turbine type is returned.

    Returns
    -------
    turb_type : str
        Turbine type

    Notes
    -----
    turbines.geojson is generated by `utils/extract_turbines_wikipedia.py`
    based on turbine specifications shared on wikipedia as matlab files.

    References
    ----------
    [2] https://de.wikipedia.org/wiki/Datei:Kennfeld_Wasserturbinen.svg
    """

    if file_turb_graph is None:
        file_turb_graph = resource_stream(__name__, 'data/turbines.geojson')
    else:
        file_turb_graph = os.path.join(os.path.dirname(__file__), 'data', file_turb_graph)

    try:
        turbines = gpd.read_file(file_turb_graph)
    except IOError:
        logger.info(f'No file {file_turb_graph} in data folder')
        raise

    matching_turbines = turbines.loc[turbines.contains(Point(hpp.dV_n, hpp.h_n))]

    if matching_turbines.empty:
        hpp.turb_type = 'dummy'
        logger.warning(f'Turbine type could not be defined for plant {hpp.name}. Dummy type used')
    else:
        hpp.turb_type = matching_turbines.id.iloc[0]

    return hpp.turb_type
