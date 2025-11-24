import pandas as pd
import time
import numpy as np


def validate(actual_result):
    expected_result = pd.read_csv('dmv_fuel_type_passengers_expected.csv')
    if not actual_result.equals(expected_result):
        print("EXPECTED:\n===")
        print(expected_result)
        print("===\nACTUAL:\n===")
        print(actual_result)
        print("===")
        return False
    return True


# using python dict
def query(df):
    ht = {}
    rows = []
    for fuel_type, passengers in zip(df["fuel_type"], df["passengers"]):
        
        passengers_value = 0
        avg_count_value = 0
        if not pd.isna(passengers):
            passengers_value = passengers
            avg_count_value = 1
            
        try:         
            count, value, avg_count = ht[fuel_type]
            ht[fuel_type] = (count + 1, value + passengers_value, avg_count + avg_count_value)
        except KeyError:
            ht[fuel_type] = (1, passengers_value, avg_count_value)
    
    for key, value in ht.items():
            rows.append({"fuel_type": key, "vehicle_count": value[0], "avg_passengers":  round(value[1] / value[2], 1) if value[2] != 0 else float('nan')})

    return pd.DataFrame(rows).sort_values(by="fuel_type", ignore_index=True)


# own hashtable with linear probing
def fast_reduce_16_to_n(h, n):
    """Compute floor(h * n / 2^32) using Python integers."""
    h &= (1 << 16) - 1  
    n &= (1 << 16) - 1  
    res = h * n         
    return res >> 16


def query(df):
    ht_capacity = 20
    WIDTH = 4  # slots per entry: key, count, sum, valid

    ht = [None, 0, 0.0, 0] * ht_capacity

    fuel_types = df["fuel_type"].values 
    passengers_arr = df["passengers"].values  

    count = [0]*ht_capacity
    collisions = 0 
    for fuel_type, passengers in zip(fuel_types, passengers_arr):
        is_valid = passengers == passengers
        
        # Use Python's hash, masked to 64-bit
        idx0 = fast_reduce_16_to_n(hash(fuel_type), ht_capacity-1) if fuel_type == fuel_type else ht_capacity - 1
        
        count[idx0] += 1
        # Linear probing
        idx = idx0
        slot = idx * WIDTH
        
        while ht[slot] and idx0 != ht_capacity - 1 and ht[slot] != fuel_type:
            collisions += 1
            idx = idx + 1
            if idx == ht_capacity-1:
                idx = 0
            slot = idx * WIDTH
 
        # Update
        if not ht[slot]:
            ht[slot] = fuel_type
        ht[slot + 1] += 1
        if is_valid:
            ht[slot + 2] += passengers
            ht[slot + 3] += 1

    rows = [
        {
            "fuel_type": ht[i], 
            "vehicle_count": ht[i + 1], 
            "avg_passengers": round(ht[i + 2] / ht[i + 3], 1) if ht[i + 3] else float('nan')
        }
        for i in range(0, ht_capacity * 4, 4) if ht[i]
    ]

    print(f"{collisions=}")    
    for c in count:
        print(f"{c}")

    return pd.DataFrame(rows).sort_values(by="fuel_type", ignore_index=True)


# Read data
df = pd.read_csv('dmv_fuel_type_passengers.csv')

# Run query (data is loaded before, everything else needs to be timed)
start = time.perf_counter()
result = query(df)
end = time.perf_counter()

# Validate result and print time
if validate(result):
    print(f'Result: {(end - start) * 1e3} ms')
else:
    print("Result: Error")