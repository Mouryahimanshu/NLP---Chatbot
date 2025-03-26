import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import random

# Page configuration
st.set_page_config(page_title="Inventory Management Simulator", layout="wide")
st.title("📦 Inventory Management Simulation")

# Sidebar controls
with st.sidebar:
    st.header("Simulation Parameters")
    
    # EOQ Parameters
    st.subheader("EOQ Model")
    annual_demand = st.number_input("Annual Demand (units)", 1000, 100000, 10000)
    order_cost = st.number_input("Order Cost ($/order)", 10, 500, 100)
    holding_cost = st.number_input("Holding Cost ($/unit/year)", 1, 20, 5)
    
    # Reorder Point Parameters
    st.subheader("Reorder Point")
    avg_daily_demand = st.number_input("Average Daily Demand", 10, 200, 50)
    lead_time_days = st.number_input("Lead Time (days)", 1, 30, 7)
    service_level = st.slider("Service Level", 0.80, 0.99, 0.95)
    demand_std = st.number_input("Demand Std Dev", 1, 30, 10)
    
    # Simulation Parameters
    st.subheader("Simulation")
    simulation_days = st.number_input("Simulation Days", 30, 730, 365)
    initial_stock = st.number_input("Initial Stock", 100, 2000, 500)

# Calculate EOQ
def calculate_eoq(demand, order_cost, holding_cost):
    return np.sqrt((2 * demand * order_cost) / holding_cost)

# Calculate Reorder Point
def calculate_reorder_point(avg_daily, lead_time, service_level, demand_std):
    z_score = norm.ppf(service_level)
    safety_stock = z_score * demand_std * np.sqrt(lead_time)
    return (avg_daily * lead_time) + safety_stock

# Run Simulation
def run_simulation(days, initial_stock, reorder_point, order_quantity, lead_time):
    inventory = initial_stock
    on_order = 0
    days_until_delivery = 0
    stockouts = 0
    inventory_levels = []
    
    for day in range(days):
        demand = random.randint(
            max(1, avg_daily_demand - 2*demand_std),
            avg_daily_demand + 2*demand_std
        )
        
        if days_until_delivery == 1:
            inventory += on_order
            on_order = 0
        
        if inventory >= demand:
            inventory -= demand
        else:
            stockouts += 1
            inventory = 0
        
        if inventory <= reorder_point and on_order == 0:
            on_order = order_quantity
            days_until_delivery = lead_time
        elif days_until_delivery > 0:
            days_until_delivery -= 1
        
        inventory_levels.append(inventory)
    
    return inventory_levels, stockouts

# Main calculations
eoq = calculate_eoq(annual_demand, order_cost, holding_cost)
rop = calculate_reorder_point(avg_daily_demand, lead_time_days, service_level, demand_std)

# Display results
col1, col2 = st.columns(2)
with col1:
    st.metric("Economic Order Quantity (EOQ)", f"{eoq:.0f} units")
with col2:
    st.metric("Reorder Point with Safety Stock", f"{rop:.0f} units")

# Run and plot simulation
if st.button("Run Simulation"):
    inventory_levels, stockouts = run_simulation(
        days=simulation_days,
        initial_stock=initial_stock,
        reorder_point=rop,
        order_quantity=eoq,
        lead_time=lead_time_days
    )
    
    st.success(f"Simulation complete! Stockouts occurred on {stockouts} days ({stockouts/simulation_days*100:.1f}% of time)")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(inventory_levels, label='Inventory Level')
    ax.axhline(y=rop, color='r', linestyle='--', label='Reorder Point')
    ax.set_title('Inventory Levels Over Time')
    ax.set_xlabel('Day')
    ax.set_ylabel('Units in Stock')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
    
    # Additional metrics
    avg_inventory = np.mean(inventory_levels)
    min_inventory = min(inventory_levels)
    st.write(f"""
    - *Average Inventory Level*: {avg_inventory:.0f} units
    - *Minimum Inventory Level*: {min_inventory} units
    - *Service Level Achieved*: {(1 - stockouts/simulation_days)*100:.1f}%
    """)

# # How to run instructions
# st.markdown("""
# ### How to Use This Simulator
# 1. Adjust parameters in the sidebar
# 2. Click "Run Simulation"
# 3. View results and inventory trends

# ### Key Concepts Simulated:
# - *EOQ*: Optimal order quantity to minimize costs
# - *Reorder Point*: When to place new orders
# - *Safety Stock*: Buffer for demand variability
# - *Service Level*: Probability of avoiding stockouts
# """)
