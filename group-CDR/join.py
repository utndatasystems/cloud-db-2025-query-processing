import pandas as pd
import duckdb
import time
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
    #    select sum(l_extendedprice)::bigint as volume
    #    from lineitem, part
    #    where l_partkey = p_partkey
    #    and l_shipdate >= date '1995-09-01'
    #    and l_shipdate < date '1995-10-01';

    lineitem = con.sql("""
        SELECT l_extendedprice, l_partkey, l_shipdate
        FROM lineitem
    """).fetchdf()

    part = con.sql("""
        SELECT p_partkey
        FROM part
    """).fetchdf()

    # build hash table for lineitem (likely smaller due to filters)
    ht = {}
    volume = 0
    for l_tuple in lineitem.itertuples(index=False):
        if l_tuple.l_shipdate >= pd.Timestamp('1995-09-01') and l_tuple.l_shipdate < pd.Timestamp('1995-10-01'):
            try:
                ht[l_tuple.l_partkey] +=  l_tuple.l_extendedprice
            except KeyError:
                ht[l_tuple.l_partkey] =  l_tuple.l_extendedprice
    
    for p_tuple in part.itertuples(index=False):
        try: 
            volume += ht[p_tuple.p_partkey]
        except KeyError:
            continue
        

    return pd.DataFrame({'volume': [int(volume)]})


# ---------------------------------------------------------
# Load or generate data
# ---------------------------------------------------------

con = duckdb.connect(database=':memory:', read_only=False)

if not (os.path.exists("lineitem-parquet") and os.path.exists("part-parquet")):
    # Load TPCH extension
    con.execute("INSTALL tpch;")
    con.execute("LOAD tpch;")

    # Generate SF=1 TPC-H dataset (creates all TPCH tables)
    con.execute("CALL dbgen(sf=1);")

    # Cache two tables to Parquet
    con.execute("COPY lineitem TO 'lineitem.parquet' (FORMAT PARQUET);")
    con.execute("COPY part     TO 'part.parquet'     (FORMAT PARQUET);")

    # Drop the auto-generated TPCH tables to reload into your schema
    con.execute("DROP TABLE lineitem;")
    con.execute("DROP TABLE part;")


# ---------------------------------------------------------
# Recreate schema & reload from Parquet
# ---------------------------------------------------------

schema = """
    drop table if exists lineitem;
    drop table if exists part;

    create table lineitem
    (
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
con.execute(schema)

# Load cached Parquet
con.execute("INSERT INTO lineitem SELECT * FROM read_parquet('lineitem.parquet');")
con.execute("INSERT INTO part     SELECT * FROM read_parquet('part.parquet');")


# ---------------------------------------------------------
# Run query (generation & loading must happen before timing)
# ---------------------------------------------------------
start = time.time()
result = query(con)
end = time.time()

# Validate result and print time
if validate(result):
    print("Result:", end - start)
else:
    print("Result: Error")