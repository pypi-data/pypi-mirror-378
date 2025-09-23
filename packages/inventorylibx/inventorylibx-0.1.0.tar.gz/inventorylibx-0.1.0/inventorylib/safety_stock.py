def calculate_safety_stock(z_score, demand_std_dev, lead_time):
    """
    Calculate Safety Stock (SS).

    SS = Z × σ × sqrt(Lead Time)

    Parameters:
    z_score (float): Service level factor (e.g., 1.65 for 95%)
    demand_std_dev (float): Standard deviation of demand
    lead_time (float): Lead time
    """
    return z_score * demand_std_dev * (lead_time ** 0.5)
