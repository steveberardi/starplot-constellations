from starplot.styles import PlotStyle, extensions
from starplot import MapPlot, Miller, StereoNorth, StereoSouth, Constellation, _
from shapely import LineString
from .geometry import union_at_zero



def create_plots(catalog, build_path, logger):
    style = PlotStyle().extend(
        extensions.BLUE_NIGHT,
        extensions.MAP,
    )

    conids = [
        # "and",
        # "cma",
        # "tuc",
        # "cas",
        # "psc",
        "cet",
        # "scl",
        # "phe",
        # "dra",
        "umi",
        "oct",
        # "cep",
    ]
    conids = [c.iau_id for c in Constellation.all(catalog=catalog)]

    # for cons in Constellation.all(catalog=catalog):
    for cons in Constellation.find(where=[_.iau_id.isin(conids)], catalog=catalog):
        logger.info(f"Plotting: {cons.iau_id} | {cons.name}")
        boundary = cons.boundary

        if boundary.geom_type == "MultiPolygon":
            # TODO : this needs to go in model from_tuple
            boundary = union_at_zero(boundary.geoms[0], boundary.geoms[1])

        extent = boundary.bounds  # bbox (minx, miny, maxx, maxy)

        if extent[0] < 0:
            extent = (extent[0] + 360, extent[1], extent[2] + 360, extent[3])

        # ra, dec = [p for p in cons.border.coords.xy]
        # extent = (min(ra), min(dec), max(ra), max(dec))

        if cons.dec > 60:
            proj = StereoNorth
        elif cons.dec < -60:
            proj = StereoSouth
        else:
            proj = Miller

        center_ra = max((extent[0] + extent[2]) / 2, 0)
        if center_ra > 360:
            center_ra -= 360

        p = MapPlot(
            projection=proj(center_ra=center_ra),
            ra_min=extent[0],
            ra_max=extent[2],
            dec_min=extent[1],
            dec_max=extent[3],
            style=style,
            resolution=2000,
            clip_path=boundary,
            scale=0.8,
        )
        p.constellations(
            where=[_.iau_id == cons.iau_id],
            catalog=catalog,
        )

        coords = [c for c in cons.border.coords]

        coords.append(coords[0])

        extended = [coords[0]]
        for i, radec in enumerate(coords[1:]):
            ra, dec = radec
            if abs(ra - extended[i][0]) > 180:
                ra += 360

            extended.append([ra, dec])

        ls = LineString(extended).segmentize(1)

        p.line(
            ls.coords,
            style=p.style.constellation_borders,
        )

        # p.polygon(
        #     geometry=boundary,
        #     style=dict(
        #         line_style =(0, (4, 3)),
        #         edge_color = "red",
        #     )
        # )

        p.stars(
            where=[_.hip.isin(cons.star_hip_ids)],
            where_labels=[_.magnitude < 4],
            bayer_labels=True,
        )

        p.title(cons.name, style__line_spacing=80)

        p.ax.set_axis_off()  # hide the axis background that's outside the clip path

        p.export(build_path / f"{cons.iau_id}.png", padding=0.5)

        p.close_fig()
