## Kiến trúc tổng thể (Overall)

```mermaid
flowchart LR
  user[UserBrowser] --> apiGateway[api-gateway]

  apiGateway --> bookService[book-service]
  apiGateway --> customerService[customer-service]
  apiGateway --> cartService[cart-service]
  apiGateway --> orderService[order-service]
  apiGateway --> reviewService[review-service]
  apiGateway --> payService[pay-service]
  apiGateway --> shipService[ship-service]
  apiGateway --> catalogueService[catalogue-service]
  apiGateway --> staffService[staff-service]
  apiGateway --> managerService[manager-service]
  apiGateway --> recommenderService[recommender-ai-service]

  customerService -->|"Auto create cart"| cartService
  catalogueService --> bookService
  catalogueService --> reviewService
```

## api-gateway

```mermaid
flowchart LR
  browser[Browser] --> gateway[api-gateway]
  gateway -->|"books/publishers"| bookService[book-service]
  gateway -->|"customers"| customerService[customer-service]
  gateway -->|"carts"| cartService[cart-service]
  gateway -->|"orders"| orderService[order-service]
  gateway -->|"reviews"| reviewService[review-service]
  gateway -->|"payments"| payService[pay-service]
  gateway -->|"shipments"| shipService[ship-service]
  gateway -->|"catalog"| catalogueService[catalogue-service]
  gateway -->|"recommendations"| recommenderService[recommender-ai-service]

  gatewayDb[(SQLite gateway volume)]
  gateway --> gatewayDb
```

## book-service

```mermaid
flowchart LR
  gateway[api-gateway] --> book[book-service]
  catalogue[catalogue-service] --> book

  bookDb[(SQLite book volume)]
  book --> bookDb
```

## customer-service

```mermaid
flowchart LR
  gateway[api-gateway] --> customer[customer-service]
  customerDb[(SQLite customer volume)]
  customer --> customerDb
  customer -->|"POST /carts/"| cart[cart-service]
```

## cart-service

```mermaid
flowchart LR
  gateway[api-gateway] --> cart[cart-service]
  customer[customer-service] --> cart
  cartDb[(SQLite cart volume)]
  cart --> cartDb
```

## order-service

```mermaid
flowchart LR
  gateway[api-gateway] --> order[order-service]
  orderDb[(SQLite order volume)]
  order --> orderDb
```

## pay-service

```mermaid
flowchart LR
  gateway[api-gateway] --> pay[pay-service]
  payDb[(SQLite pay volume)]
  pay --> payDb
```

## ship-service

```mermaid
flowchart LR
  gateway[api-gateway] --> ship[ship-service]
  shipDb[(SQLite ship volume)]
  ship --> shipDb
```

## review-service

```mermaid
flowchart LR
  gateway[api-gateway] --> review[review-service]
  catalogue[catalogue-service] --> review
  reviewDb[(SQLite review volume)]
  review --> reviewDb
```

## catalogue-service

```mermaid
flowchart LR
  gateway[api-gateway] --> catalogue[catalogue-service]
  catalogue -->|"GET /books/"| book[book-service]
  catalogue -->|"GET /reviews/stats/{book_id}/"| review[review-service]
```

## staff-service

```mermaid
flowchart LR
  admin[Admin via api-gateway] --> staff[staff-service]
  staffDb[(SQLite staff volume)]
  staff --> staffDb
```

## manager-service

```mermaid
flowchart LR
  admin[Admin via api-gateway] --> manager[manager-service]
  managerDb[(SQLite manager volume)]
  manager --> managerDb
```

## recommender-ai-service

```mermaid
flowchart LR
  gateway[api-gateway] --> recommender[recommender-ai-service]
  recommender -->|"Gemini API"| gemini[Gemini]
  recommenderDb[(SQLite recommender volume)]
  recommender --> recommenderDb
```

