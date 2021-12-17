from openpnm.phase import mixtures
import openpnm.models as mods


class O2(mixtures.GenericSpecies):
    r"""
    Creates Phase object with preset models and values for O2 gas

    Parameters
    ----------
    network : GenericNetwork
        The network to which this phase object will be attached.
    name : str, optional
        The name of the phase.  This is useful to keep track of the objects
        throughout the simulation.  The name must be unique to the project.  If
        no name is given, one is generated.

    Examples
    --------
    >>> import openpnm as op
    >>> import openpnm.phase.mixtures as mixtures
    >>> pn = op.network.Cubic(shape=[5, 5, 5])
    >>> O2 = mixtures.species.gases.O2(network=pn)

    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pop('pore.temperature', None)
        self.pop('pore.pressure', None)

        self['pore.molecular_weight'] = 0.032  # kg/mol
        self['pore.molar_diffusion_volume'] = 16.6  # ??