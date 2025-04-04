import argparse
import numpy as np
from loguru import logger
from tqdm import tqdm
import sys
from iqtools import *
import sys

# font settings for plot
font = {"weight": "bold", "size": 6}  #'family' : 'normal',
plt.rc("font", **font)


def process_files(file_list):
    """
    Process the files from the file list, summing up the 'zz' arrays from spectrogram files.
    """
    zz_sum = None
    found_files = False

    with open(file_list, "r") as f:
        files = f.read().splitlines()

    spectrogram_files = [file for file in files if file.endswith("_spectrogram.npz")]

    if not spectrogram_files:
        logger.info(
            "No files ending with '_spectrogram.npz' found. Exiting gracefully."
        )
        return zz_sum, False

    for file in tqdm(spectrogram_files, desc="Processing files"):
        try:
            data = np.load(file)
            xx, yy, zz = data["arr_0"], data["arr_1"], data["arr_2"]
            if zz_sum is None:
                zz_sum = zz
            else:
                zz_sum += zz
            found_files = True
        except Exception as e:
            logger.error(f"Error processing file {file}: {e}")

    return xx, yy, zz_sum, found_files


def main():
    """
    Main function to parse arguments and invoke the processing function.
    """
    parser = argparse.ArgumentParser(
        description="Process a file list and sum the 'zz' arrays from spectrogram files."
    )
    parser.add_argument(
        "file_list",
        type=str,
        help="Path to the file containing the list of file paths.",
    )
    
    parser.add_argument("-t", "--time-cut", type=float, required=False, help="Start time as a float (optional)")
    
    args = parser.parse_args()

    try:
        logger.info("Starting the summation...")
        xx, yy, zz_sum, found_files = process_files(args.file_list)

        if args.time_cut is not None:
            y_idx = (np.abs(yy[:,0] - float(args.time_cut))).argmin()
            filename_suffix = "_time_cut"
        else:
            y_idx = 0
            filename_suffix = ""
            
        logger.info("Saving 3D NPZ sum to file...")
        np.savez("summed_spectrogram.npz", arr_0=xx[y_idx:,:], arr_1=yy[y_idx:,:], arr_2=zz_sum[y_idx:,:])
        
        logger.info("Plotting the 3D NPZ sum...")
        
        slx = slice (int(np.shape(xx[y_idx:,:])[1]/2) - 500, int(np.shape(xx[y_idx:,:])[1]/2) + 500)
        sly = slice(y_idx, np.shape(yy)[0]) # this one was very tricky until I found it!
        
        plot_spectrogram(
            xx[sly,slx], yy[sly,slx], zz_sum[sly,slx],
            zzmin=10,
            zzmax=500,
            filename="summed_spectrogram" + filename_suffix,
            title="summed_spectrogram" + filename_suffix,
        )

        logger.info("Creating 2D average...")
        navg = np.shape(zz_sum[y_idx:,:])[0]
        xx_avg, yy_avg, zz_sum_avg = get_averaged_spectrogram(xx[y_idx:,:], yy[y_idx:,:], zz_sum[y_idx:,:], every=navg)

        logger.info("Saving 2D NPZ sum to file...")
        np.savez("summed_spectrum.npz", arr_0=xx_avg.flatten(), arr_1=zz_sum_avg.flatten())

        logger.info("Plotting the 2D NPZ sum...")
        plot_spectrum(
            xx_avg.flatten(),
            zz_sum_avg.flatten(),
            dbm=True,
            filename="summed_spectrum" + filename_suffix,
            title="summed_spectrum" + filename_suffix,
        )

        if found_files:
            logger.info(
                "Successfully processed all spectrogram files."
            )
        else:
            logger.info("No valid spectrogram files found to process.")
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user (Ctrl+C). Exiting gracefully.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("Script interrupted (Ctrl+C). See you!")
        sys.exit(1)
