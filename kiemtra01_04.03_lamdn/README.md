# Django Microservices + API Gateway

Da chuyen sang kien truc microservice hoan chinh trong thu muc `microservices/`.

## Services

- `staff_service` (Django) -> MySQL `staff_db`
- `customer_service` (Django) -> MySQL `customer_db`
- `laptop_service` (Django) -> PostgreSQL `laptop_db`
- `moblie_service` (Django) -> PostgreSQL `moblie_db`
- `gateway_service` (Django API Gateway) -> chua URL tong hop va proxy sang cac service

## Run

```bash
cd microservices
docker compose up --build
```

Gateway URL: `http://localhost:8000`

## Gateway Routes

- `/api/staff/*` -> `staff_service`
- `/api/customer/*` -> `customer_service`
- `/api/laptop/*` -> `laptop_service`
- `/api/moblie/*` -> `moblie_service`
- `/health/` -> health check cua gateway

## Database Connections

- `staff_service`: `mysql_staff:3306` / `staff_db`
- `customer_service`: `mysql_customer:3306` / `customer_db`
- `laptop_service`: `postgres_laptop:5432` / `laptop_db`
- `moblie_service`: `postgres_moblie:5432` / `moblie_db`

## Main APIs

- Staff: `POST /api/staff/register/`, `POST /api/staff/login/`
- Customer: register/login/search/cart CRUD/checkout qua `/api/customer/*`
- Laptop: `GET /api/laptop/products/`, `POST /api/laptop/products/create/`
- Moblie: `GET /api/moblie/products/`, `POST /api/moblie/products/create/`
