# Recommendation System - ShopSense

الـ AI model بتاع الـ Recommendation، عبارة عن Flask API لوحده جوه ai/recommendation/.

## بيعمل إيه

بياخد user_id ويرجع المنتجات المتوقع تعجبه، based on تشابهه مع يوزرز تانيين تفاعلوا مع نفس المنتجات (clicks / add to cart / purchase).

## ليه RetailRocket مش الـ dummy data

درّبت الموديل على RetailRocket dataset (داتا حقيقية، ~2.7 مليون event) بدل seed data، عشان الأرقام تبقى حقيقية مش شكلية. لما events table بتاعتنا يبقى فيها traffic كفاية، نفس الـ pipeline هيشتغل، بس هنبدّل المصدر من CSV لـ Postgres من غير ما نلمس المنطق.

## إزاي شغال

1. prepare_data.py - بينضف الداتا ويعمل sessions (فاصل 30 دقيقة)
2. filter_data.py - بيشيل اليوزرز/المنتجات اللي تفاعلاتهم أقل من 5
3. train.py - item-item similarity بـ cosine similarity، بأوزان click=1, add_to_cart=3, purchase=5، وfallback للأكثر شعبية لو cold start. بيحفظ model.pkl
4. evaluate.py - Hit Rate@5 = 0.2305 مقابل 0.0005 لو رشحنا الأكثر شعبية بس (يعني تقريباً 460 ضعف أحسن)
5. api.py - الـ Flask API، بورت 5001

## طريقه التشغيل

cd ai/recommendation
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
وبعدين بالترتيب:

python prepare_data.py
python filter_data.py
python train.py
python evaluate.py
python api.py
## API

- GET /health - health check
- GET /recommend/<user_id>?n=5 - يرجع أفضل n منتج ليوزر معين، fallback للأكثر شعبية لو اليوزر مش معروف

## Note

data/, model.pkl, venv/ مش موجودين في الريبو (حجمهم كبير وممكن تتعمل regenerate). لو حد عايز يشغّله من الأول يجيب retailrocket_events.csv ويحطه في data/ ويشغّل الخطوات فوق بالترتيب.



- متدرب على RetailRocket عشان نثبت إنه شغال، هيحتاج retraining على events table بتاعتنا لما يبقى فيه traffic حقيقي - الـ pipeline جاهز لده أصلاً
- seed_data.py و test_model.py من مرحلة dummy data القديمة، ممكن نشيلهم بعدين

— Elgawishhhhhh