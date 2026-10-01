import numpy as np
import pandas as pd

np.random.seed(42)

N_USERS = 200
N_PRODUCTS = 50
N_EVENTS = 5000

categories = ["electronics", "clothing", "books", "home", "sports"]
products = pd.DataFrame({
    "product_id": range(1, N_PRODUCTS + 1),
    "name": [f"Product {i}" for i in range(1, N_PRODUCTS + 1)],
    "category": np.random.choice(categories, N_PRODUCTS),
})

event_types = ["click", "add_to_cart", "purchase"]
events = pd.DataFrame({
    "user_id": np.random.randint(1, N_USERS + 1, N_EVENTS),
    "session_id": np.random.randint(1, 1000, N_EVENTS),
    "event_type": np.random.choice(event_types, N_EVENTS, p=[0.7, 0.2, 0.1]),
    "product_id": np.random.randint(1, N_PRODUCTS + 1, N_EVENTS),
    "timestamp": pd.date_range("2026-09-01", periods=N_EVENTS, freq="5min"),
})

products.to_csv("products.csv", index=False)
events.to_csv("events.csv", index=False)
print("Done:", len(products), "products,", len(events), "events")