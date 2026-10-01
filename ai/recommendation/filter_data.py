import pandas as pd

INPUT = "data/events_prepared.csv"
OUTPUT = "data/events_filtered.csv"
MIN_USER_EVENTS = 5
MIN_ITEM_EVENTS = 5

df = pd.read_csv(INPUT)
print("Before:", len(df), "rows |", df["user_id"].nunique(), "users |", df["product_id"].nunique(), "items")

for i in range(5):
    user_counts = df["user_id"].value_counts()
    df = df[df["user_id"].isin(user_counts[user_counts >= MIN_USER_EVENTS].index)]
    item_counts = df["product_id"].value_counts()
    df = df[df["product_id"].isin(item_counts[item_counts >= MIN_ITEM_EVENTS].index)]

print("After:", len(df), "rows |", df["user_id"].nunique(), "users |", df["product_id"].nunique(), "items")
print(df["event_type"].value_counts())

df.to_csv(OUTPUT, index=False)
print("Saved to", OUTPUT)