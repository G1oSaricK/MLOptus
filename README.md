# MLOps. Feature Store

## Описание

Работа с **Feast Feature Store** для управления признаками моделей машинного обучения.

### Архитектура

```
notebooks/
  read_feature_view.ipynb    - ноутбук с примерами запросов
feature_store/
  feature_repo/
    feature_store.py         - определение Entity, FeatureView, OnDemandView
    feature_store.yaml       - конфигурация Feast
    data/
      driver_stats.parquet   - сырые данные
      registry.db            - реестр признаков
```

### Компоненты

| Компонент | Описание | Статус |
|---|---|---|
| Entity (`driver`) | Первичный ключ - `driver_id` | ✅ |
| FeatureView `driver_efficiency` | `conv_rate`, `acc_rate` | ✅ |
| FeatureView `driver_activity` | `avg_daily_trips` | ✅ |
| On-DemandView `driver_performance_metrics` | `efficiency_gap`, `performance_score`, `is_high_performer` | ✅ |
| FeatureService `driver_activity_v1` | Собранный набор фичей для модели | ✅ |
| Historical features | Извлечение данных для обучения | ✅ |
| Online features | Извлечение данных для инференса | ✅ |

## Быстрый старт

```bash
# Установка зависимостей
pip install feast pandas pyarrow

# Регистрация признаков
make apply

# Материализация в online store
feast materialize 2024-01-01T00:00:00 2024-12-31T23:59:59

# Запуск ноутбука
jupyter notebook notebooks/read_feature_view.ipynb
```

## Makefile

| Команда | Описание |
|---|---|
| `make apply` | Регистрация признаков в Feast |
| `make ui` | Запуск Feast UI |
