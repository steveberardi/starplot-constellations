import numpy as np

from shapely.geometry import Polygon, LineString, MultiPolygon
from shapely.ops import split
from shapely import union_all

MERIDIAN = LineString([(360, 90), (360, -90)])

def split_polygon_with_line(polygon, line=MERIDIAN):
    """Split a polygon with a line."""
    if not polygon.intersects(line):
        return [polygon]
    
    result = split(polygon, line)
    
    polygons = []
    for geom in result.geoms:
        if geom.geom_type == 'Polygon':
            polygons.append(geom)
        elif geom.geom_type == 'MultiPolygon':
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


def union_at_zero(a: Polygon, b: Polygon) -> Polygon:
    """Returns union of two polygons"""
    a_ra = list(a.exterior.coords.xy)[0]
    b_ra = list(b.exterior.coords.xy)[0]

    if max(a_ra) == 360 and min(b_ra) == 0:
        points = list(zip(*b.exterior.coords.xy))
        return a, Polygon([[ra + 360, dec] for ra, dec in points])

    if min(a_ra) == 0 and max(b_ra) == 360:
        points = list(zip(*a.exterior.coords.xy))
        return Polygon([[ra + 360, dec] for ra, dec in points]), b

    return union_all([a, b])


def interpolate(a, b, num_points=100):
    p1 = np.array(a)
    p2 = np.array(b)
    t = np.linspace(0, 1, num_points)
    return p1 + t[:, np.newaxis] * (p2 - p1)

