from openpnm.utils import Docorator
import numpy as np


docstr = Docorator()


__all__ = [
    "ideal_gas",
    "water_correlation",
    "liquid_mixture",
    "liquid_pure",
    "mass_to_molar",
]


def ideal_gas(
    target,
    P='pore.pressure',
    T='pore.temperature',
    MW='param.molecular_weight',
):
    r"""
    Uses ideal gas law to calculate the mass density of an ideal gas

    Parameters
    ----------
    %(models.target.parameters)s
    %(models.phase.T)s
    %(models.phase.P)s
    mol_weight : str
        Name of the dictionary key on ``target`` where the array containing
        molecular weight values is stored

    Returns
    -------
    %(models.phase.density.returns)s

    """
    P = target[P]
    T = target[T]
    try:
        # If target is a pure species, it should have molecular weight in params
        MW = target[MW]
    except KeyError:
        # Otherwise, get the mole weighted average value
        MW = target.get_mix_vals(MW)
    R = 8.314462618  # J/(mol.K)
    value = P/(R*T)*(MW/1000)  # Convert to kg/m3
    return value


def water_correlation(
    target,
    T='pore.temperature',
    salinity='pore.salinity',
):
    r"""
    Calculates density of pure water or seawater at atmospheric pressure
    using Eq. (8) given by Sharqawy et. al [1]. Values at temperature higher
    than the normal boiling temperature are calculated at the saturation
    pressure.

    Parameters
    ----------

    Returns
    -------
    %(models.phase.density.returns)s

    Notes
    -----
     T must be in K, and S in g of salt per kg of phase, or ppt (parts per
        thousand)
    VALIDITY: 273 < T < 453 K; 0 < S < 160 g/kg;
    ACCURACY: 0.1 %

    References
    ----------
    [1] Sharqawy M. H., Lienhard J. H., and Zubair, S. M., Desalination and
    Water Treatment, 2010.

    """
    T = target[T]
    if salinity in target.keys():
        S = target[salinity]
    else:
        S = 0
    a1 = 9.9992293295E+02
    a2 = 2.0341179217E-02
    a3 = -6.1624591598E-03
    a4 = 2.2614664708E-05
    a5 = -4.6570659168E-08
    b1 = 8.0200240891E-01
    b2 = -2.0005183488E-03
    b3 = 1.6771024982E-05
    b4 = -3.0600536746E-08
    b5 = -1.6132224742E-11
    TC = T-273.15
    rho_w = a1 + a2*TC + a3*TC**2 + a4*TC**3 + a5*TC**4
    d_rho = b1*S + b2*S*TC + b3*S*(TC**2) + b4*S*(TC**3) + b5*(S**2)*(TC**2)
    rho_sw = rho_w + d_rho
    value = rho_sw
    return value


def liquid_mixture(
    target,
    T='pore.temperature',
    MWs='param.molecular_weight.*',
    Tcs='param.critical_temperature.*',
    Vcs='param.critical_volume.*',
    omegas='param.acentric_factor.*',
):
    r"""
    Computes the density of a liquid mixture using the COrrospoding STAtes
    Liquid Density (COSTALD) method.

    Parameters
    ----------


    Returns
    -------
    density : ndarray
        The density of the liquid mixture in units of kg/m3.  Note that
        ``chemicals.volume.COSTALD`` returns molar volume, so this function
        converts it to density using the mole fraction weighted molecular
        weight of the mixture: :math:`MW_{mix} = \Sigma x_i \cdot MW_i`.

    Notes
    -----
    This is same approach used by ``chemicals.volume.COSTALD_mixture`` and
    exact numerical correspondance is confirmed. Unlike the ``chemicals``
    version, this function is vectorized over the conditions rather than
    the compositions, since a typical simulation has millions of pores each
    representing an independent conditions, but a mixture typically only has
    a few components.

    """
    # Fetch parameters for each pure component
    Tcs = target.get_comp_vals(Tcs)
    Vcs = target.get_comp_vals(Vcs)
    omegas = target.get_comp_vals(omegas)
    Xs = target['pore.mole_fraction']
    # Compute mixture values
    omegam = np.vstack([Xs[k]*omegas[k] for k in Xs.keys()]).sum(axis=0)
    Vm1 = np.vstack([Xs[k]*Vcs[k] for k in Xs.keys()]).sum(axis=0)
    Vm2 = np.vstack([Xs[k]*(Vcs[k])**(2/3) for k in Xs.keys()]).sum(axis=0)
    Vm3 = np.vstack([Xs[k]*(Vcs[k])**(1/3) for k in Xs.keys()]).sum(axis=0)
    Vm = 0.25*(Vm1 + 3*Vm2*Vm3)
    Tcm = 0.0
    for i, ki in enumerate(Xs.keys()):
        inner = 0.0
        for j, kj in enumerate(Xs.keys()):
            inner += Xs[ki]*Xs[kj]*(Vcs[ki]*Tcs[ki]*Vcs[kj]*Tcs[kj])**0.5
        Tcm += inner
    Tcm = Tcm/Vm
    # Convert molar volume to normal mass density
    MWs = target.get_comp_vals('param.molecular_weight')
    MWm = np.vstack([Xs[k]*MWs[k] for k in Xs.keys()]).sum(axis=0)
    T = target[T]
    rhoL = liquid_pure(
        target=target,
        T=T,
        MW=MWm,
        Tc=Tcm,
        Vc=Vm,
        omega=omegam,
    )
    return rhoL


def liquid_pure(
    target,
    T='pore.temperature',
    Tc='param.critical_temperature',
    Vc='param.critical_volume',
    omega='param.acentric_factor',
    MW='param.molecular_weight',
):
    r"""
    """
    Vc = target[Vc]
    Tc = target[Tc]
    omega = target[omega]
    T = target[T]
    Tr = T/Tc
    V0 = 1 - 1.52816*(1-Tr)**(1/3) + 1.43907*(1-Tr)**(2/3) - 0.81446*(1-Tr) + \
        0.190454*(1-Tr)**(4/3)
    V1 = (-0.296123 + 0.386914*Tr - 0.0427258*Tr**2 - 0.0480645*Tr**3)/(Tr - 1.00001)
    Vs = Vc*V0*(1-omega*V1)
    MW = target[MW]
    rhoL = 1e-3*MW/Vs
    return rhoL


def mass_to_molar(
    target,
    MW='param.molecular_weight',
    rho='pore.density',
):
    r"""
    Calculates the molar density from the molecular weight and mass density

    Parameters
    ----------
    %(models.target.parameters)s
    mol_weight : str
        The dictionary key containing the molecular weight in kg/mol
    density : str
        The dictionary key containing the density in kg/m3

    Returns
    -------
    value : ndarray
        A numpy ndrray containing molar density values [mol/m3]

    """
    MW = target[MW]
    rho = target[rho]
    value = rho/MW
    return value
