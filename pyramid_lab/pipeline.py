import duckdb

REVENUE_SQL = """
  select
    order_id,
    case when status = 'cancelled' then 0
         else amount + coalesce(refund_amount, 0) # bug
    end as net_revenue
  from stg_orders
  order by order_id
"""

def build_revenue(con: duckdb.DuckDBPyConnection):
    return con.execute(REVENUE_SQL).fetchall()