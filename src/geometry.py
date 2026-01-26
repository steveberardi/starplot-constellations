import numpy as np

from shapely.geometry import Polygon, LineString
from shapely.ops import split

MERIDIAN = LineString([(360, 90), (360, -90)])


def interpolate(a, b, num_points=100):
    p1 = np.array(a)
    p2 = np.array(b)
    t = np.linspace(0, 1, num_points)
    return p1 + t[:, np.newaxis] * (p2 - p1)


def split_polygon_with_line(polygon, line=MERIDIAN):
    """Split a polygon with a line."""
    if not polygon.intersects(line):
        return [polygon]

    result = split(polygon, line)

    polygons = []
    for geom in result.geoms:
        if geom.geom_type == "Polygon":
            polygons.append(geom)
        elif geom.geom_type == "MultiPolygon":
            polygons.extend(list(geom.geoms))

    return polygons if polygons else [polygon]


def normalize_to_360(polygon: Polygon) -> Polygon:
    """
    If the provided polygon has coordinates with large jumps from < 100 to > 300,
    then it likely crosses the 0-point. This function will add 360 to all X coords
    under 100 and return the result.
    """

    ra, dec = [p for p in polygon.exterior.coords.xy]

    if min(ra) < 100 and max(ra) > 300:
        new_ra = [r + 360 if r < 100 else r for r in ra]
        return Polygon(list(zip(new_ra, dec)))

    return polygon


def restrict_to_360(polygon: Polygon) -> Polygon:
    """
    If the polygon has a max RA over 360, then subtract 360 from all RA coordinates.
    """
    ra, dec = [p for p in polygon.exterior.coords.xy]

    if max(ra) > 360:
        new_ra = [r - 360 for r in ra]
        return Polygon(list(zip(new_ra, dec)))

    return polygon
