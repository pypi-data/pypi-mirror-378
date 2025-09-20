# accessnode/mongodb.py
from pymongo import MongoClient
from bson import ObjectId
from typing import Any, Dict, List, Union
from ..base import DatabaseHandler


class MongoDBHandler(DatabaseHandler):
    def __init__(self, **kwargs):
        # Setup the connection
        connection_string = f"mongodb://{kwargs.get('username', '')}:{kwargs.get('password', '')}@{kwargs.get('host', 'localhost')}:{kwargs.get('port', 27017)}/{kwargs.get("database", "")}"
        self.client = MongoClient(connection_string)
        self.db = self.client[{kwargs.get("database", "")}]

    def create_collection(self, collection_name: str) -> None:
        self.db.create_collection(collection_name)

    def insert(self, collection_name: str, data: Dict[str, Any]) -> str:
        collection = self.db[collection_name]
        result = collection.insert_one(data)
        return str(result.inserted_id)

    def get(self, collection_name: str, filter_data: Dict[str, Any]) -> Union[Dict[str, Any], None]:
        collection = self.db[collection_name]
        result = collection.find_one(filter_data)
        if result:
            result['_id'] = str(result['_id'])
        return result

    def get_all(self, collection_name: str, filter_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        collection = self.db[collection_name]
        if filter_data is None:
            filter_data = {}
        results = list(collection.find(filter_data))
        for result in results:
            result['_id'] = str(result['_id'])
        return results

    def update(self, collection_name: str, filter_data: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        collection = self.db[collection_name]
        result = collection.update_many(filter_data, {'$set': update_data})
        return result.modified_count

    def delete(self, collection_name: str, filter_data: Dict[str, Any]) -> int:
        collection = self.db[collection_name]
        result = collection.delete_many(filter_data)
        return result.deleted_count

    def raw_query(self, collection_name: str, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Validate the collection name
        if not isinstance(collection_name, str) or not collection_name.isidentifier():
            raise ValueError("Invalid collection name")

        # Validate pipeline stages
        allowed_stages = {'$match', '$group', '$sort', '$limit', '$project', '$unwind', '$lookup', '$addFields'}
        for stage in pipeline:
            if not isinstance(stage, dict) or not all(key in allowed_stages for key in stage.keys()):
                raise ValueError(f"Disallowed or invalid pipeline stage: {stage}")

        # Enforce a limit to the number of documents returned
        if not any('$limit' in stage for stage in pipeline):
            pipeline.append({'$limit': 1000})  # Default limit to avoid large results

        collection = self.db[collection_name]
        
        # Execute the pipeline and sanitize results
        try:
            results = list(collection.aggregate(pipeline))
        except Exception as e:
            raise RuntimeError(f"Error executing pipeline: {e}")

        for result in results:
            if '_id' in result:
                result['_id'] = str(result['_id'])  # Convert ObjectId to string for better readability

        return results

    async def get_table_schema(self, table_name: str = None) -> List[Dict[str, Any]]:
        """Get schema information for all collections or a specific collection."""
        if table_name:
            # Get schema info for a specific collection in MongoDB
            collection = self.db[table_name]
            # For MongoDB, we can sample some documents to infer schema
            sample_docs = list(collection.find().limit(10))
            if sample_docs:
                # Extract field names and types from sample documents
                fields = set()
                for doc in sample_docs:
                    fields.update(doc.keys())

                schema_info = []
                for field in fields:
                    # Simple type inference from first occurrence
                    sample_value = None
                    for doc in sample_docs:
                        if field in doc:
                            sample_value = doc[field]
                            break

                    field_type = type(sample_value).__name__ if sample_value is not None else 'Mixed'
                    schema_info.append({
                        'column_name': field,
                        'data_type': field_type,
                        'is_nullable': 'YES',  # MongoDB fields are typically nullable
                        'column_default': None,
                        'key_type': 'PRIMARY KEY' if field == '_id' else None
                    })
                return schema_info
            else:
                return []
        else:
            # Get all collections
            collections = self.db.list_collection_names()
            return [{'table_name': name} for name in collections]

    def close(self) -> None:
        self.client.close()

