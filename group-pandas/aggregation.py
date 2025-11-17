import pandas as pd
import time


def validate(actual_result):
    expected_result = pd.read_csv('../dmv_fuel_type_passengers_expected.csv')
    if not actual_result.equals(expected_result):
        print("EXPECTED:\n===")
        print(expected_result)
        print("===\nACTUAL:\n===")
        print(actual_result)
        print("===")
        return False
    return True


def query(df):
    result = (
        # Do keep NaN groups.
        df.groupby('fuel_type', dropna=False)
          .agg(
              vehicle_count=('fuel_type', 'size'),
              avg_passengers=('passengers', 'mean')
          )
          .reset_index()
    )

    result['avg_passengers'] = result['avg_passengers'].round(1)

    return result.sort_values('fuel_type')


# Read data
df = pd.read_csv('../dmv_fuel_type_passengers.csv')

# Run query (data is loaded before, everything else needs to be timed)
start = time.perf_counter()
result = query(df)
end = time.perf_counter()

# Validate result and print time
if validate(result):
    print(f'Result: {(end - start) * 1e3} ms')
else:
    print("Result: Error")
