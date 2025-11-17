import pandas as pd
import time


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

    sorted_df = df.sort_values(by="fuel_type")

    previous = ""

    rows = []
    current_count = 0
    current_agg = 0
    for fuel_type, passengers in zip(sorted_df["fuel_type"], sorted_df["passengers"]):
        if fuel_type == previous:
            current_count = current_count + 1
            current_agg = current_agg + passengers
            
        else:
            rows.append({"fuel_type": fuel_type, "vehicle_count": current_count, "avg_passengers": passengers})
            current_count = 0
            current_agg = 0
        previous = fuel_type


    return pd.DataFrame(rows)


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