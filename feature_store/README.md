# Feature Store Repository

## Структура

```
feature_repo/
├── feature_store.py       — определение признаков
├── feature_store.yaml     — конфигурация Feast
└── data/
    ├── driver_stats.parquet  — сырые данные
    ├── registry.db           — реестр признаков
    └── online_store.db       — online store (SQLite)
```

## Определения признаков

### Entity
- **driver** — `driver_id` (INT64)

### Feature Views
- **driver_efficiency** — `conv_rate` (FLOAT), `acc_rate` (FLOAT)
- **driver_activity** — `avg_daily_trips` (INT64)

### On-Demand Feature View
- **driver_performance_metrics** — вычисляемые на лету фичи:
  - `efficiency_gap` — разница между целевой и текущей конверсией
  - `performance_score` — взвешенная оценка производительности
  - `is_high_performer` — бинарный флаг высокоэффективного водителя

### Feature Service
- **driver_activity_v1** — объединённый набор всех фичей

## Запуск

```bash
# Регистрация признаков
feast apply

# Материализация
feast materialize 2024-01-01T00:00:00 2024-12-31T23:59:59
```
