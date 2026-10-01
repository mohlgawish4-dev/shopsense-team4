# ShopSense Backend

Flask REST API backend for ShopSense. Bridges the Frontend, PostgreSQL, and the AI layer
(Recommendation System, Smart Search, Cart Abandonment Prediction).

```
Frontend -> REST API -> Flask Backend -> PostgreSQL -> AI services -> Backend/Frontend
```

## 1. Tech Stack

Python, Flask, PostgreSQL, Flask-SQLAlchemy, Flask-Migrate, Flask-JWT-Extended, Marshmallow, Docker.

## 2. Project Structure

```
backend/
├── app/
│   ├── __init__.py          # app factory, extension init, error handlers
│   ├── config.py            # env-driven configuration
│   ├── extensions.py        # db, migrate, jwt, cors instances
│   ├── api/routes/          # HTTP layer (auth, products, cart, checkout, events)
│   ├── models/               # SQLAlchemy models (User, Product, Cart, Order, Event)
│   ├── services/              # business logic
│   ├── schemas/                # marshmallow request validation
│   └── utils/helpers.py        # response envelopes, ApiError
├── migrations/                 # flask-migrate output (generated)
├── tests/test_api.py           # pytest smoke tests (sqlite in-memory)
├── seed/seed_data.py           # demo data generator for the AI team
├── requirements.txt
├── Dockerfile
├── .env.example
└── run.py
```

## 3. Local Setup

### a) Create and activate a virtualenv, install deps

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### b) Configure environment

```bash
cp .env.example .env
# edit .env: set DATABASE_URL, JWT_SECRET_KEY, SECRET_KEY
```

### c) Start PostgreSQL

Easiest with Docker:

```bash
docker run --name shopsense-postgres \
  -e POSTGRES_USER=shopsense_user \
  -e POSTGRES_PASSWORD=shopsense_pass \
  -e POSTGRES_DB=shopsense \
  -p 5432:5432 -d postgres:16
```

Make sure `DATABASE_URL` in `.env` matches those credentials.

### d) Initialize the database schema

Either via Flask-Migrate (recommended, tracks schema changes):

```bash
flask db init      # first time only
flask db migrate -m "initial schema"
flask db upgrade
```

Or quickly create tables without migration history (fine for local dev):

```bash
python -c "from app import create_app; from app.extensions import db; app = create_app(); app.app_context().push(); db.create_all()"
```

### e) Seed demo data (recommended — the AI team needs this early)

```bash
python seed/seed_data.py
```

This drops/recreates all tables and inserts ~50 products, 15 users, orders, and a realistic
event history (`view_product`, `click`, `search`, `add_to_cart`, `purchase`) so the AI members
can start querying Postgres via Pandas/DuckDB immediately.

### f) Run the server

```bash
python run.py
# or
flask --app run run --debug
```

The API is now available at `http://localhost:5000/api`. Health check: `GET /health`.

## 4. Running Tests

```bash
pytest tests/ -v
```

Tests run against an in-memory SQLite database, so no Postgres connection is required.

## 5. Docker

```bash
docker build -t shopsense-backend .
docker run -p 5000:5000 --env-file .env shopsense-backend
```

When wiring this into the project's overall `docker-compose.yml`, point `DATABASE_URL` at the
Postgres service name (e.g. `postgresql://shopsense_user:shopsense_pass@postgres:5432/shopsense`).

## 6. API Reference

All responses use the envelope:

```json
{ "success": true, "message": "...", "data": {} }
{ "success": false, "message": "...", "errors": {} }
```

### Auth
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | /api/auth/register | - | Register (email, password, full_name?) |
| POST | /api/auth/login | - | Login, returns JWT access_token |
| GET | /api/auth/me | JWT | Current authenticated user |

### Products
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | /api/products | - | List products (`?page&per_page&category&search`) |
| GET | /api/products/<id> | - | Get one product |
| POST | /api/products | JWT | Create product |
| PUT | /api/products/<id> | JWT | Update product |
| DELETE | /api/products/<id> | JWT | Delete product |

### Cart
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | /api/cart | JWT | View current user's cart |
| POST | /api/cart | JWT | Add item `{product_id, quantity}` |
| PATCH | /api/cart/<item_id> | JWT | Update quantity `{quantity}` |
| DELETE | /api/cart/<item_id> | JWT | Remove one item |
| DELETE | /api/cart | JWT | Clear cart |

### Checkout / Orders
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | /api/checkout | JWT | Validate cart, create order, clear cart, log purchase events |
| GET | /api/orders | JWT | List current user's orders |
| GET | /api/orders/<id> | JWT | Get one order |

### Events
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | /api/events | optional JWT | Log an interaction: `{session_id, event_type, product_id?, metadata?}` |
| GET | /api/events | JWT | Browse recent events (sanity-check only; AI team queries Postgres directly for real analysis) |

Valid `event_type` values: `click`, `add_to_cart`, `purchase`, `view_product`, `search`.
`user_id` and `timestamp` are always set server-side — never trust client input for these.

## 7. Notes for the AI Team

- Connect to the same PostgreSQL instance and pull data with Pandas/DuckDB — no separate
  pipeline is provided by design (see project docs: no dedicated Data Engineer yet).
- `events` table columns: `id, user_id, session_id, event_type, product_id, event_metadata (JSON), timestamp`.
- `orders` + `order_items` give ground-truth purchases; `events` with `event_type='add_to_cart'`
  that never lead to a matching `purchase` event in the same session are useful abandoned-cart
  signals.
- Run `python seed/seed_data.py` any time you need a fresh, realistic dataset.
