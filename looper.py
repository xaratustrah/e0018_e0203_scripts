#
# Multiprocessing looper
# 
# (2025) xaratustrah@github
#

import os
import time
import multiprocessing
import pickle
import tomli
from loguru import logger
from functools import partial
import argparse
from iqtools import *


# Declare the global variable
PROCESSED_FILES = set()

# font settings for plot
font = {"weight": "bold", "size": 5}  #'family' : 'normal',
plt.rc("font", **font)


def read_and_verify_settings(toml_file):
    """
    Read and validate settings from a TOML file using a required_keys structure.
    """
    try:
        # Define required sections and keys
        required_keys = {
            "paths": [
                "monitor_dir",
                "state_file",
            ],
            "processing": ["num_cores", "interval_seconds", "file_ready_seconds"],
            "analysis": ["nframes", "lframes", "navg"],
        }

        # Load the TOML file
        with open(toml_file, "rb") as file:
            config = tomli.load(file)

        # Validate required sections and keys
        for section, keys in required_keys.items():
            if section not in config:
                raise KeyError(f"Missing section: {section}")
            for key in keys:
                if key not in config[section]:
                    raise KeyError(f"Missing key: {key} in section: {section}")

        logger.info("Settings successfully read and validated.")
        return config

    except KeyError as e:
        logger.error(f"Configuration error: {e}")
        print(f"Configuration error: {e}")  # Ensure visibility in console
        raise
    except Exception as e:
        logger.error(f"Error reading or validating settings: {e}")
        print(f"Error: {e}")
        raise


# Load processed files state from disk
def load_processed_files(state_file):
    global PROCESSED_FILES
    if os.path.exists(state_file):
        with open(state_file, "rb") as file:
            PROCESSED_FILES = pickle.load(file)
        logger.info(f"Loaded {len(PROCESSED_FILES)} processed files from state.")


# Save processed files state to disk
def save_processed_files(state_file):
    with open(state_file, "wb") as file:
        pickle.dump(PROCESSED_FILES, file)
    logger.info("Processed files state saved.")


# Check if file is ready for processing
def is_file_ready(filepath, settings):
    file_ready_seconds = settings["processing"]["file_ready_seconds"]
    initial_size = os.path.getsize(filepath)
    time.sleep(file_ready_seconds)  # Wait briefly
    current_size = os.path.getsize(filepath)
    ready = initial_size == current_size  # File size is stable
    if ready:
        logger.debug(f"File {filepath} is ready for processing.")
    else:
        logger.warning(f"File {filepath} is still being written.")
    return ready


# Process the file
def process_file(filename, settings):
    navg = settings["analysis"]["navg"]
    zzmin = settings["analysis"]["zzmin"]
    zzmax = settings["analysis"]["zzmax"]
    dbm = settings["analysis"]["dbm"]
    mask = settings["analysis"]["mask"]
    lframes = settings["analysis"]["lframes"]
    nframes = settings["analysis"]["nframes"]
    monitor_dir = settings["paths"]["monitor_dir"]
    monitor_dir = os.path.join(monitor_dir, "") 
    output_dir = settings["paths"]["output_dir"]
    output_dir = os.path.join(output_dir, "")

    start_time = time.time()  # Record start time

    # here comes the actual calculation
    iq = get_iq_object(monitor_dir + filename)
    iq.method = "fftw"
    iq.read(nframes=nframes, lframes=lframes)
    xx, yy, zz = iq.get_power_spectrogram(nframes=nframes, lframes=lframes)
    xx, yy, zz = get_averaged_spectrogram(xx, yy, zz, every=navg)
    plot_spectrogram(
        xx,
        yy,
        zz,
        cen=iq.center,
        zzmin=zzmin,
        zzmax=zzmax,
        dbm=dbm,
        mask=mask,
        filename=output_dir + filename,
        title=filename,
    )
    np.savez(output_dir + filename + ".npz", xx + iq.center, yy, zz)

    end_time = time.time()  # Record end time
    elapsed_time = end_time - start_time  # Calculate elapsed time
    logger.info(f"Finished processing {filename} in {elapsed_time:.2f} seconds.")


# Monitor and process files
def monitor_directory(settings):
    global PROCESSED_FILES

    state_file = settings["paths"]["state_file"]
    monitor_dir = settings["paths"]["monitor_dir"]
    num_cores = settings["processing"]["num_cores"]
    interval_seconds = settings["processing"]["interval_seconds"]

    load_processed_files(state_file)  # Load state at startup
    try:
        while True:
            files = [f for f in os.listdir(monitor_dir) if f.lower().endswith(".tiq")]
            unprocessed_files = [f for f in files if f not in PROCESSED_FILES]

            # Check for files that are ready to process
            ready_files = []
            for file in unprocessed_files:
                filepath = os.path.join(monitor_dir, file)
                if os.path.isfile(filepath) and is_file_ready(filepath, settings):
                    ready_files.append(file)

            if ready_files:
                logger.info(f"Files to process: {ready_files}")

                # Prepare the partial function with the additional argument
                process_file_partial = partial(process_file, settings=settings)

                # Process files using multiprocessing pool
                with multiprocessing.Pool(num_cores) as pool:
                    pool.map(process_file_partial, ready_files)

                # Update the list of processed files
                PROCESSED_FILES.update(ready_files)

                # Save state after processing files
                save_processed_files(state_file)

            time.sleep(interval_seconds)  # Monitor at regular intervals
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
        save_processed_files(state_file)  # Save state on exit


def main():
    # Setup argument parser for command-line arguments
    parser = argparse.ArgumentParser(
        description="Monitor a directory and process files."
    )
    parser.add_argument(
        "--config", required=True, help="Path to the TOML configuration file."
    )
    args = parser.parse_args()

    logger.add(
        "processing.log",
        format="{time} {level} {message}",
        level="INFO",
        rotation="1 MB",
    )

    # Load settings from the provided TOML file
    settings = read_and_verify_settings(args.config)
    monitor_directory(settings)


# -------------------------

if __name__ == "__main__":
    main()
