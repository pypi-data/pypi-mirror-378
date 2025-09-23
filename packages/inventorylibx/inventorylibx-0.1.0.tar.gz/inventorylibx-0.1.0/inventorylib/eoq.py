import math

def calculate_eoq(demand, order_cost, holding_cost):
    """
    Calculate Economic Order Quantity (EOQ).

    EOQ = sqrt( (2 * demand * order_cost) / holding_cost )
    """
    return math.sqrt((2 * demand * order_cost) / holding_cost)