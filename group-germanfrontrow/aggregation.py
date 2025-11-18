import pandas as pd
import time
from collections import defaultdict
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


def query(df):
    # TODO: Implement the query and return a data frame with the result.
    # select fuel_type,
    #        count(*) as vehicle_count,
    #        round(avg(passengers), 1) as avg_passengers
    # from dmv
    # group by fuel_type
    # order by fuel_type;

    # Use direct array access instead of iterrows
    step_start = time.perf_counter()
    fuel_types = df['fuel_type'].values
    passengers = df['passengers'].values
    step_end = time.perf_counter()
    print(f"Step 1 - Extract arrays: {(step_end - step_start) * 1e3:.2f} ms")
    
    # Create mask for NaN fuel types (vectorized)
    step_start = time.perf_counter()
    is_nan_mask = pd.isna(fuel_types)
    fuel_types_clean = np.where(is_nan_mask, '', fuel_types)
    step_end = time.perf_counter()
    print(f"Step 1b - Vectorized NaN handling: {(step_end - step_start) * 1e3:.2f} ms")
    
    # create hash map using defaultdict for fuel_type to (vehicle_count, total_passengers, passenger_count)
    step_start = time.perf_counter()
    fuel_map = defaultdict(lambda: [0, 0.0, 0])
    
    for i in range(len(fuel_types_clean)):
        fuel_type = fuel_types_clean[i]
        passenger_count = passengers[i]
        
        fuel_map[fuel_type][0] += 1
        
        # Handle NaN passengers - single check
        if passenger_count == passenger_count:  # Not NaN
            fuel_map[fuel_type][1] += passenger_count
            fuel_map[fuel_type][2] += 1
    
    step_end = time.perf_counter()
    total_time = (step_end - step_start) * 1e3
    print(f"Step 2 - Aggregate data: {total_time:.2f} ms")
    
    # prepare result data
    step_start = time.perf_counter()
    result_data = []
    # Sort with empty string last (it will be converted to NaN)
    sorted_keys = sorted(fuel_map.keys(), key=lambda x: (x == '', x))
    step_end = time.perf_counter()
    print(f"Step 3 - Sort keys: {(step_end - step_start) * 1e3:.2f} ms")
    
    step_start = time.perf_counter()
    for fuel_type in sorted_keys:
        vehicle_count = fuel_map[fuel_type][0]
        total_passengers = fuel_map[fuel_type][1]
        count_with_passengers = fuel_map[fuel_type][2]
        if count_with_passengers == 0:
            avg_passengers = float('nan')
        else:
            avg_passengers = round(total_passengers / count_with_passengers, 1)
        # Convert empty string back to NaN for display
        display_fuel_type = float('nan') if fuel_type == '' else fuel_type
        result_data.append((display_fuel_type, vehicle_count, avg_passengers))
    step_end = time.perf_counter()
    print(f"Step 4 - Build result data: {(step_end - step_start) * 1e3:.2f} ms")

    step_start = time.perf_counter()
    result_df = pd.DataFrame(columns=['fuel_type', 'vehicle_count', 'avg_passengers'], data=result_data)
    step_end = time.perf_counter()
    print(f"Step 5 - Create DataFrame: {(step_end - step_start) * 1e3:.2f} ms")
    
    return result_df

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