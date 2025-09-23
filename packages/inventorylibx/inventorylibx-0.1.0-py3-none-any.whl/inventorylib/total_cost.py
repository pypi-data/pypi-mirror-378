def calculate_total_cost(demand, order_cost, holding_cost, order_qty):
    """
    Calculate Total Cost (Ordering + Holding).

    TC(Q) = (D/Q) * Co + (Q/2) * Ch
    """
    ordering_cost = (demand / order_qty) * order_cost
    holding_cost_total = (order_qty / 2) * holding_cost
    return ordering_cost + holding_cost_total
