def net_revenue(amount, refund, status):
    if status == "cancelled":
        return 0
    return amount - (refund or 0)

def test_net_revenue_subtracts_refund():
    amount = 100
    refund = 25
    status = "completed"

    result = net_revenue(amount, refund, status)

    assert result == 75, (
        f"net_revenue({amount}, {refund}, '{status}') "
        f"returned {result}, expected 75"
    )