import pandas as pd
import duckdb
import time
import utils
import os

def validate(actual_result):
  expected_result = pd.read_csv('join_expected.csv')

  # Hint: make sure the types of the data frame match as well: print(expected_result.dtypes)
  if not actual_result.equals(expected_result):
    print("EXPECTED:\n===")
    print(expected_result)
    print("===\nACTUAL:\n===")
    print(actual_result)
    print("===")
    return False
  return True

def query(lineitem_df, part_df):
  start = pd.Timestamp(1995, 9, 1)
  end   = pd.Timestamp(1995, 10, 1)

  # The filter mask.
  mask = (
    (lineitem_df["l_shipdate"] >= start) &
    (lineitem_df["l_shipdate"] <  end)
  )

  # Join.
  merged = lineitem_df[mask].merge(
    part_df,
    left_on='l_partkey',
    right_on='p_partkey',
    how='inner'
  )

  # And return.
  return pd.DataFrame({'volume': [int(merged["l_extendedprice"].sum())]})

# ---------------------------------------------------------
# Load or generate data
# ---------------------------------------------------------

# Cache two tables to Parquet only if not already present
if not os.path.exists('lineitem.parquet') or not os.path.exists('part.parquet'):
  utils.enforce_parquet_files()
else:
  print('Using the cached Parquet files.')

# Open the connection.
con = duckdb.connect(database=':memory:', read_only=False)

# Run the schema.
con.execute(utils.tpch_schema)

# Load the tables into DuckDB.
lineitem_df = con.sql(f'select * from read_parquet(\'lineitem.parquet\');').fetchdf()
part_df = con.sql(f'select * from read_parquet(\'part.parquet\');').fetchdf()

# ---------------------------------------------------------
# Run query (generation & loading must happen before timing)
# ---------------------------------------------------------
start = time.perf_counter()
result = query(lineitem_df, part_df)
end = time.perf_counter()

# Validate result and print time
if validate(result):
  print(f'Result: {(end - start) * 1e3} ms')
else:
  print("Result: Error")