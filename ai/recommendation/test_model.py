import pickle

with open("model.pkl", "rb") as f:
    data = pickle.load(f)

sim_df = data["sim_df"]
matrix = data["matrix"]

for uid in [1, 2, 3, 9999]:
    if uid in matrix.index:
        user_scores = matrix.loc[uid]
        scores = sim_df.dot(user_scores)
        scores = scores.drop(user_scores[user_scores > 0].index)
        print("user", uid, "->", scores.nlargest(5).index.tolist())
    else:
        print("user", uid, "-> new user")