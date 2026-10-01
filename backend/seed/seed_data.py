"""
Seed the database with realistic demo data so the AI team (Recommendation,
Smart Search, Cart Abandonment) can start querying PostgreSQL immediately,
without waiting for real user traffic.

Usage:
    python seed/seed_data.py
"""
import os
import random
import sys
from datetime import datetime, timedelta, timezone

# Make the project root importable when this script is run directly.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.product import Product
from app.models.cart import Cart
from app.models.order import Order, OrderItem, OrderStatus
from app.models.event import Event

random.seed(42)

CATEGORIES = ["Electronics", "Home & Kitchen", "Fashion", "Sports", "Books", "Beauty"]

PRODUCT_NAMES = {
    "Electronics": ["Wireless Earbuds", "4K Monitor", "Mechanical Keyboard", "Smartwatch", "Bluetooth Speaker", "USB-C Hub", "Webcam HD", "Gaming Mouse"],
    "Home & Kitchen": ["Air Fryer", "Coffee Maker", "Blender", "Non-stick Pan Set", "Vacuum Cleaner", "Electric Kettle", "Toaster", "Knife Set"],
    "Fashion": ["Running Shoes", "Denim Jacket", "Leather Wallet", "Sunglasses", "Backpack", "Wool Sweater", "Cotton T-Shirt", "Sneakers"],
    "Sports": ["Yoga Mat", "Dumbbell Set", "Resistance Bands", "Cycling Helmet", "Water Bottle", "Tennis Racket", "Jump Rope", "Foam Roller"],
    "Books": ["Data Engineering Basics", "Python Crash Course", "SQL for Beginners", "Clean Code", "System Design Interview", "The Pragmatic Programmer"],
    "Beauty": ["Facial Cleanser", "Moisturizer", "Sunscreen SPF50", "Shampoo", "Lip Balm", "Hair Dryer"],
}

FIRST_NAMES = ["Sara", "Omar", "Layla", "Ahmed", "Mona", "Youssef", "Nour", "Karim", "Hana", "Tarek"]
LAST_NAMES = ["Hassan", "Ali", "Ibrahim", "Mostafa", "Fathy", "Saeed", "Gaber", "Adel"]


def seed_products():
    products = []
    for category, names in PRODUCT_NAMES.items():
        for name in names:
            product = Product(
                name=name,
                description=f"High quality {name.lower()} in the {category} category.",
                category=category,
                price=round(random.uniform(5, 300), 2),
                stock=random.randint(10, 200),
                image_url=f"https://picsum.photos/seed/{name.replace(' ', '-')}/400/400",
            )
            products.append(product)
    db.session.add_all(products)
    db.session.commit()
    return products


def seed_users(count=15):
    users = []
    for i in range(count):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        email = f"{first.lower()}.{last.lower()}{i}@example.com"
        user = User(email=email, full_name=f"{first} {last}")
        user.set_password("Password123!")
        users.append(user)
    db.session.add_all(users)
    db.session.commit()

    # Give every seeded user an empty cart, same as the real registration flow.
    for user in users:
        db.session.add(Cart(user_id=user.id))
    db.session.commit()

    return users


def seed_orders_and_events(users, products):
    events = []
    now = datetime.now(timezone.utc)

    for user in users:
        session_id = f"session-{user.id}-{random.randint(1000, 9999)}"
        browsed_products = random.sample(products, k=random.randint(3, 8))

        # Browsing behaviour: view_product + click events over the last 14 days.
        for product in browsed_products:
            ts = now - timedelta(days=random.randint(0, 14), hours=random.randint(0, 23))
            events.append(Event(
                user_id=user.id, session_id=session_id, event_type="view_product",
                product_id=product.id, event_metadata={"source": "catalog"}, timestamp=ts,
            ))
            if random.random() < 0.6:
                events.append(Event(
                    user_id=user.id, session_id=session_id, event_type="click",
                    product_id=product.id, event_metadata={"source": "product_page"},
                    timestamp=ts + timedelta(minutes=1),
                ))

        # Search events.
        for _ in range(random.randint(0, 3)):
            ts = now - timedelta(days=random.randint(0, 14))
            events.append(Event(
                user_id=user.id, session_id=session_id, event_type="search",
                event_metadata={"query": random.choice(["shoes", "headphones", "kitchen", "laptop bag"])},
                timestamp=ts,
            ))

        # Some users complete a purchase (used for cart-abandonment signal too).
        if random.random() < 0.5:
            purchased = random.sample(browsed_products, k=min(len(browsed_products), random.randint(1, 3)))
            order_total = 0.0
            order = Order(user_id=user.id, status=OrderStatus.COMPLETED.value, total_amount=0)
            db.session.add(order)
            db.session.flush()

            for product in purchased:
                qty = random.randint(1, 3)
                order_total += float(product.price) * qty
                db.session.add(OrderItem(
                    order_id=order.id, product_id=product.id, product_name=product.name,
                    unit_price=product.price, quantity=qty,
                ))
                events.append(Event(
                    user_id=user.id, session_id=session_id, event_type="add_to_cart",
                    product_id=product.id, event_metadata={"quantity": qty}, timestamp=now - timedelta(days=random.randint(0, 5)),
                ))
                events.append(Event(
                    user_id=user.id, session_id=session_id, event_type="purchase",
                    product_id=product.id, event_metadata={"order_id": order.id, "quantity": qty},
                    timestamp=now - timedelta(days=random.randint(0, 5)),
                ))

            order.total_amount = round(order_total, 2)
        else:
            # Abandoned cart signal: added to cart but never purchased.
            abandoned = random.sample(browsed_products, k=min(len(browsed_products), random.randint(1, 2)))
            for product in abandoned:
                events.append(Event(
                    user_id=user.id, session_id=session_id, event_type="add_to_cart",
                    product_id=product.id, event_metadata={"quantity": random.randint(1, 2)},
                    timestamp=now - timedelta(days=random.randint(0, 3)),
                ))

    db.session.add_all(events)
    db.session.commit()


def main():
    app = create_app()
    with app.app_context():
        print("Dropping and recreating all tables...")
        db.drop_all()
        db.create_all()

        print("Seeding products...")
        products = seed_products()
        print(f"  Created {len(products)} products.")

        print("Seeding users...")
        users = seed_users()
        print(f"  Created {len(users)} users (password: 'Password123!').")

        print("Seeding orders and events...")
        seed_orders_and_events(users, products)
        print(f"  Created orders and events for {len(users)} users.")

        print("Seeding complete.")


if __name__ == "__main__":
    main()
