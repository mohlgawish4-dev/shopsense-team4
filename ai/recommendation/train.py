import pickle
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.preprocessing import normalize

INPUT = "data/events_filtered.csv"
MODEL_PATH = "model.pkl"
WEIGHTS = {"click": 1, "add_to_cart": 3, "purchase": 5}

df = pd.read_csv(INPUT)
df["weight"] = df["event_type"].map(WEIGHTS)

interactions = df.groupby(["user_id", "product_id"], as_index=False)["weight"].sum()

user_ids = interactions["user_id"].astype("category")
item_ids = interactions["product_id"].astype("category")

user_index = {u: i for i, u in enumerate(user_ids.cat.categories)}
item_index = {p: i for i, p in enumerate(item_ids.cat.categories)}
index_to_item = list(item_ids.cat.categories)

matrix = csr_matrix(
    (interactions["weight"].values, (user_ids.cat.codes, item_ids.cat.codes)),
    shape=(len(user_index), len(item_index)),
)
print("Matrix shape (users x items):", matrix.shape)

item_matrix = normalize(matrix.T.tocsr())
item_sim = (item_matrix @ item_matrix.T).tocsr()
print("Similarity computed")

popular = (
    interactions.groupby("product_id")["weight"].sum()
    .sort_values(ascending=False)
    .index.tolist()
)

model = {
    "matrix": matrix,
    "item_sim": item_sim,
    "user_index": user_index,
    "item_index": item_index,
    "index_to_item": index_to_item,
    "popular": popular,
}

with open(MODEL_PATH, "wb") as f:
    pickle.dump(model, f)

print("Model saved to", MODEL_PATH)