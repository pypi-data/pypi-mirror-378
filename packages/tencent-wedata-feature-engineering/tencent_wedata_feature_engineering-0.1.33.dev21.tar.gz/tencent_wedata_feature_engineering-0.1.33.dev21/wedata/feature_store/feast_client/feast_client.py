# -*- coding: utf-8 -*-

__doc__ = """
Feast客户端，用于与Feast服务器交互
"""

import logging
import json
import os
from typing import Union, List, Dict, Optional
from feast import FeatureStore, RepoConfig, FeatureView
from pyspark.sql import DataFrame, SparkSession
from wedata.feature_store.common.store_config.redis import RedisStoreConfig
from feast import Entity, Field, FileSource
from feast.data_source import RequestSource
from pyspark.sql.functions import current_timestamp
from feast.types import ValueType
from pyspark.sql.types import (
    StringType, IntegerType, LongType, FloatType, DoubleType,
    BooleanType, BinaryType, TimestampType, DateType, DecimalType,
    ArrayType, MapType, StructType, NullType, StructField
)

TEMP_FILE_PATH = "/tmp/feast_data/"


class FeastClient:

    def __init__(self, offline_store: SparkSession, online_store_config: RedisStoreConfig = None):
        project_id = os.getenv("WEDATA_PROJECT_ID", "")
        remote_path = os.getenv("FEAST_REMOTE_ADDRESS", "")
        if offline_store is None or not isinstance(offline_store, SparkSession):
            raise ValueError("offline_store must be provided SparkSession instance")

        # 应用Spark配置
        spark_conf_dict = dict()
        spark_conf = offline_store.sparkContext.getConf().getAll()
        for item in spark_conf:
            print(f"type:{type(item)} value:{item}")
            spark_conf_dict[item[0]] = item[1]

        print("spark_conf:\n", spark_conf_dict)
        config = RepoConfig(
            project=project_id,
            registry={"registry_type": "remote", "path": remote_path},
            provider="local",
            online_store={"type": "redis",
                          "connection_string": online_store_config.connection_string} if online_store_config else None,
            offline_store={"type": "spark", "spark_conf": spark_conf_dict},
            batch_engine={"type": "spark.engine"}
        )

        self._client = FeatureStore(config=config)
        self._spark = offline_store

    @property
    def client(self):
        return self._client

    def create_table(self,
                     table_name: str,
                     primary_keys: List[str],
                     timestamp_keys: Union[str, List[str]],
                     df: Optional[DataFrame] = None,
                     schema: Optional[StructType] = None,
                     tags: Optional[Dict[str, str]] = None):
        if schema is not None and df is None:
            # 创建空的Spark DataFrame
            df = self._spark.createDataFrame([], schema)
        feature_view = _create_table_to_feature_view(
            table_name=table_name,
            primary_keys=primary_keys,
            timestamp_keys=timestamp_keys,
            df=df,
            tags=tags
        )
        self._client.apply(feature_view)

    def remove_offline_table(self, table_name: str):
        self._client.delete_feature_view(table_name)

    def write_table(self, table_name: str, df: DataFrame):
        try:
            logging.info(f"Starting to write table {table_name}")

            # 确保临时目录存在
            os.makedirs(TEMP_FILE_PATH, exist_ok=True)

            # 获取Spark DataFrame的schema信息
            schema = df.schema

            # 通过schema识别时间戳列
            timestamp_cols = [field.name for field in schema.fields
                              if isinstance(field.dataType, (TimestampType, DateType))]

            if not timestamp_cols:
                raise ValueError("No timestamp columns found in DataFrame schema")

            event_timestamp = timestamp_cols[0]  # 默认使用第一个时间戳列作为event_timestamp
            created_timestamp = timestamp_cols[-1] if len(timestamp_cols) > 1 else None

            logging.info(f"Detected timestamp columns from schema: {timestamp_cols}")
            logging.info(f"Using event_timestamp: {event_timestamp}")
            if created_timestamp:
                logging.info(f"Using created_timestamp: {created_timestamp}")

            # 转换为Pandas DataFrame
            logging.info("Converting Spark DataFrame to Pandas")
            pd_df = df.toPandas()

            # 写入Parquet文件
            file_path = os.path.join(TEMP_FILE_PATH, f"{table_name}.parquet")
            logging.info(f"Writing to parquet file at {file_path}")
            pd_df.to_parquet(file_path, engine='pyarrow')

            # 创建FileSource
            file_source = FileSource(
                name=table_name,
                path=file_path,
                event_timestamp_column=event_timestamp,
                created_timestamp_column=created_timestamp,
                date_partition_column="date"  # 可选
            )

            # 获取现有的FeatureView
            logging.info(f"Getting feature view {table_name}")
            feature_view = self._client.get_feature_view(table_name)

            # 更新FeatureView的source
            logging.info("Updating feature view source")
            feature_view.source = file_source

            # 应用更新
            logging.info("Applying changes to Feast")
            self._client.apply([feature_view])

            logging.info("Successfully updated feature view")
        except Exception as e:
            logging.error(f"Failed to write table {table_name}: {str(e)}")
            raise

    def alter_table(self, full_table_name: str, timestamp_key: str, primary_keys: List[str]):
        """
        将已注册的Delta表同步到Feast中作为离线特征数据
        
        Args:
            full_table_name: 表名（格式：<table>）
            timestamp_key: 时间戳列名
            primary_keys: 主键列名列表
        Raises:
            ValueError: 当表不存在或参数无效时抛出
            RuntimeError: 当同步操作失败时抛出
        """
        import logging
        try:

            # 构建完整表名

            logging.info(f"Starting to sync Delta table {full_table_name} to Feast")

            # 1. 读取Delta表数据和schema
            df = self._spark.table(full_table_name)

            # 2. 从表属性中获取主键和时间戳列
            tbl_props = self._spark.sql(f"SHOW TBLPROPERTIES {full_table_name}").collect()
            props = {row['key']: row['value'] for row in tbl_props}

            if not primary_keys:
                raise ValueError("Primary keys not found in table properties")
            if not timestamp_key:
                raise ValueError("Timestamp keys not found in table properties")

            logging.info(f"Primary keys: {primary_keys}")
            logging.info(f"Timestamp keys: {timestamp_key}")

            # 3. 创建或更新FeatureView
            feature_view = _create_table_to_feature_view(
                table_name=full_table_name,
                primary_keys=primary_keys,
                timestamp_keys=timestamp_key,
                df=df,
                tags={"source": "delta_table", **json.loads(props.get("tags", "{}"))}
            )

            # 4. 应用到Feast
            self._client.apply(feature_view)
            logging.info(f"Successfully synced Delta table {full_table_name} to Feast")

        except Exception as e:
            logging.error(f"Failed to sync Delta table to Feast: {str(e)}")
            raise RuntimeError(f"Failed to sync Delta table {full_table_name} to Feast: {str(e)}") from e

    def modify_tags(
            self,
            table_name: str,
            tags: Dict[str, str]
    ) -> None:
        """修改特征表的标签信息

        Args:
            table_name: 特征表名称(格式: <database>.<table>)
            tags: 要更新的标签字典

        Raises:
            ValueError: 当参数无效时抛出
            RuntimeError: 当修改操作失败时抛出
        """
        if not table_name:
            raise ValueError("table_name cannot be empty")
        if not tags:
            raise ValueError("tags cannot be empty")

        try:
            # 获取现有的FeatureView
            feature_view = self._client.get_feature_view(table_name)
            if not feature_view:
                raise ValueError(f"FeatureView '{table_name}' not found")

            # 更新标签
            current_tags = feature_view.tags or {}
            current_tags.update(tags)
            feature_view.tags = current_tags

            # 应用更新
            self._client.apply([feature_view])
            print(f"Successfully updated tags for table '{table_name}'")

        except Exception as e:
            raise RuntimeError(f"Failed to modify tags for table '{table_name}': {str(e)}") from e


def _create_table_to_feature_view(
        table_name: str,
        primary_keys: List[str],
        timestamp_keys: Union[str, List[str]],
        df: Optional[DataFrame],
        tags: Optional[Dict[str, str]] = None
):
    """

    Returns:
        FeatureView实例
    """

    entities = list()
    for primary_key in primary_keys:
        entities.append(Entity(name=primary_key, value_type=ValueType.STRING))

    if primary_keys is None or len(primary_keys) == 0:
        raise ValueError("primary_keys must not be empty")
    if timestamp_keys is None or len(timestamp_keys) == 0:
        raise ValueError("timestamp_keys must not be empty")

    # 处理timestamp_keys
    missing_timestamps = []
    if isinstance(timestamp_keys, str):
        if timestamp_keys not in df.columns:
            df = df.withColumn(timestamp_keys, current_timestamp())
            missing_timestamps.append(timestamp_keys)
    elif isinstance(timestamp_keys, list):
        for ts_key in timestamp_keys:
            if ts_key not in df.columns:
                df = df.withColumn(ts_key, current_timestamp())
                missing_timestamps.append(ts_key)

    if missing_timestamps:
        print(f"Added missing timestamp columns: {missing_timestamps}")

    os.makedirs(TEMP_FILE_PATH, exist_ok=True)
    df.toPandas().to_parquet(os.path.join(TEMP_FILE_PATH, f"{table_name}.parquet"), engine='pyarrow')

    print(f"Creating feature view for table: {table_name}  primary_keys: {primary_keys}  timestamp_keys: {timestamp_keys}")
    resources = FileSource(
        name=table_name,
        path=os.path.join(TEMP_FILE_PATH, f"{table_name}.parquet"),
        event_timestamp_column=timestamp_keys[0] if isinstance(timestamp_keys, list) else timestamp_keys,
        created_timestamp_column=timestamp_keys[-1] if isinstance(timestamp_keys, list) and len(
            timestamp_keys) > 1 else None,
        owner="",
    )

    # 构建FeatureView的剩余逻辑
    feature_view = FeatureView(
        name=table_name,
        entities=entities,
        tags=tags,
        source=resources,
    )

    return feature_view
