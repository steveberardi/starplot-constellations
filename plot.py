from starplot.styles import PlotStyle, extensions
from starplot import MapPlot, Miller, StereoNorth, StereoSouth, Constellation, _

from geometry import union_at_zero

def create_plots(catalog, build_path):
    

    style = PlotStyle().extend(
        extensions.BLUE_NIGHT,
        extensions.MAP,
    )

    conids = [
        "and",
        # "cma",
        # "tuc",
        # "cas",
        # "psc",
        # "cet",
        # "scl",
        # "phe",
        # "dra",  # Good !
        "umi",
        # "oct",
        "cep",
    ]

    for cons in Constellation.find(where=[_.iau_id.isin(conids)], catalog=catalog):
    # for cons in Constellation.all(catalog=catalog):
        boundary = cons.boundary
        extent = boundary.bounds  # bbox (minx, miny, maxx, maxy)

        if boundary.geom_type == "MultiPolygon":
            # TODO : this needs to go in model from_tuple
            boundary = union_at_zero(boundary.geoms[0], boundary.geoms[1])
            print(cons.iau_id, "is multi")

        extent = boundary.bounds  # bbox (minx, miny, maxx, maxy)

        if extent[0] < 0:
            extent = (extent[0] + 360, extent[1], extent[2] + 360, extent[3])

        print(cons.iau_id, extent)

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
            resolution=2400,
            clip_path=boundary,
            autoscale=True,
        )
        p.constellations(
            where=[_.iau_id == cons.iau_id],
        )

        # p.polygon(
        #     geometry=boundary,
        #     style=PolygonStyle(
        #         fill_color=None,
        #         line_style="dashed",
        #         edge_color="red",
        #     ),
        # )
        p.stars(
            where=[_.magnitude < 6], where_labels=[_.magnitude < 4]
        )
        p.constellation_labels()
        p.constellation_borders()
        p.ax.set_axis_off()  # hide the axis background that's outside the clip path
        p.export(build_path / f"{cons.iau_id}.png", padding=0.5)
        p.close_fig()
