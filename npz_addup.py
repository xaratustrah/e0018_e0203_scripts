import argparse
import numpy as np
from loguru import logger
from tqdm import tqdm

def process_files(file_list):
    """
    Process the files from the file list, summing up the 'zz' arrays from spectrogram files.
    """
    zz_sum = None
    found_files = False

    with open(file_list, 'r') as f:
        files = f.read().splitlines()

    spectrogram_files = [file for file in files if file.endswith("_spectrogram.npz")]

    if not spectrogram_files:
        logger.info("No files ending with '_spectrogram.npz' found. Exiting gracefully.")
        return zz_sum, False

    for file in tqdm(spectrogram_files, desc="Processing files"):
        try:
            data = np.load(file)
            xx, yy, zz = data['arr_0'], data['arr_1'], data['arr_2']
            if zz_sum is None:
                zz_sum = zz
            else:
                zz_sum += zz
            found_files = True
        except Exception as e:
            logger.error(f"Error processing file {file}: {e}")

    return xx, yy, zz_sum

def main():
    """
    Main function to parse arguments and invoke the processing function.
    """
    parser = argparse.ArgumentParser(description="Process a file list and sum the 'zz' arrays from spectrogram files.")
    parser.add_argument("file_list", type=str, help="Path to the file containing the list of file paths.")
    args = parser.parse_args()

    xx, yy, zz = process_files(args.file_list)
    print(np.shape(xx), np.shape(yy), np.shape(zz))

    if found_files:
        logger.info("Successfully processed all spectrogram files and summed the 'zz' arrays.")
    else:
        logger.info("No valid spectrogram files found to process.")

if __name__ == "__main__":
    main()
