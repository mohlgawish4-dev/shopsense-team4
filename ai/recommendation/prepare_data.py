import pandas as pd

INPUT = "data/retailrocket_events.csv"
OUTPUT = "data/events_prepared.csv"
SESSION_GAP_MS = 30 * 60 * 1000

df = pd.read_csv(INPUT)
print("Rows loaded:", len(df))

df = df.rename(columns={
    "visitorid": "user_id",
    "itemid": "product_id",
    "event": "event_type",
})

df["event_type"] = df["event_type"].replace({
    "view": "click",
    "addtocart": "add_to_cart",
    "transaction": "purchase",
})

df = df.sort_values(["user_id", "timestamp"]).reset_index(drop=True)

gap = df.groupby("user_id")["timestamp"].diff()
new_session = gap.isna() | (gap > SESSION_GAP_MS)
df["session_num"] = new_session.groupby(df["user_id"]).cumsum()
df["session_id"] = df["user_id"].astype(str) + "_" + df["session_num"].astype(str)

out = df[["user_id", "session_id", "event_type", "product_id", "timestamp"]]
out.to_csv(OUTPUT, index=False)

print("Rows saved:", len(out))
print(out["event_type"].value_counts())
print(out.head())