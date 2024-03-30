import numpy as np
import cupy as cp


def savez(file, *args, **kwds):
    """
    Save several arrays into a single file in uncompressed .npz format.
    If arguments are passed in with no keywords, the corresponding variable names will be used.
    If keyword arguments are given, the corresponding keys will be used.
    """
    npArgs = []
    for val in args:
        if isinstance(val, cp.ndarray):
            npArgs.append(val.get())
        else:
            npArgs.append(val)

    npDict = {}
    for key, val in kwds.items():
        if isinstance(val, cp.ndarray):
            npDict[key] = val.get()
        else:
            npDict[key] = val

    np.savez(file, *npArgs, **npDict)
