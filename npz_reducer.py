import argparse
import numpy as np

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Reduce data in a NumPy file")
    parser.add_argument("input_file", help="Path to the input NumPy file (.npz)")
    parser.add_argument("--reduce_by", type=float, default=3, help="Factor to reduce the data by (default: 3)")
    args = parser.parse_args()
    
    # Load the input file
    filename = args.input_file
    data = np.load(filename)
    ff, pp = data['arr_0'], data['arr_1']
    
    # Calculate the reduced length
    reduce_factor = args.reduce_by
    reduced_length = int(len(ff) / reduce_factor)
    
    # Reduce the data and save to a new file
    reduced_filename = filename + f'_reduced_by_{reduce_factor}.npz'
    np.savez(reduced_filename, ff[:reduced_length], pp[:reduced_length])
    print(f"Reduced data saved to {reduced_filename}")

if __name__ == "__main__":
    main()
