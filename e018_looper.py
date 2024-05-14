#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Process several files as given in the command line argument

2024 xaratustrah
"""

import sys
import argparse
import datetime
import time
from loguru import logger
import shutil
import toml
from iqtools import *


def process_loop(
    syncfile, logfile, lustrepath, outpath, wwwpath, n_avg, lframes, nframes
):
    try:
        with open(syncfile) as sf:
            for line in sf.readlines():
                basefilename = line.split()[0].split("/")[-1]
                source_fullfilename = lustrepath + basefilename
                if not already_processed(source_fullfilename, logfile):
                    put_into_logfile(source_fullfilename, logfile)
                    process_each(
                        source_fullfilename,
                        basefilename,
                        outpath,
                        wwwpath,
                        n_avg,
                        lframes,
                        nframes,
                    )

    except:
        logger.error("No sync file list on the specified location. Aborting.")
        exit()


def process_each(
    source_fullfilename, basefilename, outpath, wwwpath, n_avg, lframes, nframes
):
    """
    what to do with each file
    """

    logger.info(f"Now processing {basefilename}")
    iq = get_iq_object(source_fullfilename)
    logger.info("Reading file...")
    iq.read(nframes=nframes, lframes=lframes)
    iq.method = "fftw"
    logger.info("Do FFT...")
    xx, yy, zz = iq.get_power_spectrogram(lframes=lframes, nframes=nframes, sparse=True)
    xx, yy, zz = get_averaged_spectrogram(xx, yy, zz, every=n_avg)

    font = {"weight": "bold", "size": 5}  #'family' : 'normal',

    plt.rc("font", **font)

    logger.info("Write to PNG...")
    plot_spectrogram(
        xx, yy, zz, cen=iq.center, filename=outpath + basefilename, title=basefilename
    )

    plot_spectrogram(
        xx,
        yy,
        zz,
        cen=iq.center,
        filename=outpath + basefilename + "_zoom",
        title=basefilename + "_zoom",
        span=200000,
    )

    logger.info("Write to NPZ...")
    np.savez(outpath + basefilename + ".npz", xx + iq.center, yy, zz)

    logger.info("Copying files...")
    shutil.copy(source_fullfilename, outpath)
    shutil.copy(outpath + basefilename + ".png", wwwpath + basefilename[:5] + ".png")
    shutil.copy(
        outpath + basefilename + "_zoom.png",
        wwwpath + "zoom_" + basefilename[:5] + ".png",
    )
    logger.success(f"Done processing {basefilename}\n\n")


def put_into_logfile(file, logfilename):
    """
    Write into the log file.
    """

    with open(logfilename, "a") as file_object:
        file_object.write(file + "\n")


def already_processed(currentfilename, logfilename):
    """
    check whether the file is already in the log file
    """

    already_processed = False
    try:
        with open(logfilename, "r") as file_object:
            loglist = file_object.readlines()

            for line in loglist:
                if currentfilename in line:
                    already_processed = True

    except OSError as e:
        logger.warning("Log file does not exist, creating a new one.")

    return already_processed


def main():
    scriptname = "e018_looper"
    __version__ = "v0.0.1"

    default_logfilename = datetime.datetime.now().strftime("%Y.%m.%d.%H.%M.%S") + ".txt"

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        nargs=1,
        type=str,
        default=None,
        help="Path and name of the TOML config file.",
    )

    logger.remove(0)
    logger.add(sys.stdout, level="INFO")

    args = parser.parse_args()

    logger.info("{} {}".format(scriptname, __version__))

    # read config file
    config_dic = None
    if args.config:
        logger.info("Configuration file has been provided: " + args.config[0])
        try:
            # Load calibration file
            config_dic = toml.load(args.config[0])
            # check structure of calibration file
            print(config_dic)
            for key in ["syncfile", "logfile", "lustrepath", "outpath", "wwwpath"]:
                assert key in config_dic["paths"].keys()
            for key in ["n_avg", "sleeptime", "lframes", "nframes"]:
                assert key in config_dic["settings"].keys()

        except:
            logger.error("Config file does not have required format.")
            exit()

        logger.success("Config file is good.")

        lframes = config_dic["settings"]["lframes"]
        nframes = config_dic["settings"]["nframes"]
        n_avg = config_dic["settings"]["n_avg"]
        sleeptime = config_dic["settings"]["sleeptime"]

        syncfile = config_dic["paths"]["syncfile"]
        logfile = config_dic["paths"]["logfile"]
        lustrepath = config_dic["paths"]["lustrepath"]
        outpath = config_dic["paths"]["outpath"]
        wwwpath = config_dic["paths"]["wwwpath"]

    else:
        logger.error("No Config file provided. Aborting...")
        exit()

    logger.info("Processing files from sync file list: " + syncfile)
    logger.info("Log file: " + logfile)
    logger.info("Taking files from (lustrepath): " + lustrepath)
    logger.info("Writing files to (outpath): " + outpath)
    logger.info("Copy files to (wwwpath): " + wwwpath)

    wwwpath = os.path.join(wwwpath, "")
    outpath = os.path.join(outpath, "")
    lustrepath = os.path.join(lustrepath, "")

    logger.info("Let us see if there are new files...")
    try:
        while True:
            # Make sure there is a trailing slash at the end of the path

            # start looping process
            process_loop(
                syncfile, logfile, lustrepath, outpath, wwwpath, n_avg, lframes, nframes
            )
            time.sleep(sleeptime)
            logger.info("I am waiting for new files...")

    except KeyboardInterrupt:
        logger.success(
            "\nOh no! You don't want me to continue waiting for new files! Aborting as you wish :-("
        )


# ------------------------
if __name__ == "__main__":
    main()
