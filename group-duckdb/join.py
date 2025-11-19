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


def query(con):
  # TODO: Implement the query and return a data frame with the result.
  # NOTE: Don't use duckdb or built-in pandas functions for the join!
  # NOTE: Your join operator should be done manually.
  return con.sql(f"""
    select sum(l_extendedprice)::bigint as volume
    from lineitem, part
    where l_partkey = p_partkey
    and l_shipdate >= date '1995-09-01'
    and l_shipdate < date '1995-10-01';
  """).fetchdf()

# ---------------------------------------------------------
# Load or generate data
# ---------------------------------------------------------

# Cache two tables to Parquet only if not already present
if not os.path.exists('lineitem.parquet') or not os.path.exists('part.parquet'):
  utils.enforce_parquet_files()
else:
  print('Using the cached Parquet files.')

# ---------------------------------------------------------
# Recreate schema & reload from Parquet
# ---------------------------------------------------------

# Open the connection.
con = duckdb.connect(database=':memory:', read_only=False)

# Run the schema.
con.execute(utils.tpch_schema)

# Load the tables into DuckDB.
con.execute('INSERT INTO lineitem SELECT * FROM read_parquet(\'lineitem.parquet\');')
con.execute('INSERT INTO part     SELECT * FROM read_parquet(\'part.parquet\');')

# ---------------------------------------------------------
# Run query (generation & loading must happen before timing)
# ---------------------------------------------------------
start = time.perf_counter()
result = query(con)
end = time.perf_counter()

# Validate result and print time
if validate(result):
  print(f'Result: {(end - start) * 1e3} ms')
else:
  print("Result: Error")