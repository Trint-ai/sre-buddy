import os
from pymilvus import MilvusClient, DataType, FieldSchema, CollectionSchema


class milvus:
    def __init__(self):
        self.milvus_client = MilvusClient(uri=os.getenv('MILVUS_URI'))
        self.collection_datadog_alerts = "datadog_alerts"

    def create_collections(self):
        # Check if the collections already exists and exit it if it does.
        # Otherwise, create the collections with the specified schema.

        # Datadog Alerts
        if self.milvus_client.has_collection(self.collection_datadog_alerts):
            print(f"Collection {self.collection_datadog_alerts} already exists.")
            return

        field1 = FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True)
        field2 = FieldSchema(name="dense", dtype=DataType.FLOAT_VECTOR, dim=1536) # 1536 is the dimension of the vectors from the embeddings model
        field3 = FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535, enable_analyzer=True)

        # Metadata fields
        field4 = FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=65535)
        field5 = FieldSchema(name="alert_triggered_on", dtype=DataType.INT64)
        field6 = FieldSchema(name="device_name", dtype=DataType.VARCHAR, max_length=65535)
        field7 = FieldSchema(name="host", dtype=DataType.VARCHAR, max_length=65535)
        field8 = FieldSchema(name="priority", dtype=DataType.VARCHAR, max_length=65535)
        field9 = FieldSchema(name="resource", dtype=DataType.VARCHAR, max_length=65535)
        field10 = FieldSchema(name="tags", dtype=DataType.VARCHAR, max_length=65535)

        schema = CollectionSchema(fields=[field1, field2, field3, field4, field5, field6, field7, field8, field9, field10])


        index_params = self.milvus_client.prepare_index_params()

        index_params.add_index(
            field_name="dense",
            index_name="dense_index",
            index_type="IVF_FLAT",
            metric_type="IP"
        )

        self.milvus_client.create_collection(
            collection_name=self.collection_datadog_alerts,
            schema=schema,
            index_params=index_params
        )

    def insert(self, data, collection_name):
        self.milvus_client.insert(collection_name=collection_name, data=data)

    def search(self, question, limit, collection_name):
        search_params = {
            'params': {'drop_ratio_search': 0.2},
        }

        return self.milvus_client.search(
            collection_name=collection_name,
            anns_field="dense",
            data=[question],
            limit=limit,
            search_params=search_params,
            output_fields=["title"]
        )

    def query(self, limit, expr, collection_name):
        return (
            self.milvus_client.query(
                collection_name=collection_name,
                filter=expr,
                limit=limit,
                output_fields=["text"]
            ))
