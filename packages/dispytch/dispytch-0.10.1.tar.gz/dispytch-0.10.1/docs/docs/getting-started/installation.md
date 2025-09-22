# 📦 Installation

Dispytch is backend-agnostic by default. This means it won't install Kafka or RabbitMQ dependencies unless explicitly
requested.

Install with [`uv`](https://github.com/astral-sh/uv), [`poetry`](https://github.com/python-poetry/poetry) or `pip`, including extras for your preferred message broker:

## With Kafka support

```bash
uv add dispytch[kafka]
# or
poetry add dispytch[kafka]
# or
pip install dispytch[kafka]
```

Includes: `aiokafka`

---

## With RabbitMQ support

```bash
uv add dispytch[rabbitmq]
# or
poetry add dispytch[rabbitmq]
# or
pip install dispytch[rabbitmq]
```

Includes: `aio-pika`

---

## With Redis support

```bash
uv add dispytch[redis]
# or
poetry add dispytch[redis]
# or
pip install dispytch[redis]
```

Includes: `redis`

---

## ⚠️ No Backend by Default

If you install Dispytch without any extras:

```bash
uv add dispytch
# or
poetry add dispytch
# or
pip install dispytch
```

then no producer or consumer backends will be available. You'll need to install at least one extra
or install the dependencies separately to use built-in event producers and consumers.

---

## 🔧 Custom Backends

If you're building your own backend implementation (e.g., for Redis, NATS, SQS, etc.), installing Dispytch
without extras is exactly what you want.