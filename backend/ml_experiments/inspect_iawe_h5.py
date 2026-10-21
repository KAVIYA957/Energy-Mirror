"""
inspect_iawe_h5.py - Deep forensic inspection of iAWE HDF5 structure.
Reads groups, datasets, attributes, tables, meters, and ground truth for Water Motor.
"""

import os
import sys
import json
import h5py
import numpy as np
import pandas as pd

H5_PATH = os.path.join(os.path.dirname(__file__), "data", "iawe.h5")

def inspect_h5():
    if not os.path.exists(H5_PATH):
        print(f"File not found: {H5_PATH}")
        return

    size_mb = os.path.getsize(H5_PATH) / (1024 * 1024)
    print(f"=== iAWE HDF5 Inspection ===")
    print(f"File: {H5_PATH} ({size_mb:.2f} MB)")

    with h5py.File(H5_PATH, "r") as f:
        print("\n--- Root Groups and Attributes ---")
        for k in f.keys():
            print(f"Key: {k} -> {type(f[k])}")
            for attr_name, attr_val in f[k].attrs.items():
                print(f"  Attr [{attr_name}]: {str(attr_val)[:100]}")

        # Recursively explore tree
        print("\n--- Full Tree Walk ---")
        def visitor(name, obj):
            if isinstance(obj, h5py.Dataset):
                print(f"  [Dataset] {name} | shape={obj.shape} | dtype={obj.dtype}")
            elif isinstance(obj, h5py.Group):
                print(f"  [Group]   {name}")
                for ak, av in obj.attrs.items():
                    print(f"    attr: {ak} = {str(av)[:80]}")
        f.visititems(visitor)

if __name__ == "__main__":
    inspect_h5()
