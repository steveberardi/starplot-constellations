import json
import logging
from pathlib import Path

from shapely.geometry import Polygon

from starplot import Constellation
from starplot.data import Catalog

__version__ = "0.1.1"

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "data"
BUILD_PATH = HERE / "build"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler("build.log", mode="a")
logger.addHandler(console_handler)
logger.addHandler(file_handler)
formatter = logging.Formatter(
    "{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
)
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)


def parse_ra(ra_str):
    """Parses RA from border file HH MM SS to 0...360 degree float"""
    h, m, s = ra_str.strip().split(" ")
    return round(15 * (float(h) + float(m) / 60 + float(s) / 3600), 6)


def parse_dec(dec_str):
    """Parses DEC from ONGC CSV from HH:MM:SS to -90...90 degree float"""
    return round(float(dec_str), 6)


def parse_borders(constellation_id):
    coords = []

    with open(DATA_PATH / "boundaries" / f"{constellation_id}.txt", "r") as borderfile:
        for line in borderfile.readlines():
            if "|" not in line:
                continue
            ra_str, dec_str, _ = line.split("|")
            ra = parse_ra(ra_str)
            dec = parse_dec(dec_str)
            coords.append((ra, dec))

    return Polygon(coords)


def read_properties():
    with open(DATA_PATH / "constellations.json", "r") as constellation_props_file:
        content = constellation_props_file.read()
        return json.loads(content)


def constellations():
    props_all = read_properties()

    ctr = 0
    for constellation_id, props in props_all.items():
        hiplines = props["hip_lines"]
        hip_ids = set()
        for hip_pair in hiplines:
            hip_ids.update(hip_pair)
        hip_ids = list(hip_ids)

        ctr += 1
        c = Constellation(
            pk=ctr,
            name=props["name"],
            ra=props["ra"],
            dec=props["dec"],
            iau_id=constellation_id,
            constellation_id=constellation_id,
            star_hip_ids=hip_ids,
            star_hip_lines=hiplines,
            boundary=parse_borders(constellation_id),
        )
        yield c


def build():
    logger.info("Building Constellations - IAU...")
    output_path = BUILD_PATH / f"constellations.{__version__}.parquet"
    Catalog.build(
        objects=constellations(),
        path=output_path,
        chunk_size=100,
        columns=[
            "pk",
            "name",
            "ra",
            "dec",
            "iau_id",
            "constellation_id",
            "star_hip_ids",
            "star_hip_lines",
            "boundary",
        ],
        sorting_columns=[],
        compression="none",
        row_group_size=100,
    )

    cat = Catalog(path=output_path)
    all_constellations = [c for c in Constellation.all(catalog=cat)]

    logger.info(f"Total objects: {len(all_constellations)}")
    assert len(all_constellations) == 89

    cma = Constellation.get(iau_id="cma", catalog=cat)
    assert cma.name == "Canis Major"
    assert cma.star_hip_ids == [
        35904,
        33152,
        33347,
        31592,
        33160,
        33579,
        34444,
        30324,
        34045,
        32349,
    ]

    logger.info("Checks passed!")
    logger.info("Done!")


if __name__ == "__main__":
    build()
