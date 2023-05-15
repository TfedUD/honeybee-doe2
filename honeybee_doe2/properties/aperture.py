# -*- coding: utf-8 -*-

import math

from ladybug_geometry.geometry3d.face import Face3D, Vector3D, Point2D, Plane, \
    Polygon2D, Mesh2D
from ..utils.doe_formatters import short_name


class Window:
    def __init__(self, aperture, parent):
        self.aperture = aperture
        self.parent = parent

    def to_inp(self, resolution=0.5):
        """
        Args:
            resolution: The resolution size for breaking down the non-rectangular
                apertures in ft. The default is set to 0.5.
        """

        glass_type = short_name(
            self.aperture.properties.energy.construction.display_name, 32)

        parent_llc = self.parent.geometry.lower_left_corner
        rel_plane = self.parent.geometry.plane
        apt_llc = self.aperture.geometry.lower_left_corner
        apt_urc = self.aperture.geometry.upper_right_corner

        # horizontal faces
        # horizontal Face3D; use world XY
        angle_tolerance = 0.01
        if rel_plane.n.angle(Vector3D(0, 0, 1)) <= angle_tolerance or \
                rel_plane.n.angle(Vector3D(0, 0, -1)) <= angle_tolerance:
            proj_x = Vector3D(1, 0, 0)
        else:
            proj_y = Vector3D(0, 0, 1).project(rel_plane.n)
            proj_x = proj_y.rotate(rel_plane.n, math.pi / -2)

        ref_plane = Plane(rel_plane.n, parent_llc, proj_x)
        min_2d = ref_plane.xyz_to_xy(apt_llc)
        max_2d = ref_plane.xyz_to_xy(apt_urc)
        height = max_2d.y - min_2d.y
        width = max_2d.x - min_2d.x

        # find the bounding box of the polygon and use the area to identify the
        # rectangular ones
        bb_vertices = [
            min_2d, min_2d.move(Point2D(width, 0)), max_2d,
            min_2d.move(Point2D(0, height))
        ]

        bb = Polygon2D(bb_vertices)

        geometry: Face3D = self.aperture.geometry

        if bb.area / geometry.boundary_polygon2d.area < 1.01:
            # this is a rectangle
            return \
                '"{}" = WINDOW\n'.format(short_name(self.aperture.display_name)) + \
                "\n  X             = {}".format(min_2d.x) + \
                "\n  Y             = {}".format(min_2d.y) + \
                "\n  WIDTH         = {}".format(width, 3) + \
                "\n  HEIGHT        = {}".format(height, 3) + \
                '\n  GLASS-TYPE    = "{}"'.format(glass_type) + "\n  ..\n"

        # non rectangular aperture
        window_strings = []
        vertices = [ref_plane.xyz_to_xy(v) for v in geometry.vertices]
        # create a 2D Polygon on the parent face
        geometry_2d = Polygon2D(vertices)
        try:
            grid = Mesh2D.from_polygon_grid(
                geometry_2d, resolution, resolution, True
            )
        except AssertionError:
            print(
                f'{self.aperture.display_name} is too small and will not be '
                f'translated. Try a smaller resolution than {resolution}.'
            )
            return '\n\n'

        # group face by y value. All the rows will be merged together.
        vertices = grid.vertices
        groups = {}
        for face in grid.faces:
            min_2d = vertices[face[0]]
            for y in groups:
                if abs(min_2d.y - y) < 0.01:
                    groups[y].append(face)
                    break
            else:
                groups[min_2d.y] = [face]

        for count, group in enumerate(groups.values()):
            # find min_2d and max_2d for each group
            group.sort(key=lambda x: vertices[x[0]].x)
            min_2d = vertices[group[0][0]]
            max_2d = vertices[group[-1][2]]

            height = max_2d.y - min_2d.y
            width = max_2d.x - min_2d.x
            name = f'{short_name(self.aperture.display_name)}_{1000 + count}'
            window = \
                '"{}" = WINDOW\n'.format(name) + \
                "\n  X             = {}".format(min_2d.x) + \
                "\n  Y             = {}".format(min_2d.y) + \
                "\n  WIDTH         = {}".format(width, 3) + \
                "\n  HEIGHT        = {}".format(height, 3) + \
                '\n  GLASS-TYPE    = "{}"'.format(glass_type) + "\n  ..\n"
            window_strings.append(window)

        return '\n\n'.join(window_strings)

    def __repr__(self):
        return self.to_inp()
