# e018_scripts

Script to loop-process the files on the server during the E018 experiment, and then copy them to different locations.


#### NPZ file
You can read it like this (you may need to flatten one array)

```python
data = np.load('filename.npz')
xx, yy, zz, center = data['arr_0'], data['arr_1'], data['arr_2'], data['arr_3']
```

note that you can `flaten` arrays before use, or just make a `float()` cast.

