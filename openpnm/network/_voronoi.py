from openpnm.network import Network
from openpnm.utils import Docorator
from openpnm._skgraph.generators import voronoi


docstr = Docorator()
__all__ = ['Voronoi']


@docstr.dedent
class Voronoi(Network):
    r"""
    Random network formed by Voronoi tessellation of arbitrary base points.

    Parameters
    ----------
    points : array_like or int
        Can either be an N-by-D array of point coordinates which will be
        used directly, or a scalar value indicating the number of points to
        generate.  If 3D points are supplied, and a 2D shape is specified, then
        the z-coordinate is ignored.See *Notes* for more details.
    shape : array_like
        The size and shape of the domain:

        ========== ============================================================
        shape      result
        ========== ============================================================
        [x, y, z]  A 3D cubic domain of dimension x, y and z
        [x, y, 0]  A 2D square domain of size x by y
        ========== ============================================================

    trim : bool, optional
        If ``True`` (default) then all Voronoi vertices laying outside the domain
        will be removed.
    reflect : bool, optional
        If ``True`` (default) then the base points will be reflected across
        all the faces of the domain prior to performing the tessellation. This
        feature is best combined with ``trim=True`` to make nice flat faces
        on all sides of the domain.

    %(Network.parameters)s

    Notes
    -----
    These points are used by the Voronoi tessellation, meaning these points will
    each lie in the center of a Voronoi cell, so they will not be the pore centers.
    The number of pores in the returned network will greater that the number of
    points supplied or requested.

    It is also possible to generate circular ``[r, 0]``, cylindrical ``[r, z]``, and
    spherical domains ``[r]``, but this feature does not quite work as desired.
    It does not produce a truly clean outer surface since the tessellation are
    conducted in cartesian coordinates, so the circular and spherical surfaces
    have artifacts. Scipy recently added the ability to do tessellations on
    spherical surfaces, for geological applications, but this is not flexible
    enough, yet.

    """

    def __init__(self, shape, points, trim=True, reflect=True, **kwargs):
        super().__init__(**kwargs)
        net, vor = voronoi(points=points,
                           shape=shape,
                           trim=trim,
                           node_prefix='pore',
                           edge_prefix='throat')
        self.update(net)
        self.vor = vor
