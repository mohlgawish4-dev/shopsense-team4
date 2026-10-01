import pickle
import numpy as np
from flask import Flask, jsonify, request

MODEL_PATH = "model.pkl"

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

item_sim = model["item_sim"]
matrix = model["matrix"]
user_index = model["user_index"]
item_index = model["item_index"]
index_to_item = model["index_to_item"]
popular = model["popular"]

app = Flask("recommendation")


def recommend(user_id, n=5):
    uidx = user_index.get(user_id)
    if uidx is None:
        return popular[:n]

    user_row = matrix.getrow(uidx)
    seen = set(user_row.indices)

    scores = np.zeros(item_sim.shape[0])
    for idx, w in zip(user_row.indices, user_row.data):
        sim_row = item_sim.getrow(idx)
        scores[sim_row.indices] += sim_row.data * w

    for idx in seen:
        scores[idx] = -1

    top = np.argsort(scores)[::-1][:n]
    return [index_to_item[i] for i in top]


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/recommend/<int:user_id>")
def get_recommendations(user_id):
    n = request.args.get("n", default=5, type=int)
    recs = recommend(user_id, n)
    return jsonify({"user_id": user_id, "recommendations": [int(p) for p in recs]})


app.run(port=5001)