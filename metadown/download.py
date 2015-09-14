from metadown.collectors.thredds import ThreddsCollector
from metadown.collectors.geonetwork import GeoNetworkCollector
from metadown.downloader import XmlDownloader
import argparse
import os
import sys

def run_downloader(selects, url, dlpath, **kwargs):
    """
    Selects is list of selectors
    Url is url of base catalog page
    dlpath is download path
    kwargs is any other kwargs to ThreddsCollector
    """
    print "Downloading", url, "to", dlpath
    try:
        isos = ThreddsCollector(url, selects=selects, **kwargs).run()
        XmlDownloader.run(isos, dlpath)
    except Exception as e:
        print >>sys.stderr, "Problem with", url, "ex:", e

def main(base_download_path):

    # selects: The ID in THREDDS needs to contain one of these strings to be identified.
    # skips: The LINK path in the actual thredds catalog webpage can't be equal to any of these strings

    # We only want the Agg selects
    selects = [".*SST-Agg"]
    download_path = os.path.join(base_download_path, "Satellite")
    run_downloader(selects, "http://tds.glos.us/thredds/mtri/aoc.html", download_path)

    # We only want the Agg selects
    selects = [".*CHL-Agg"]
    download_path = os.path.join(base_download_path, "Satellite")
    run_downloader(selects, "http://tds.glos.us/thredds/mtri/chl.html", download_path)

    # We only want the Agg selects
    selects = [".*NC-Agg"]
    download_path = os.path.join(base_download_path, "Satellite")
    run_downloader(selects, "http://tds.glos.us/thredds/mtri/natcolor.html", download_path)

    # MTRI CDOM, DOC and SM Aggregates
    selects = [".*CDOM-Agg"]
    download_path = os.path.join(base_download_path, "Satellite")
    run_downloader(selects, "http://tds.glos.us/thredds/mtri/cdom.html", download_path)

    selects = [".*DOC-Agg"]
    download_path = os.path.join(base_download_path, "Satellite")
    run_downloader(selects, "http://tds.glos.us/thredds/mtri/doc.html", download_path)

    selects = [".*SM-Agg"]
    download_path = os.path.join(base_download_path, "Satellite")
    run_downloader(selects, "http://tds.glos.us/thredds/mtri/sm.html", download_path)


    # We only want the all year best selects
    selects = [".*2D_best.*", ".*3D_best.*", ".*2D_-_All_Years_best.*", ".*3D_-_All_Years_best.*"]
    download_path = os.path.join(base_download_path, "Models", "GLCFS")
    run_downloader(selects, "http://tds.glos.us/thredds/glcfs/glcfs.html", download_path)

    # We only want the Agg and Latest
    selects = [".*Nowcast-Agg.*", ".*Lastest-Forecast.*"]
    # Don't process the "files/" lists
    skips = [".*Nowcast - Individual Files/", ".*Forecast - Individual Files/"]
    download_path = os.path.join(base_download_path, "Models", "HECWFS")
    run_downloader(selects, "http://tds.glos.us/thredds/hecwfs/hecwfs.html", download_path, skips=skips)

    # We only want the Agg and Latest
    selects = [".*Nowcast-Agg.*", ".*Lastest-Forecast.*"]
    # Don't process the "files/" lists
    skips = [".*Nowcast - Individual Files/", ".*Forecast - Individual Files/"]
    download_path = os.path.join(base_download_path, "Models", "SLRFVM")
    run_downloader(selects, "http://tds.glos.us/thredds/slrfvm/slrfvm.html", download_path, skips=skips)

    # RANGER3
    selects = [".*RANGER3"]
    download_path = os.path.join(base_download_path, "RANGER3")
    run_downloader(selects, "http://tds.glos.us/thredds/ranger3.html", download_path)

    # GLERL
    selects = [".*"]
    download_path = os.path.join(base_download_path, "GLERL", "NBS")
    run_downloader(selects, "http://tds.glos.us/thredds/glerl/NBS.html", download_path)

    selects = [".*"]
    download_path = os.path.join(base_download_path, "GLERL", "ATMO")
    run_downloader(selects, "http://tds.glos.us/thredds/glerl/ATMO.html", download_path)

    selects = [".*"]
    download_path = os.path.join(base_download_path, "GLERL", "PRECIP")
    run_downloader(selects, "http://tds.glos.us/thredds/glerl/PRECIP.html", download_path)

    selects = [".*"]
    download_path = os.path.join(base_download_path, "GLERL", "AIRTEMPS")
    run_downloader(selects, "http://tds.glos.us/thredds/glerl/AIRTEMPS.html", download_path)

    # water levels
    selects = [".*"]
    download_path = os.path.join(base_download_path, "WaterLevels")
    run_downloader(selects, "http://tds.glos.us/thredds/water_levels.html", download_path)

    #UMD Glider
    selects = [".*"]
    download_path = os.path.join(base_download_path, "UMDGlider")
    run_downloader(selects, "http://tds.glos.us/thredds/glos_glider.html", download_path)

    # GLOP
    selects = [".*"]
    download_path = os.path.join(base_download_path, "GLOP")
    run_downloader(selects, "http://tds.glos.us/thredds/glop/glop.html", download_path)

    # CIA
    selects = [".*"]
    isos = ThreddsCollector("http://tds.glos.us/thredds/glc/wateruse.html", selects=selects).run()
    download_path = os.path.join(base_download_path, "GLC")
    XmlDownloader.run(isos, download_path)

    # MTRI Water Temp
    selects = [".*"]
    download_path = os.path.join(base_download_path, "Thermistor")
    run_downloader(selects, "http://tds.glos.us/thredds/mtri/water_temp_in_situ.html", download_path)


def geonetwork_collector(base_download_path):
    # FIXME: Remove hardcoding of GN url
    isos = GeoNetworkCollector("http://data.glos.us/metadata").run()
    download_path = os.path.join(base_download_path, "GeoNetwork")
    XmlDownloader.run(isos, download_path,
                      namer=GeoNetworkCollector.uuid_namer,
                      modifier=GeoNetworkCollector.modifier)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Metadata Download')
    parser.add_argument('-g', '--geonetwork', help="Run only the geonetwork collector", action="store_true")
    parser.add_argument("base_download_path", help="Root directory for downloads")
    args = parser.parse_args()
    if args.geonetwork:
        geonetwork_collector(args.base_download_path)
    else:
        main(args.base_download_path)
    exit(0)
