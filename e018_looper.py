#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Process several files as given in the command line argument

2024 xaratustrah
'''

import sys
import argparse
import datetime
import time
from loguru import logger
import shutil
import toml
from iqtools import *


def process_loop(syncfile, logfile, lustrepath, outpath, wwwpath, static_png_name, n_avg, lframes, nframes):
        with open(syncfile) as sf:
            for line in sf.readlines():
                basefilename = line.split()[0].split('/')[-1]
                source_fullfilename = lustrepath + basefilename
                if not already_processed(source_fullfilename, logfile):
                    process_each(source_fullfilename, basefilename, outpath, wwwpath, static_png_name, n_avg, lframes, nframes)
                    put_into_logfile(source_fullfilename, logfile)
                    #copy_files(fullfilename, wwwpath)


def process_each(source_fullfilename, basefilename, outpath, wwwpath, static_png_name, n_avg, lframes, nframes):
    """
    what to do with each file
    """
    
    logger.info('Processing ' +  source_fullfilename)
    iq = get_iq_object(source_fullfilename)
    iq.read_samples(1)
    logger.info('Plotting into a png file...')
    iq.read(nframes=nframes, lframes=lframes)
    iq.method = 'fftw'
    xx, yy, zz = iq.get_power_spectrogram(lframes=lframes, nframes=nframes, sparse=True)
    xx, yy, zz = get_averaged_spectrogram(xx, yy, zz, every = n_avg)

    font = {#'family' : 'normal',
            'weight' : 'bold',
            'size'   : 5}

    plt.rc('font', **font)

    plot_spectrogram(xx, yy, zz, cen=iq.center,
                     filename=outpath+basefilename, title=basefilename)
    
    logger.info('Creating a NPZ file...')
    np.savez(outpath + basefilename + '.npz', xx + iq.center, yy, zz)
    
    # then make copies
    shutil.copy(source_fullfilename, outpath)
    shutil.copy(outpath+basefilename+'.png', wwwpath + static_png_name)
    
    

def put_into_logfile(file, logfilename):
    """
    Write into the log file.
    """

    with open(logfilename, 'a') as file_object:
        file_object.write(file + '\n')


def already_processed(currentfilename, logfilename):
    """
    check whether the file is already in the log file
    """

    already_processed = False
    try:
        with open(logfilename, 'r') as file_object:
            loglist = file_object.readlines()

            for line in loglist:
                if currentfilename in line:
                    already_processed = True

    except OSError as e:
        logger.warning('Log file does not exist, creating a new one.')

    return already_processed

def main():
    scriptname = 'e018_looper'
    __version__ = 'v0.0.1'

    default_logfilename = datetime.datetime.now().strftime('%Y.%m.%d.%H.%M.%S') + '.txt'

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

    logger.info('{} {}'.format(scriptname, __version__))

    # read config file
    config_dic = None
    if args.config:
        logger.info("Configuration file has been provided: " + args.config[0])
        try:
            # Load calibration file
            config_dic = toml.load(args.config[0])
            # check structure of calibration file
            print(config_dic)
            for key in ['syncfile', 'logfile', 'lustrepath', 'outpath', 'wwwpath']:
                assert key in config_dic['paths'].keys()
            for key in ['n_avg', 'sleeptime', 'static_png_name', 'lframes', 'nframes']:
                assert key in config_dic['settings'].keys()
                
        except:
            logger.error('Config file does not have required format.')
            exit()
           
        logger.success("Config file is good.")

        lframes = config_dic['settings']['lframes']
        nframes = config_dic['settings']['nframes']
        static_png_name = config_dic['settings']['static_png_name']
        n_avg = config_dic['settings']['n_avg']
        sleeptime = config_dic['settings']['sleeptime']

        syncfile = config_dic['paths']['syncfile']
        logfile = config_dic['paths']['logfile']
        lustrepath = config_dic['paths']['lustrepath']
        outpath = config_dic['paths']['outpath']
        wwwpath = config_dic['paths']['wwwpath']
                
                
    else:
        logger.error(
            "No Config file provided. Aborting..."
        )
        exit()


    logger.info('Processing files from sync file list: ', syncfile)
    logger.info('Lustre path will be: ' + lustrepath)
    logger.info('Out path will be: ' +  outpath)
    logger.info('WWW path will be: ' +  wwwpath)
    logger.info('Log file will be: ' +  logfile)

    
    wwwpath = os.path.join(wwwpath, '')
    outpath = os.path.join(outpath, '')
    lustrepath = os.path.join(lustrepath, '')


    logger.info('Let us see if there are new files...')
    try:
        while True:
            # Make sure there is a trailing slash at the end of the path

            # start looping process
            process_loop(syncfile, logfile, lustrepath, outpath, wwwpath, static_png_name, n_avg, lframes, nframes)
            time.sleep(sleeptime)
            logger.info('I am waiting for new files...')

    except KeyboardInterrupt:
        logger.success(
            "\nOh no! You don't want me to continue waiting for new files! Aborting as you wish :-(")


# ------------------------
if __name__ == '__main__':
    main()
