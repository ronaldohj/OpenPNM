import pickle
import openpnm
import time
import copy
from openpnm.core import logging
from openpnm.utils import Settings
logger = logging.getLogger()


def singleton(cls):
    r'''
    This is based on PEP318
    '''
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance


@singleton
class Workspace(dict):

    def __init__(self):
        super().__init__()
        self.comments = 'Using OpenPNM ' + openpnm.__version__
        self.settings = Settings()

    def _setloglevel(self, level):
        logger.setLevel(level)

    def _getloglevel(self):
        return 'Log level is currently set to: ' + str(logger.level)

    loglevel = property(fget=_getloglevel, fset=_setloglevel)

    def _create_console_handles(self, simulation):
        r"""
        Adds all objects in the given Simulation to the console as variables
        with handle names taken from each object's name.
        """
        import __main__
        for item in simulation:
            __main__.__dict__[item.name] = item

    def save_simulation(self, simulation, filename=''):
        r"""
        Save a single simulation to a 'net' file, including all of its
        associated objects, but not Algorithms

        Parameters
        ----------
        simulation : OpenPNM Network object
            The Network to save

        filename : string, optional
            If no filename is given the name of the Network is used
        """
        if filename == '':
            filename = simulation.name
        else:
            filename = filename.rsplit('.net', 1)[0]

        # Save nested dictionary pickle
        pickle.dump(simulation, open(filename + '.net', 'wb'))

    def load_simulation(self, filename):
        r"""
        Loads a Simulation from the specified 'net' file and adds it
        to the Workspace

        Parameters
        ----------
        filename : string
            The name of the file containing the Network simulation to load
        """
        filename = filename.rsplit('.net', 1)[0]
        sim = pickle.load(open(filename + '.net', 'rb'))
        if sim.name not in self.keys():
            self[sim.name] = sim
        else:
            raise Exception('A simulation with that name is already present')

    def close_simulation(self, simulation):
        r"""
        """
        del self[simulation.name]

    def copy_simulation(self, simulation, new_name=None):
        r"""
        Make a copy of an existing Simulation object

        Parameters
        ----------
        simulation : Simulation object
            The Simulation object to be copied

        name : string, optional
            A name for the new copy of the Simulation.  If not supplied, then
            one will be generated (e.g. 'sim_02')

        Returns
        -------
        The new Simulation object

        """
        new_sim = copy.deepcopy(simulation)
        new_sim._name = hex(id(new_sim))  # Assign temporary name
        new_sim.name = new_name
        return new_sim

    def new_simulation(self, name=None):
        r"""
        Creates a new, empty simulation object

        Parameters
        ----------
        name : string (optional)
            The unique name to give to the Simulation.  If none is given, one
            will be automatically generated (e.g. 'sim_01`)

        Returns
        -------
        An empty Simulation object, suitable for passing into a Network
        generator

        """
        sim = openpnm.core.Simulation(name=name)
        return sim

    def import_data(self, filename):
        r"""
        """
        raise NotImplementedError()

    def export_data(self, network, phases=[], filename=None, filetype='vtp'):
        r"""
        Export the pore and throat data from the given object(s) into the
        specified file and format.

        Parameters
        ----------
        network: OpenPNM Network Object
            The network containing the data to be stored

        phases : list of OpenPNM Phase Objects
            The data on each supplied phase will be added to file

        filename : string
            The file name to use.  If none is supplied then one will be
            automatically generated based on the name of the Simulation
            containing the supplied Network, with the date and time appended.

        filetype : string
            Which file format to store the data.  Option are:

            **'vtk'** : (default) The Visualization Toolkit format, used by
            various softwares such as Paraview.  This actually produces a 'vtp'
            file.  NOTE: This can be quite slow since all the data is written
            to a simple text file.  For large data simulations consider
            'xdmf'.

            **'csv'** : The comma-separated values format, which is easily
            openned in any spreadsheet program.  The column names represent
            the property name, including the type and name of the object to
            which they belonged, all separated by the pipe character.

            **'xmf'** : The extensible data markup format, is a very efficient
            format for large data sets.  This actually results in the creation
            of two files, the *xmf* file and an associated *hdf* file.  The
            *xmf* file contains instructions for looking into the *hdf* file.
            Paraview opens the *xmf* format natively, and is very fast.  NOTE:
            This is using *xmf* version 2.

            **'mat'** : Matlab 'mat-file', which can be openned in Matlab as
            a structured variable, with field names corresponding to the
            property names.

        Notes
        -----
        This is a helper function for the actual functions in the IO module.
        For more control over the format of the output, and more information
        about the format refer to ``openpnm.io``.

        """
        simulation = network.simulation
        if filename is None:
            filename = simulation.name + '_' + time.strftime('%Y%b%d_%H%M%p')
        if filetype.lower() in ['vtp', 'vtp', 'vtu']:
            openpnm.io.VTK.save(network=network, phases=phases,
                                filename=filename)
        if filetype.lower() == 'csv':
            openpnm.io.CSV.save(network=network, phases=phases,
                                filename=filename)
        if filetype.lower() in ['xmf', 'xdmf']:
            openpnm.io.XDMF.save(network=network, phases=phases,
                                 filename=filename)
        if filetype.lower() in ['hdf5', 'hdf', 'h5']:
            f = openpnm.io.HDF5.to_hdf5(network=network, phases=phases,
                                        filename=filename)
            f.close()
        if filetype.lower() == 'mat':
            openpnm.io.MAT.save(network=network, phases=phases,
                                filename=filename)

    def _gen_name(self):
        r"""
        Generates a valid name for simulations
        """
        n = [0]
        for item in self.keys():
            if item.startswith('sim_'):
                n.append(int(item.split('sim_')[1]))
        name = 'sim_'+str(max(n)+1).zfill(2)
        return name

    def _set_comments(self, string):
        if hasattr(self, '_comments') is False:
            self._comments = {}
        self._comments[time.strftime('%c')] = string

    def _get_comments(self):
        if hasattr(self, '_comments') is False:
            self._comments = {}
        for key in list(self._comments.keys()):
            print(key, ': ', self._comments[key])

    comments = property(fget=_get_comments, fset=_set_comments)

    def __str__(self):
        s = []
        hr = '―'*78
        s.append(hr)
        for item in self.values():
            s.append(' ' + item.name)
            s.append(item.__str__())
        return '\n'.join(s)
