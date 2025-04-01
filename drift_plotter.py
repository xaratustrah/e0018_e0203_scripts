import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import argparse
from loguru import logger
from tqdm import tqdm

def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description="Process .npz files to extract f_max and plot results.")
    parser.add_argument("directory", type=str, help="Path to the directory containing .npz files")
    args = parser.parse_args()

    # Validate the provided directory
    directory = args.directory
    if not os.path.isdir(directory):
        logger.error(f"The specified path '{directory}' is not a valid directory.")
        sys.exit(1)

    # Lists to store timestamps and f_max values
    timestamps = []
    f_max_values = []

    # Flag to check for matching files
    found_matching_files = False

    # Loop through the files in the directory with progress tracking using tqdm
    files = os.listdir(directory)
    for filename in tqdm(files, desc="Processing files", unit="file"):
        if filename.endswith("_spectrum.npz"):
            found_matching_files = True  # Set flag to True when a matching file is found

            # Extract the timestamp from the filename
            timestamp_str = filename.split('-')[1].split('.tiq')[0]
            timestamp = datetime.strptime(timestamp_str, '%Y.%m.%d.%H.%M.%S.%f')
            timestamps.append(timestamp)

            # Load data from the .npz file
            filepath = os.path.join(directory, filename)
            data = np.load(filepath)
            ff, pp = data['arr_0'], data['arr_1']

            # Find f_max
            f_max = ff[np.argmax(pp)]
            f_max_values.append(f_max)

    # Handle case when no matching files are found
    if not found_matching_files:
        logger.warning("No files matching the pattern '_spectrum.npz' were found in the directory.")
        sys.exit(1)

    # Write timestamps and f_max values to a TXT file
    output_txt = os.path.join(directory, "output.txt")
    np.savetxt(output_txt, np.column_stack((timestamps, f_max_values)), 
               fmt='%s', header="Timestamp, f_max")
    logger.info(f"Timestamps and f_max values saved to {output_txt}")

    # Plot timestamps and f_max values
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, f_max_values, marker='o', linestyle='-')
    plt.xlabel("Timestamp")
    plt.ylabel("f_max")
    plt.title("f_max vs Timestamp")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot as a PNG file without showing it
    output_png = os.path.join(directory, "output.png")
    plt.savefig(output_png)
    logger.info(f"Plot saved to {output_png}")

if __name__ == "__main__":
    logger.add("script.log", format="{time} {level} {message}", level="DEBUG", rotation="1 MB", compression="zip")
    main()
