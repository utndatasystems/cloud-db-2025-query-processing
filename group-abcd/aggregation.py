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

#ex 1
"""
def query(df):
    # Group by fuel_type and compute aggregations
    result = (
        df.groupby("fuel_type")
          .agg(
              vehicle_count=("fuel_type", "size"),
              avg_passengers=("passengers", lambda x: round(x.mean(), 1))
          )
          .reset_index()
          .sort_values("fuel_type")
    )

    return result


    #return pd.DataFrame(columns=['fuel_type', 'vehicle_count', 'avg_passengers'], data=[('X', 0, 0)])


    """

"""
#ex 2
def query(df):
    fuel = df["fuel_type"].to_numpy()
    passengers = df["passengers"].to_numpy()

    # Hash map: fuel_type -> [count, sum_passengers]
    agg = {}

    for f, p in zip(fuel, passengers):
        # do NOT skip NaN
        key = f

        if key in agg:
            agg[key][0] += 1
            agg[key][1] += float(p)
        else:
            agg[key] = [1, float(p)]

    # Custom sort: NaN always last, strings first
    def sort_key(x):
        if pd.isna(x):
            return (1, "")      # put NaN at the end
        return (0, str(x))       # normal strings

    rows = []
    for f in sorted(agg.keys(), key=sort_key):
        c, s = agg[f]
        rows.append((f, c, round(s / c, 1)))

    return pd.DataFrame(rows, columns=["fuel_type", "vehicle_count", "avg_passengers"])

"""

def query(df):
    """
    Pandas-optimized version using efficient groupby operations.
    Often comparable in speed, more readable.
    Treats NaN fuel_type as 'Other' category and places it last.
    """
    if df.empty:
        return pd.DataFrame(columns=['fuel_type', 'vehicle_count', 'avg_passengers'])
    
    # Fill NaN fuel_type with 'Other'
    df_copy = df.copy()
    df_copy['fuel_type'] = df_copy['fuel_type'].fillna('NaN')
    
    result = (df_copy.groupby('fuel_type', sort=True)
              .agg(
                  vehicle_count=('fuel_type', 'size'),
                  avg_passengers=('passengers', lambda x: round(x.mean(), 1))
              )
              .reset_index())
    
    # Move 'Other' to the end
    if 'NaN' in result['fuel_type'].values:
        other_row = result[result['fuel_type'] == 'NaN']
        result = pd.concat([
            result[result['fuel_type'] != 'NaN'],
            other_row
        ], ignore_index=True)
    result.replace('NaN', np.nan, inplace=True)
    return result
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