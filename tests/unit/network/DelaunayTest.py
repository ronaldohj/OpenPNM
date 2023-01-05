import numpy as np
import openpnm as op


class DelaunayGabrielTest:
    def setup_class(self):
        pass

    def teardown_class(self):
        pass

    def test_delaunay_square_with_2D_points(self):
        np.random.seed(0)
        pts = np.random.rand(50, 2)
        tri = op.network.Delaunay(points=pts, shape=[1, 1, 0])
        assert tri.coords.shape == (50, 3)
        assert np.all(tri.coords[:, :2] == pts)

    def test_delaunay_square_with_3D_points(self):
        np.random.seed(0)
        pts = np.random.rand(50, 3)
        tri = op.network.Delaunay(points=pts, shape=[1, 1, 0])
        assert tri.coords.shape == (50, 3)
        assert np.all(tri.coords[:, :2] == pts[:, :2])
        assert np.all(tri.coords[:, -1] != pts[:, -1])
        assert np.all(tri.coords[:, -1] == 0.0)

    def test_delaunay_cube_with_points(self):
        np.random.seed(0)
        pts = np.random.rand(50, 3)
        tri = op.network.Delaunay(points=pts, shape=[1, 1, 1])
        assert tri.coords.shape == (50, 3)
        assert np.all(tri.coords == pts)

    def test_delaunay_disk_with_2D_points(self):
        np.random.seed(0)
        pts = np.random.rand(50, 2)
        tri = op.network.Delaunay(points=pts, shape=[1, 0])
        assert tri.coords.shape == (50, 3)
        assert np.all(tri.coords[:, :2] == pts[:, :2])
        assert np.all(tri.coords[:, -1] != pts[:, -1])
        assert np.all(tri.coords[:, -1] == 0.0)

    def test_delaunay_disk_with_3D_points(self):
        np.random.seed(0)
        pts = np.random.rand(50, 3)
        tri = op.network.Delaunay(points=pts, shape=[1, 1])
        assert tri.coords.shape == (50, 3)
        assert np.all(tri.coords == pts)

    def test_delaunay_cylinder_with_points(self):
        np.random.seed(0)
        pts = np.random.rand(50, 3)
        tri = op.network.Delaunay(points=pts, shape=[1, 1])
        assert tri.coords.shape == (50, 3)
        assert np.all(tri.coords == pts)


if __name__ == '__main__':

    t = DelaunayGabrielTest()
    t.setup_class()
    self = t
    for item in t.__dir__():
        if item.startswith('test'):
            print('running test: '+item)
            t.__getattribute__(item)()