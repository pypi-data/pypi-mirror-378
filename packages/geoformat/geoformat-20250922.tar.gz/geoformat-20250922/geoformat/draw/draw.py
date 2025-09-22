from __future__ import annotations

import os
import sys

from geoformat.conf.error_messages import import_matplotlib_error, import_numpy_error
from geoformat.conversion.coordinates_conversion import force_rhr_polygon_coordinates
from geoformat.conversion.geometry_conversion import geometry_to_bbox
from geoformat.geoprocessing.merge_geometries import merge_geometries

# ---------------------------------------------------------------------
# Choose an interactive backend if a GUI is available
# ---------------------------------------------------------------------
import matplotlib


def _environment_supports_gui() -> bool:
    """Return True if a graphical display seems available."""
    return bool(
        os.environ.get("DISPLAY")
        or os.environ.get("WAYLAND_DISPLAY")
        or sys.platform.startswith("win")
    )


def _ensure_interactive_backend() -> None:
    """
    If no MPLBACKEND is set and a GUI is available, try to use an interactive
    backend (QtAgg → Qt5Agg → TkAgg).
    """
    if os.environ.get("MPLBACKEND") or not _environment_supports_gui():
        return
    for candidate in ("QtAgg", "Qt5Agg", "TkAgg"):
        try:
            matplotlib.use(candidate, force=True)
            break
        except Exception:
            continue


_ensure_interactive_backend()

# ---------------------------------------------------------------------
# Imports depending on the environment
# ---------------------------------------------------------------------
try:
    import numpy as np
    import_numpy_success = True
except ImportError:
    import_numpy_success = False

try:
    import matplotlib.pyplot as plt
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path
    import_matplotlib_success = True
except ImportError:
    import_matplotlib_success = False


# ---------------------------------------------------------------------
# Implementation
# ---------------------------------------------------------------------
if import_matplotlib_success and import_numpy_success:

    class DrawGeometry:
        """
        Utility to draw GeoJSON-like geometries with Matplotlib.
        """

        # ---- default style ----
        POINT_MARKER = "o"
        POINT_MARKER_SIZE = 10
        POINT_COLOR = "black"
        POINT_LINESTYLE = "None"
        POINT_Z_ORDER = 2

        LINESTRING_COLOR = "black"
        LINESTRING_FACECOLOR = "none"
        LINESTRING_WIDTH = 1
        LINESTRING_LINESTYLE = "-"
        LINESTRING_Z_ORDER = 1

        POLYGON_EDGE_COLOR = "black"
        POLYGON_FACE_COLOR = "#d8e0ea"
        POLYGON_WIDTH = 1
        POLYGON_LINESTYLE = "-"
        POLYGON_Z_ORDER = 0

        GRATICULE_MAJOR_COLOR = "black"
        GRATICULE_MAJOR_LINE_STYLE = "-"
        GRATICULE_MAJOR_LINE_WIDTH = 0.5
        GRATICULE_MAJOR_ALPHA = 0.5
        GRATICULE_MINOR_COLOR = "grey"
        GRATICULE_MINOR_LINE_STYLE = ":"
        GRATICULE_MINOR_LINE_WIDTH = 0.2
        GRATICULE_MINOR_ALPHA = 0.5

        VERTEX_MARKER = "x"
        VERTEX_MARKER_SIZE = 6
        VERTEX_COLOR = "black"
        VERTEX_LINESTYLE = "None"

        def __init__(self, geometry: dict, *, show_vertices: bool = False) -> None:
            """
            Parameters
            ----------
            geometry : dict
                GeoJSON-like geometry.
            show_vertices : bool, optional
                If True, draw all vertices as markers.
            """
            self.geometry = geometry
            self.bbox = geometry.get("bbox") or geometry_to_bbox(geometry=self.geometry)
            self.fig, self.ax = plt.subplots()
            self.show_vertices = show_vertices

        # ---- helpers ----
        def create_codes(self, num_points: int) -> list[int]:
            return [Path.MOVETO] + [Path.LINETO] * (num_points - 1)

        def validate_coordinates(self, coordinates: list) -> bool:
            return bool(coordinates and (not isinstance(coordinates[0], (list, tuple)) or any(coordinates)))

        def _plot_vertices(self, points: list[list[float]]) -> None:
            if not points:
                return
            arr = np.array(points)
            self.ax.plot(
                arr[:, 0],
                arr[:, 1],
                marker=self.VERTEX_MARKER,
                markersize=self.VERTEX_MARKER_SIZE,
                color=self.VERTEX_COLOR,
                linestyle=self.VERTEX_LINESTYLE,
                zorder=3,
            )

        # ---- plot primitives ----
        def plot_point(self, coordinates: list[float]) -> None:
            self.ax.plot(
                coordinates[0],
                coordinates[1],
                marker=self.POINT_MARKER,
                markersize=self.POINT_MARKER_SIZE,
                color=self.POINT_COLOR,
                linestyle=self.POINT_LINESTYLE,
                zorder=self.POINT_Z_ORDER,
            )
            if self.show_vertices:
                self._plot_vertices([coordinates])

        def plot_line_string(self, coordinates: list[list[float]]) -> None:
            verts = np.array(coordinates)
            path = Path(verts)
            patch = PathPatch(
                path,
                edgecolor=self.LINESTRING_COLOR,
                facecolor=self.LINESTRING_FACECOLOR,
                linewidth=self.LINESTRING_WIDTH,
                linestyle=self.LINESTRING_LINESTYLE,
                zorder=self.LINESTRING_Z_ORDER,
            )
            self.ax.add_patch(patch)
            if self.show_vertices:
                self._plot_vertices(coordinates)

        def plot_polygon(self, coordinates: list[list[list[float]]]) -> None:
            coordinates = force_rhr_polygon_coordinates(coordinates=coordinates)
            verts = None
            codes: list[int] = []
            for ring in coordinates:
                ring_verts = np.array(ring)
                verts = ring_verts if verts is None else np.concatenate([verts, ring_verts])
                codes += self.create_codes(len(ring))
            path = Path(verts, codes)
            patch = PathPatch(
                path,
                edgecolor=self.POLYGON_EDGE_COLOR,
                facecolor=self.POLYGON_FACE_COLOR,
                linewidth=self.POLYGON_WIDTH,
                linestyle=self.POLYGON_LINESTYLE,
                zorder=self.POLYGON_Z_ORDER,
            )
            self.ax.add_patch(patch)
            if self.show_vertices:
                for ring in coordinates:
                    self._plot_vertices(ring)

        def plot_multi_point(self, coordinates: list[list[float]]) -> None:
            arr = np.array(coordinates)
            self.ax.plot(
                arr[:, 0],
                arr[:, 1],
                marker=self.POINT_MARKER,
                markersize=self.POINT_MARKER_SIZE,
                color=self.POINT_COLOR,
                linestyle=self.POINT_LINESTYLE,
                zorder=self.POINT_Z_ORDER,
            )
            if self.show_vertices:
                self._plot_vertices(coordinates)

        def plot_multi_line_string(self, coordinates: list[list[list[float]]]) -> None:
            for ls in coordinates:
                if ls:
                    self.plot_line_string(ls)

        def plot_multi_polygon(self, coordinates: list[list[list[list[float]]]]) -> None:
            for poly in coordinates:
                if poly:
                    self.plot_polygon(poly)

        # ---- dispatch and final rendering ----
        def plot(
            self,
            graticule: bool = False,
            *,
            save_path: str | os.PathLike[str] | None = None,
            dpi: int | float | None = None,
        ) -> None:
            """
            Render the geometry. Save to file if save_path is provided.

            If save_path is None, try to show the figure interactively.
            In a headless environment without save_path, a RuntimeError is raised.
            """
            if self.geometry["type"] == "GeometryCollection":
                for geometry in self.geometry["geometries"]:
                    self.plot_geometry(geometry)
            else:
                self.plot_geometry(self.geometry)

            margin = self.expand_bbox()
            self.ax.set_xlim(margin[0], margin[2])
            self.ax.set_ylim(margin[1], margin[3])

            if graticule:
                self.ax.minorticks_on()
                self.ax.grid(
                    which="major",
                    color=self.GRATICULE_MAJOR_COLOR,
                    linestyle=self.GRATICULE_MAJOR_LINE_STYLE,
                    linewidth=self.GRATICULE_MAJOR_LINE_WIDTH,
                    alpha=self.GRATICULE_MAJOR_ALPHA,
                )
                self.ax.grid(
                    which="minor",
                    color=self.GRATICULE_MINOR_COLOR,
                    linestyle=self.GRATICULE_MINOR_LINE_STYLE,
                    linewidth=self.GRATICULE_MINOR_LINE_WIDTH,
                    alpha=self.GRATICULE_MINOR_ALPHA,
                )

            self.ax.set_aspect("equal", adjustable="box")

            if save_path:
                plt.savefig(save_path, dpi=dpi)
                return  # no interactive show when saving only

            try:
                plt.show()
            except Exception as e:
                raise RuntimeError(
                    "Interactive display is not available. "
                    "Provide `path='output.png'` to save the figure instead."
                ) from e

        def plot_geometry(self, geometry: dict) -> None:
            handlers = {
                "Point": self.plot_point,
                "MultiPoint": self.plot_multi_point,
                "LineString": self.plot_line_string,
                "MultiLineString": self.plot_multi_line_string,
                "Polygon": self.plot_polygon,
                "MultiPolygon": self.plot_multi_polygon,
            }
            if (handler := handlers.get(geometry["type"])) is not None:
                coords = geometry.get("coordinates", [])
                if self.validate_coordinates(coords):
                    handler(coords)

        def expand_bbox(self) -> tuple[float, float, float, float]:
            if self.bbox:
                x_diff = self.bbox[2] - self.bbox[0]
                y_diff = self.bbox[3] - self.bbox[1]
                x_margin = x_diff * 0.1 or 1
                y_margin = y_diff * 0.1 or 1
                return (
                    self.bbox[0] - x_margin,
                    self.bbox[1] - y_margin,
                    self.bbox[2] + x_margin,
                    self.bbox[3] + y_margin,
                )
            return (-1, -1, 1, 1)


# ---------------------------------------------------------------------
# Public wrapper functions
# ---------------------------------------------------------------------
def draw_geometry(
    geometry: dict,
    graticule: bool = False,
    *,
    show_vertices: bool = False,
    path: str | os.PathLike[str] | None = None,
    dpi: int | float | None = None,
) -> None:
    """
    Draw a geometry. If `path` is given, the figure is saved to that file and not shown.
    """
    if import_matplotlib_success and import_numpy_success:
        DrawGeometry(geometry, show_vertices=show_vertices).plot(
            graticule=graticule, save_path=path, dpi=dpi
        )
    else:
        if not import_matplotlib_success:
            raise Exception(import_matplotlib_error)
        if not import_numpy_success:
            raise Exception(import_numpy_error)


def draw_feature(
    feature: dict,
    graticule: bool = False,
    *,
    show_vertices: bool = False,
    path: str | os.PathLike[str] | None = None,
    dpi: int | float | None = None,
) -> None:
    """
    Draw a GeoJSON-like feature (uses its "geometry").
    If `path` is given, the figure is saved to that file and not shown.
    """
    if import_matplotlib_success and import_numpy_success:
        if geometry := feature.get("geometry"):
            draw_geometry(
                geometry,
                graticule=graticule,
                show_vertices=show_vertices,
                path=path,
                dpi=dpi,
            )
    else:
        if not import_matplotlib_success:
            raise Exception(import_matplotlib_error)
        if not import_numpy_success:
            raise Exception(import_numpy_error)


def draw_geolayer(
    geolayer: dict,
    graticule: bool = False,
    *,
    show_vertices: bool = False,
    path: str | os.PathLike[str] | None = None,
    dpi: int | float | None = None,
) -> None:
    """
    Draw a geolayer by merging all its features' geometries.
    If `path` is given, the figure is saved to that file and not shown.
    """
    if import_matplotlib_success and import_numpy_success:
        geolayer_geometry = None
        features = geolayer.get("features")
        if isinstance(features, dict):
            for _, feature in features.items():
                if geom := feature.get("geometry"):
                    geolayer_geometry = (
                        geom if geolayer_geometry is None else merge_geometries(geolayer_geometry, geom)
                    )
        if geolayer_geometry:
            draw_geometry(
                geolayer_geometry,
                graticule=graticule,
                show_vertices=show_vertices,
                path=path,
                dpi=dpi,
            )
    else:
        if not import_matplotlib_success:
            raise Exception(import_matplotlib_error)
        if not import_numpy_success:
            raise Exception(import_numpy_error)
