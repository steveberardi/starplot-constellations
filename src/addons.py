from shapely.geometry import Polygon

from .geometry import interpolate


def ursa_minor():
    p0 = interpolate(
        (0, 88.6638870),
        (135.832471, 87.66638870),
    )
    p1 = interpolate(
        (135.832471, 87.66638870),
        (339.260988, 88.6638870),
    )
    p2 = interpolate(
        (339.260988, 88.6638870),
        (360, 88.6638870),
    )

    points = [
        (0, 90),
        *p0,
        *p1,
        *p2,
        [339.260988, 88.6638870],
        [360, 88.6638870],
        [360, 90],
    ]

    points = reversed(points)
    return Polygon(points).segmentize(1)


def octans():
    p0 = interpolate(
        (48.23292, -84.5553818),
        (109.0197087495, -85.2614441),
    )
    points = [
        (0, -90),
        (0, -82.5553818),
        (40, -84.5553818),
        *p0,
        (109.0197087495, -85.2614441),
        (112.0197087495, -84.5553818),
        (360, -82.5553818),
        [360, -90],
    ]

    points = reversed(points)
    return Polygon(points).segmentize(1)


def cepheus():
    points = [
        (313.705874, 80.486786),
        (308.72097, 86.465622),
        (308.331355, 86.63063),
        (343.510666, 86.836891),
        (339.260988, 88.663887),
        (360 + 135.832471, 87.568916),
        (360 + 130.40275, 86.097542),
        (360 + 127.953615, 84.610375),
        (360 + 84.536118, 85.123947),
    ]

    points = reversed(points)
    return Polygon(points).segmentize(1)
