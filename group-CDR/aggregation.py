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

# too slow to sort first
# def query2(df):
#     sorted_df = df.sort_values(by="fuel_type")

#     previous = sorted_df["fuel_type"].iloc[0]
#     rows = []
#     current_count = 0
#     avg_count = 0
#     current_agg = 0

#     for fuel_type, passengers in zip(sorted_df["fuel_type"], sorted_df["passengers"]):
#         if pd.isna(fuel_type):
#             fuel_type = "NaN"
#         if fuel_type == previous:
#             current_count += 1
#             if not pd.isna(passengers):
#                 current_agg += passengers
#                 avg_count += 1

#         else:
#             if avg_count == 0:
#                 avg = "NaN"  
#             else:
#                 avg = round(current_agg / avg_count, 1)
#             rows.append({
#                 "fuel_type": previous,
#                 "vehicle_count": current_count,
#                 "avg_passengers": avg,
#             })

#             # reset for new group
#             previous = fuel_type
#             current_count = 1
#             avg_count = 0
#             if not pd.isna(passengers):
#                 current_agg = passengers
#             else: current_agg = 0

#     # append the last group
#     if avg_count == 0:
#         avg = "NaN"  
#     else:
#         avg = round(current_agg / avg_count, 1)
#     rows.append({
#         "fuel_type": previous,
#         "vehicle_count": current_count,
#         "avg_passengers": avg, 
#     })

#     return pd.DataFrame(rows)


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