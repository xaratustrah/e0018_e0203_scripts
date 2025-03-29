# e0018 and e0203 scripts

Script for multiprocess looping of the files on the server during the G22-00018 and G22-00203 experiment, and then copy the results to different locations.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

The settings are in a TOML file. In order to know the number of available cores on your system you may:

```python
import multiprocessing
print("Number of CPU cores:", multiprocessing.cpu_count())
```

run the command with:

```bash
python looper.py --config looper_cfg.toml
```

#### NPZ file
You can read it like this (you may need to flatten one array)

```python
data = np.load('filename.npz')
xx, yy, zz, center = data['arr_0'], data['arr_1'], data['arr_2']
```

Note that you can `flatten` arrays before use, or just make a `float()` cast if it is just a number.
