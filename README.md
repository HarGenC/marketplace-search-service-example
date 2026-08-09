# Search Service

Read-side CQRS для маркетплейса. Слушает Kafka-топик `ads`, дёргает `GET /internal/ads/{id}` у Ad Service и поддерживает денормализованный индекс в PostgreSQL для полнотекстового поиска и автодополнения.

## Стек

- Python 3.13, FastAPI, SQLAlchemy (async), PostgreSQL
- PostgreSQL full-text search (`to_tsvector('russian', ...)` + GIN-индекс)
- Kafka (Redpanda локально) — aiokafka consumer
- httpx — клиент к Ad Service
- Alembic — миграции
- uv — управление зависимостями

## Быстрый старт

```bash
uv sync

# Локальная конфигурация: хосты сервисов и порты
cp .env.example .env

# PostgreSQL
docker compose up -d

# Миграции
make migrate

# API
make run

# В соседнем терминале — консьюмер, который слушает Kafka
make consumer
```

API стартует на `http://localhost:8003`.

## Переменные окружения

| Переменная                | По умолчанию      | Описание                                          |
|---------------------------|-------------------|---------------------------------------------------|
| `POSTGRES_HOST`           | `search-postgres` | Хост PostgreSQL                                   |
| `POSTGRES_PORT`           | `5432`            | Порт PostgreSQL                                   |
| `POSTGRES_DATABASE_NAME`  | `search_db`       | Имя базы                                          |
| `POSTGRES_USERNAME`       | `postgres`        | Пользователь                                      |
| `POSTGRES_PASSWORD`       | `postgres`        | Пароль                                            |
| `DATABASE_URL`            | —                 | Готовая строка подключения; перекрывает `POSTGRES_*` |
| `KAFKA_BOOTSTRAP_SERVERS` | `redpanda:29092`  | Kafka-брокеры                                     |
| `KAFKA_TOPIC_ADS`         | `ads`             | Топик с событиями объявлений                      |
| `KAFKA_CONSUMER_GROUP`    | `search-service`  | consumer group                                    |
| `AD_SERVICE_URL`          | `http://ads-service:8000` | Базовый URL Ad Service (internal)         |
| `API_HOST`                | `0.0.0.0`         | Адрес, на котором слушает API                     |
| `API_PORT`                | `8000`            | Порт API                                          |

Значения по умолчанию рассчитаны на запуск в docker-сети `marketplace`. Для локального
запуска скопируйте `.env.example` в `.env` — см. «Быстрый старт» выше.

## API

### Публичные эндпоинты (`/search`)

| Метод | Путь              | Описание                              | Auth |
|-------|-------------------|---------------------------------------|------|
| `GET` | `/search`         | Полнотекстовый поиск по объявлениям   | Нет  |
| `GET` | `/search/suggest` | Автодополнение по первым символам     | Нет  |

## Kafka consumer

Топик `ads`, consumer group `search-service`. События тонкие, поэтому Search Service источником истины о контенте объявления не является — по `ad_id` он всегда идёт за актуальной копией в Ad Service.

| Событие      | Действие                                                                                    |
|--------------|---------------------------------------------------------------------------------------------|
| `ad.created` | `GET /internal/ads/{ad_id}` → upsert в `search_index`                                       |
| `ad.updated` | `GET /internal/ads/{ad_id}` → upsert (или удаление, если объявление archived)               |
| `ad.deleted` | Удаление записи из `search_index` по `ad_id`                                                |

Если событие потеряно или пришло не по порядку — вызов `/internal/ads/{id}` всегда отдаёт финальное состояние (включая `archived`), поэтому индекс сойдётся к правильному состоянию на следующем событии.

## Make-команды

| Команда                          | Описание                          |
|----------------------------------|-----------------------------------|
| `make run`                       | Запуск API                        |
| `make consumer`                  | Kafka-консьюмер                   |
| `make check`                     | Линтинг + форматирование (ruff)   |
| `make test`                      | Запуск тестов                     |
| `make migrate`                   | Применить миграции                |
| `make migrate-create name="..."` | Сгенерировать миграцию            |
