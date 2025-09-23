import math

def calculate_bulk_discount_eoq(demand, order_cost, holding_cost, price_breaks):
    """
    Calculate EOQ with Bulk Discounts.

    Parameters:
    demand (float): Annual demand
    order_cost (float): Ordering cost per order
    holding_cost (float): Holding cost rate (as % of unit cost)
    price_breaks (list of tuples): [(min_qty, unit_price), ...]

    Returns:
    dict: Best order quantity and cost
    """
    results = []

    for min_qty, unit_price in price_breaks:
        # Holding cost depends on unit price
        hc = holding_cost * unit_price
        
        # EOQ at this price level
        eoq = math.sqrt((2 * demand * order_cost) / hc)
        
        # Adjust EOQ if it's below minimum quantity for discount
        if eoq < min_qty:
            eoq = min_qty
        
        # Total cost = purchase + ordering + holding
        total_cost = demand * unit_price \
                   + (demand / eoq) * order_cost \
                   + (eoq / 2) * hc

        results.append((eoq, unit_price, total_cost))
    
    # Choose option with lowest total cost
    best_option = min(results, key=lambda x: x[2])
    
    return {
        "order_qty": best_option[0],
        "unit_price": best_option[1],
        "total_cost": best_option[2]
    }
