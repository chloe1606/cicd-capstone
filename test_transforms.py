
from transforms import net_revenue


def test_net_revenue_subtracts_refund():
    amount = 100
    refund = 25
    status = "completed"

    result = net_revenue(amount, refund, status)

    assert result == 75, (
        f"net_revenue({amount}, {refund}, '{status}') "
        f"returned {result}, expected 75"
    )