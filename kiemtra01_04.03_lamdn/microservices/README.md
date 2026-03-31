# Django Microservices + API Gateway

Kien truc moi:
- staff_service -> MySQL (staff_db)
- customer_service -> MySQL (customer_db)
- laptop_service -> PostgreSQL (laptop_db)
- moblie_service -> PostgreSQL (moblie_db)
- api_gateway -> Nginx reverse proxy

## Chay
```bash
cd microservices
docker compose up --build
```

Gateway: `http://localhost:8000`

## Routes qua gateway
- `/api/staff/*`
- `/api/customer/*`
- `/api/laptop/*`
- `/api/moblie/*`
