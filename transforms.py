def net_revenue(amount, refund, status):
    if status == "cancelled":
        return 0
    return amount - (refund or 0) # fixed bug   
