import pandas as pd
import time


def validate(actual_result):
    expected_result = pd.read_csv('/Users/Shared/GitHub/cloud-db-2025-query-processing/dmv_fuel_type_passengers_expected.csv')
    if not actual_result.equals(expected_result):
        print("EXPECTED:\n===")
        print(expected_result)
        print("===\nACTUAL:\n===")
        print(actual_result)
        print("===")
        return False
    return True


def query(df):
    rows = df.to_dict('records')

    aggregates = {}
    for row in rows:
        fuel_type = row['fuel_type']
        passengers = row['passengers']
        # treat empty or NaN fuel_type as None
        if fuel_type == '' or fuel_type is None or (isinstance(fuel_type, float) and pd.isna(fuel_type)):
            fuel_type = None
        if fuel_type not in aggregates:
            aggregates[fuel_type] = {'count': 0, 'sum_passengers': 0.0}
        aggregates[fuel_type]['count'] += 1
        aggregates[fuel_type]['sum_passengers'] += float(passengers)

    result_list = []
    for fuel_type, agg in aggregates.items():
        avg_passengers = round(agg['sum_passengers'] / agg['count'], 1) if agg['count'] > 0 else None
        result_list.append({
            'fuel_type': fuel_type if fuel_type is not None else '',
            'vehicle_count': agg['count'],
            'avg_passengers': avg_passengers
        })

    def sort_key(x):
        # Place None or empty fuel_type at the end of sorting
        fuel_type_value = x['fuel_type']
        # Treat empty string as None for sorting
        if fuel_type_value == '' or fuel_type_value is None:
            return (1, '')  # putting these at the end
        return (0, fuel_type_value)

    result_list.sort(key=sort_key)
    return pd.DataFrame(result_list).reset_index(drop=True)



# Read data
df = pd.read_csv('/Users/Shared/GitHub/cloud-db-2025-query-processing/dmv_fuel_type_passengers.csv')

# Run query (data is loaded before, everything else needs to be timed)
start = time.perf_counter()
result = query(df)
end = time.perf_counter()

# Validate result and print time
if validate(result):
    print(f'Result: {(end - start) * 1e3} ms')
else:
    print("Result: Error")
