import duckdb

tpch_schema = """
  drop table if exists lineitem;
  drop table if exists part;

  create table lineitem (
    l_orderkey      integer        not null,
    l_partkey       integer        not null,
    l_suppkey       integer        not null,
    l_linenumber    integer        not null,
    l_quantity      decimal(12, 2) not null,
    l_extendedprice decimal(12, 2) not null,
    l_discount      decimal(12, 2) not null,
    l_tax           decimal(12, 2) not null,
    l_returnflag    text           not null,
    l_linestatus    text           not null,
    l_shipdate      date           not null,
    l_commitdate    date           not null,
    l_receiptdate   date           not null,
    l_shipinstruct  text           not null,
    l_shipmode      text           not null,
    l_comment       text           not null
  );

  create table part (
    p_partkey     integer        not null,
    p_name        text           not null,
    p_mfgr        text           not null,
    p_brand       text           not null,
    p_type        text           not null,
    p_size        integer        not null,
    p_container   text           not null,
    p_retailprice decimal(12, 2) not null,
    p_comment     text           not null
  );
"""

def enforce_parquet_files():
  print("Parquet files not found. Generating...")

  # Create the connection.
  con = duckdb.connect(database=':memory:', read_only=False)

  # Load TPCH extension.
  con.execute("INSTALL tpch;")
  con.execute("LOAD tpch;")

  # Generate SF=1 TPC-H dataset (creates all TPCH tables).
  con.execute("CALL dbgen(sf=1);")

  # Cache two tables to Parquet.
  con.execute("COPY lineitem TO 'lineitem.parquet' (FORMAT PARQUET);")
  con.execute("COPY part     TO 'part.parquet'     (FORMAT PARQUET);")

  # Close the connection.
  con.close()