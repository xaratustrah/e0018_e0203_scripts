# G22-00018_00203 scripts

Script to loop-process the files on the server during the G22-00018 and G22-00203 experiment, and then copy them to different locations:


#### NPZ file
You can read it like this (you may need to flatten one array)

```python
data = np.load('filename.npz')
xx, yy, zz, center = data['arr_0'], data['arr_1'], data['arr_2']
```

Note that you can `flatten` arrays before use, or just make a `float()` cast if it is just a number.
