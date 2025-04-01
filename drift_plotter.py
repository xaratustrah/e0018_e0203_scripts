import sys, os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import argparse
from loguru import logger
from tqdm import tqdm

def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description="Process .npz files to extract f_max and plot results.")
    parser.add_argument("file_list", type=str, help="Path to the text file containing a list of .npz file paths")
    args = parser.parse_args()

    # Validate the provided file list
    file_list_path = args.file_list
    if not os.path.isfile(file_list_path):
        logger.error(f"The specified path '{file_list_path}' is not a valid file.")
        sys.exit(1)

    # Read file paths from the text file
    try:
        with open(file_list_path, "r") as f:
            file_paths = [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"Failed to read file list: {e}")
        sys.exit(1)

    # Lists to store timestamps and f_max values
    timestamps = []
    f_max_values = []

    # Flag to check for matching files
    found_matching_files = False

    # Loop through the file paths with progress tracking using tqdm
    for filepath in tqdm(file_paths, desc="Processing files", unit="file"):
        if filepath.endswith("_spectrum.npz") and os.path.isfile(filepath):
            found_matching_files = True  # Set flag to True when a matching file is found

            # Extract the timestamp from the filename
            filename = os.path.basename(filepath)
            timestamp_str = filename.split('-')[1].split('.tiq')[0]
            timestamp = datetime.strptime(timestamp_str, '%Y.%m.%d.%H.%M.%S.%f')
            timestamps.append(timestamp)

            # Load data from the .npz file
            data = np.load(filepath)
            ff, pp = data['arr_0'], data['arr_1']

            # Find f_max
            f_max = ff[np.argmax(pp)]
            f_max_values.append(f_max)

    # Handle case when no matching files are found
    if not found_matching_files:
        logger.warning("No files matching the pattern '_spectrum.npz' were found in the file list.")
        sys.exit(1)

    # Write timestamps and f_max values to a TXT file
    output_txt = "output.txt"
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
    output_png = "output.png"
    plt.savefig(output_png)
    logger.info(f"Plot saved to {output_png}")

if __name__ == "__main__":
    logger.add("script.log", format="{time} {level} {message}", level="DEBUG", rotation="1 MB", compression="zip")
    main()
