import duckdb

from ..pipeline import build_revenue


def test_refund_is_subtracted():
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
        values (1, 100, 25, 'completed')
    """)

    result = build_revenue(con)

    assert result == [(1, 75)]