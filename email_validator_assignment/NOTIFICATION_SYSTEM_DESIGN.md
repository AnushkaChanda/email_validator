# Scalable Notification System Design (1 Million Notifications / Day)

## 1. Throughput Math
- Total: 1,000,000 / day
- Average: ~12 notifications/sec
- Peak (20x burst): ~240–250 notifications/sec

## 2. Core Architecture
- Ingestion API (FastAPI / Node.js)
- Message Broker: RabbitMQ or Apache Kafka partitioned topics (push, email, sms)
- Worker Pool: Asynchronous consumers handling vendor dispatch
- Retry Engine: Exponential backoff with Dead Letter Queue (DLQ)
- Deduplication: Redis cache with TTL matching an idempotency key
