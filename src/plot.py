from shapely import Polygon

from starplot.styles import PlotStyle, extensions
from starplot import MapPlot, Miller, StereoNorth, StereoSouth, Constellation, _


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

    for cons in Constellation.find(where=[_.iau_id.isin(conids)], catalog=catalog):
        logger.info(f"Plotting: {cons.iau_id} | {cons.name}")

        ra, dec = [p for p in cons.border.coords.xy]
        extent = (
            min(ra) - 2,
            max(min(dec) - 2, -90),
            max(ra) + 2,
            min(max(dec) + 2, 90),
        )

        if extent[0] < 0:
            extent = (extent[0] + 360, extent[1], extent[2] + 360, extent[3])

        if cons.dec > 60:
            proj = StereoNorth
        elif cons.dec < -60:
            proj = StereoSouth
        else:
            proj = Miller

        center_ra = (extent[0] + extent[2]) / 2
        if center_ra < 0:
            center_ra += 360
        elif center_ra > 360:
            center_ra -= 360

        p = MapPlot(
            projection=proj(center_ra=center_ra),
            ra_min=extent[0],
            ra_max=extent[2],
            dec_min=extent[1],
            dec_max=extent[3],
            style=style,
            resolution=2000,
            clip_path=Polygon(cons.border.coords),
            scale=0.8,
        )
        p.constellations(
            where=[_.iau_id == cons.iau_id],
            catalog=catalog,
        )

        p.line(
            cons.border.coords,
            style=p.style.constellation_borders,
        )

        # p.polygon(
        #     geometry=Polygon(cons.border.coords),
        #     style={"color": "yellow", "alpha": 0.1},
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
