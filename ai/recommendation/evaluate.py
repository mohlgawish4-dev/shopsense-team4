import pickle
import numpy as np
import pandas as pd

INPUT = "data/events_filtered.csv"
MODEL_PATH = "model.pkl"
K = 5
MAX_USERS = 2000
WEIGHTS = {"click": 1, "add_to_cart": 3, "purchase": 5}

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

item_sim = model["item_sim"]
item_index = model["item_index"]
index_to_item = model["index_to_item"]
popular = model["popular"]

df = pd.read_csv(INPUT)
df["weight"] = df["event_type"].map(WEIGHTS)
df = df.sort_values(["user_id", "timestamp"])

rng = np.random.default_rng(42)
users = df["user_id"].unique()
rng.shuffle(users)

hits_model = 0
hits_pop = 0
tested = 0

for u in users:
    if tested >= MAX_USERS:
        break
    udf = df[df["user_id"] == u].drop_duplicates("product_id", keep="last")
    if len(udf) < 3:
        continue

    held_out = udf.iloc[-1]["product_id"]
    history = udf.iloc[:-1]
    seen = set(history["product_id"])

    scores = np.zeros(item_sim.shape[0])
    for pid, w in zip(history["product_id"], history["weight"]):
        idx = item_index.get(pid)
        if idx is None:
            continue
        row = item_sim.getrow(idx)
        scores[row.indices] += row.data * w

    for pid in seen:
        idx = item_index.get(pid)
        if idx is not None:
            scores[idx] = -1

    top = np.argsort(scores)[::-1][:K]
    rec_model = [index_to_item[i] for i in top]

    rec_pop = [p for p in popular if p not in seen][:K]

    hits_model += held_out in rec_model
    hits_pop += held_out in rec_pop
    tested += 1

print("Users tested:", tested)
print("Hit Rate@%d  Model:      %.4f" % (K, hits_model / tested))
print("Hit Rate@%d  Popularity: %.4f" % (K, hits_pop / tested))