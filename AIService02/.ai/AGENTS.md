# 🎓 AGENTS.md — E-Commerce Microservices Agent Instructions

# Compatible with: Codex, Claude Code, Copilot Agent, Cursor, Windsurf, etc.

## Identity

You are a Senior Software Engineering Assistant working on a complex E-commerce Microservices system.
You help developers design, build, debug, document, and deploy a production-ready system that supports:

- Full E-commerce user flow (Registration, Login, Cart, Checkout, Payment, Shipping).
- Distributed product management (Books, Clothes, Electronics).
- Advanced AI integrations (Deep Learning recommendations, Knowledge Graph, RAG Chatbot).

---

## Project Architecture

The system is strictly divided into microservices. Frontend traffic MUST go through the `api-gateway`.

infrastructure/
api-gateway/ → Central entry point & reverse proxy (Kong/Nginx/Spring Cloud Gateway)
data/ → Database initialization scripts & volumes

core-services/
customer-service/ → Public user management, Auth (Login/Register)
manager-service/ → Admin/Manager user management & RBAC
staff-service/ → Employee/Staff management

product-services/
catalogue-service/ → Central product catalog & search aggregation
book-service/ → Specific logic/schema for Books
clothe-service/ → Specific logic/schema for Clothes
electronic-service/ → Specific logic/schema for Electronics

transaction-services/
cart-service/ → User shopping cart (Redis recommended)
order-service/ → Order placement & state machine
pay-service/ → Payment processing (Mock external gateways)
ship-service/ → Logistics and tracking

engagement-services/
review-service/ → Product ratings and reviews
recommender-ai-service/ → AI integrations (DL Models, Neo4j Graph, LLM RAG)

docs/ → API specs, architecture diagrams
tools/ → Utility scripts

---

## Core Constraints

1. **Docker-first (MANDATORY)**
   - All services must be containerized.
   - The entire system must spin up using: `docker-compose up --build` or via provided powershell scripts (`compile_code.ps1`).

2. **Database per Service Pattern**
   - No shared databases.
   - `customer-service` has its own DB, `order-service` has its own DB, etc.
   - `recommender-ai-service` specifically uses Neo4j for its Knowledge Base Graph.

3. **API Gateway Routing Only**
   - Frontend/Clients NEVER call microservices directly.
   - All external requests route through `api-gateway`.

4. **Authentication & Authorization**
   - Decentralized, stateless Auth using JWT.
   - `customer-service` handles public Sign Up / Log In.
   - Gateway or individual services validate JWT signatures.
   - Strict RBAC: Customers can buy; Staff can update stock; Managers have full CRUD.

5. **Inter-service Communication**
   - Synchronous: REST/gRPC for immediate reads (e.g., Order checking Catalogue).
   - Asynchronous: Message Broker (Kafka/RabbitMQ) for events (e.g., Order Created -> triggers Ship & Pay).

6. **Health Checks**
   - Every service MUST expose `GET /health` returning `{"status": "UP"}`.

---

## Core System Logic

### 1. User & Auth Flow

- Registration: Hash passwords (Bcrypt).
- Login: Issue JWT containing `user_id` and `role`.
- Profile: Users can update their own info.

### 2. Shopping Flow

- **Cart**: Add/Remove items. Should be fast (cache-based).
- **Order**: Creates a pending order -> reserves stock -> waits for payment.
- **Pay**: Processes transaction -> emits `PaymentSuccess` event.
- **Ship**: Listens to `PaymentSuccess` -> updates shipping status.

### 3. AI & Recommender System (recommender-ai-service)

- Integrates the `data_user500.csv` dataset.
- Hosts Deep Learning models (RNN, LSTM, biLSTM) to predict user actions.
- Maintains a Neo4j Knowledge Base Graph connecting Users, Products, Categories.
- Exposes a RAG-based Chat endpoint for user queries based on the Graph.

---

## Coding Standards

- **Validation**: Use strict schema validation (e.g., Pydantic for Python, DTOs with Validation API for Java/TS).
- **Error Handling**: Standardized error response format across all services:
  ```json
  {
    "timestamp": "2026-04-21T10:00:00Z",
    "status": 400,
    "error": "Bad Request",
    "message": "Invalid product ID format",
    "path": "/api/v1/orders"
  }
  ```
