# Это пример файла с определением признаков (feature definition)

import os

from datetime import timedelta

import numpy as np
import pandas as pd

from feast import (
    Entity,
    FeatureService,
    FeatureView,
    Field,
    FileSource,
    RequestSource,
    ValueType,
)

from feast.feature_logging import LoggingConfig
from feast.infra.offline_stores.file_source import FileLoggingDestination
from feast.on_demand_feature_view import on_demand_feature_view
from feast.types import Float32, Float64, Int32, Int64

REPO_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(REPO_PATH, "data")

# Определяем сущность для водителя. Сущность можно рассматривать как первичный ключ,
# который используется для получения признаков
driver = Entity(name="driver", join_keys=["driver_id"], value_type=ValueType.INT64,)

# Читаем данные из parquet файлов.
driver_stats_source = FileSource(
    name="driver_hourly_stats_source",
    path=os.path.join(DATA_PATH, "driver_stats.parquet"),
    timestamp_field="event_timestamp",
    # created_timestamp_column="created",
)

#Feature View 1: ЭФфективность водителя

driver_efficiency_fv = FeatureView(
    name="driver_efficiency",
    entities=[driver],
    ttl=timedelta(days=3650),
    schema=[
        Field(name="conv_rate", dtype=Float32),
        Field(name="acc_rate", dtype=Float32),
    ],
    source=driver_stats_source,
    online=True,
)

#Feature View 2: Активность водителя

driver_activity_fv = FeatureView(
    name="driver_activity",
    entities=[driver],
    ttl=timedelta(days=3650),
    schema=[
        Field(name="avg_daily_trips", dtype=Int64),
    ],
    source=driver_stats_source,
    online=True,
)

#On-Demand Feature View: Комбинированные метрики

input_request = RequestSource(
    name="driver_request",
    schema=[
        Field(name="target_conv_rate", dtype=Float64),
    ]
)

@on_demand_feature_view(
    sources=[driver_efficiency_fv, driver_activity_fv, input_request],
    schema=[
        Field(name="efficiency_gap", dtype=Float64),
        Field(name="is_high_performer", dtype=Int64),
        Field(name="performance_score", dtype=Float64),
    ]
)
def driver_performance_metrics(inputs: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame()
    
    # 1. Разрыв между текущей и целевой конверсией
    df["efficiency_gap"] = inputs["target_conv_rate"] - inputs["conv_rate"]
    
    # 2. Является ли водитель высокоэффективным (conv_rate > 0.7 и avg_daily_trips > 20)
    df["is_high_performer"] = (
        (inputs["conv_rate"] > 0.7) & 
        (inputs["avg_daily_trips"] > 20)
    ).astype(int)
    
    # 3. Общий показатель производительности (взвешенная сумма)
    df["performance_score"] = (
        inputs["conv_rate"] * 0.4 + 
        inputs["acc_rate"] * 0.3 + 
        (inputs["avg_daily_trips"] / 100) * 0.3
    )
    
    return df

#Feature Service для модели
driver_activity_v1 = FeatureService(
    name="driver_activity_v1",
    features=[
        driver_efficiency_fv,
        driver_activity_fv,
        driver_performance_metrics,
    ]
)
