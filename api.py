from flask import Flask, request, jsonify
import joblib
import pandas as pd

app = Flask(__name__)

# تحميل الموديل المحفوظ
model = joblib.load('model.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        
        # تحويل الـ JSON لـ DataFrame
        df = pd.DataFrame([data])
        
        # التوقع باستخدام الموديل
        prediction = model.predict(df)[0]
        
        return jsonify({
            "status": "success",
            "prediction": int(prediction),
            "cart_abandoned": int(prediction) == 0
        })
    except Exception as e:
        # إرجاع تفاصيل الخطأ بوضوح
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    app.run(port=5001, debug=True)