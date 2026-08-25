import duckdb

from ..pipeline import build_revenue


def test_output_shape():
    con = duckdb.connect()

    con.execute("""
        create table stg_orders (
            order_id integer,
            amount integer,
            refund_amount integer,
            status varchar
        )
    """)

    con.execute("""
        insert into stg_orders
        values (1, 100, null, 'completed')
    """)

    result = build_revenue(con)

    assert len(result) == 1
    assert len(result[0]) == 2