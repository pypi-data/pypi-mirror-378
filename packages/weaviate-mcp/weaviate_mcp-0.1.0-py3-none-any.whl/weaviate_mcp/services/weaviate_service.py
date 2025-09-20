"""Weaviate service implementation for MCP server."""

import logging
from typing import Any

from weaviate import WeaviateAsyncClient
from weaviate.classes.config import Configure, Property
from weaviate.classes.init import AdditionalConfig, Timeout
from weaviate.classes.query import Filter, MetadataQuery, Sort
from weaviate.connect import ConnectionParams

from ..auth import get_openai_api_key
from ..config import get_weaviate_config

logger = logging.getLogger(__name__)


class WeaviateService:
    """Weaviate service for MCP server with fail-safe error handling."""

    def __init__(self):
        """Initialize the Weaviate service."""
        try:
            # Get configuration from environment
            config = get_weaviate_config()
            openai_api_key = get_openai_api_key()

            # Create the Weaviate client directly
            self._client = WeaviateAsyncClient(
                connection_params=ConnectionParams.from_params(
                    http_host=config["url"],
                    http_port=config["http_port"],
                    http_secure=False,  # Default to False for local development
                    grpc_host=config["url"],
                    grpc_port=config["grpc_port"],
                    grpc_secure=False,  # Default to False for local development
                ),
                additional_headers={"X-OpenAI-Api-Key": openai_api_key},
                additional_config=AdditionalConfig(
                    timeout=Timeout(
                        init=30,
                        query=60,
                        insert=120,
                    ),
                ),
                skip_init_checks=False,
            )
            logger.info("WeaviateService initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WeaviateService: {e}")
            # Don't raise - let individual methods handle connection errors
            self._client = None

    # Collection management methods
    async def get_schema(self) -> dict[str, Any]:
        """Get current schema."""
        try:
            if not self._client:
                return {"error": True, "message": "Weaviate client not initialized"}

            return await self._client.collections.list_all()
        except Exception as e:
            logger.error(f"Error getting schema: {e}")
            return {"error": True, "message": str(e)}

    async def create_collection(
        self,
        name: str,
        description: str,
        properties: list[Property],
        vectorizer_config: Configure.Vectorizer | None = None,
        generative_config: Configure.Generative | None = None,
    ) -> dict[str, Any]:
        """Create a new collection."""
        try:
            if not self._client:
                return {"error": True, "message": "Weaviate client not initialized"}

            await self._client.collections.create(
                name=name,
                description=description,
                properties=properties,
                vectorizer_config=vectorizer_config,
                generative_config=generative_config,
            )
            return {
                "success": True,
                "message": f"Collection '{name}' created successfully",
            }
        except Exception as e:
            logger.error(f"Error creating collection {name}: {e}")
            return {"error": True, "message": str(e)}

    async def delete_collection(self, name: str) -> dict[str, Any]:
        """Delete a collection."""
        try:
            if not self._client:
                return {"error": True, "message": "Weaviate client not initialized"}

            await self._client.collections.delete(name)
            return {
                "success": True,
                "message": f"Collection '{name}' deleted successfully",
            }
        except Exception as e:
            logger.error(f"Error deleting collection {name}: {e}")
            return {"error": True, "message": str(e)}

    # Object operations
    async def insert_object(
        self,
        collection_name: str,
        data: dict[str, Any],
        unique_properties: list[str] | None = None,
    ) -> dict[str, Any]:
        """Insert a new object."""
        try:
            if not self._client:
                return {"error": True, "message": "Weaviate client not initialized"}

            collection = self._client.collections.get(collection_name)

            if unique_properties:
                filters = Filter.all_of(
                    *[Filter.by_property(prop).equal(data.get(prop)) for prop in unique_properties if prop in data]
                )
                existing_result = await self.get_objects(collection_name, filters=filters, limit=1)
                if existing_result.get("objects"):
                    logger.warning(f"Object with properties {unique_properties} already exists")
                    return {
                        "success": True,
                        "object_id": existing_result["objects"][0]["id"],
                    }

            object_id = await collection.data.insert(data)
            return {"success": True, "object_id": str(object_id)}
        except Exception as e:
            logger.error(f"Error inserting object into {collection_name}: {e}")
            return {"error": True, "message": str(e)}

    async def get_object(
        self,
        collection_name: str,
        uuid: str,
        include_vector: bool = False,
        return_properties: list[str] | None = None,
    ) -> dict[str, Any]:
        """Get object by ID."""
        try:
            if not self._client:
                return {"error": True, "message": "Weaviate client not initialized"}

            collection = self._client.collections.get(collection_name)
            result = await collection.query.fetch_object_by_id(
                uuid,
                include_vector=include_vector,
                return_properties=return_properties,
            )

            if result:
                properties = result.properties
                properties["id"] = str(result.uuid)
                return properties
            return {"error": True, "message": f"Object {uuid} not found"}
        except Exception as e:
            logger.error(f"Error getting object {uuid} from {collection_name}: {e}")
            return {"error": True, "message": str(e)}

    async def get_objects(
        self,
        collection_name: str,
        filters: Filter | None = None,
        limit: int = 20,
        offset: int = 0,
        sort: Sort | None = None,
        return_properties: list[str] | None = None,
        include_vector: bool = False,
    ) -> dict[str, Any]:
        """Get objects from a collection."""
        try:
            if not self._client:
                return {"error": True, "message": "Weaviate client not initialized"}

            collection = self._client.collections.get(collection_name)
            results = await collection.query.fetch_objects(
                filters=filters,
                limit=limit,
                offset=offset,
                sort=sort,
                return_properties=return_properties,
                include_vector=include_vector,
            )

            objects = []
            for obj in results.objects:
                properties = obj.properties
                properties["id"] = str(obj.uuid)
                objects.append(properties)

            return {"objects": objects, "count": len(objects)}
        except Exception as e:
            logger.error(f"Error retrieving objects from collection {collection_name}: {e}")
            return {"error": True, "message": str(e)}

    # Search operations
    async def search(
        self,
        collection_name: str,
        query_text: str,
        filters: Filter | None = None,
        limit: int = 10,
        offset: int = 0,
        include_vector: bool = False,
        return_properties: list[str] | None = None,
    ) -> dict[str, Any]:
        """Perform semantic search."""
        try:
            if not self._client:
                return {"error": True, "message": "Weaviate client not initialized"}

            collection = self._client.collections.get(collection_name)
            results = await collection.query.near_text(
                query=query_text,
                filters=filters,
                limit=limit,
                offset=offset,
                include_vector=include_vector,
                return_properties=return_properties,
                return_metadata=MetadataQuery(distance=True, certainty=True),
            )

            objects = []
            for obj in results.objects:
                properties = obj.properties
                properties["id"] = str(obj.uuid)
                properties["distance"] = obj.metadata.distance
                properties["certainty"] = obj.metadata.certainty
                objects.append(properties)

            return {"objects": objects, "count": len(objects)}
        except Exception as e:
            logger.error(f"Error searching in {collection_name}: {e}")
            return {"error": True, "message": str(e)}

    async def hybrid_search(
        self,
        collection_name: str,
        query_text: str,
        filters: Filter | None = None,
        limit: int = 10,
        alpha: float = 0.5,
        include_vector: bool = False,
        return_properties: list[str] | None = None,
    ) -> dict[str, Any]:
        """Perform hybrid search (semantic + keyword)."""
        try:
            if not self._client:
                return {"error": True, "message": "Weaviate client not initialized"}

            collection = self._client.collections.get(collection_name)
            results = await collection.query.hybrid(
                query=query_text,
                alpha=alpha,
                filters=filters,
                limit=limit,
                include_vector=include_vector,
                return_properties=return_properties,
                return_metadata=MetadataQuery(distance=True, certainty=True),
            )

            objects = []
            for obj in results.objects:
                properties = obj.properties
                properties["id"] = str(obj.uuid)
                properties["distance"] = obj.metadata.distance
                properties["certainty"] = obj.metadata.certainty
                objects.append(properties)

            return {"objects": objects, "count": len(objects)}
        except Exception as e:
            logger.error(f"Error performing hybrid search in {collection_name}: {e}")
            return {"error": True, "message": str(e)}

    # Additional object operations
    async def update_object(
        self,
        collection_name: str,
        uuid: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update an existing object."""
        try:
            if not self._client:
                return {"error": True, "message": "Weaviate client not initialized"}

            collection = self._client.collections.get(collection_name)
            await collection.data.update(uuid, data)
            return {"success": True, "message": f"Object {uuid} updated successfully"}
        except Exception as e:
            logger.error(f"Error updating object {uuid} in {collection_name}: {e}")
            return {"error": True, "message": str(e)}

    async def delete_object(
        self,
        collection_name: str,
        uuid: str,
    ) -> dict[str, Any]:
        """Delete an object."""
        try:
            if not self._client:
                return {"error": True, "message": "Weaviate client not initialized"}

            collection = self._client.collections.get(collection_name)
            await collection.data.delete_by_id(uuid)
            return {"success": True, "message": f"Object {uuid} deleted successfully"}
        except Exception as e:
            logger.error(f"Error deleting object {uuid} from {collection_name}: {e}")
            return {"error": True, "message": str(e)}

    async def batch_insert_objects(
        self,
        collection_name: str,
        objects: list[dict[str, Any]],
        unique_properties: list[str] | None = None,
        batch_size: int = 100,
    ) -> dict[str, Any]:
        """Batch insert objects."""
        try:
            if not self._client:
                return {"error": True, "message": "Weaviate client not initialized"}

            inserted_ids: list[str] = []
            for start_idx in range(0, len(objects), batch_size):
                chunk = objects[start_idx : start_idx + batch_size]

                # Process each object in the chunk
                chunk_results = []
                for obj in chunk:
                    if unique_properties:
                        # Check for existing objects with unique properties
                        filters = Filter.all_of(
                            *[Filter.by_property(prop).equal(obj.get(prop)) for prop in unique_properties if prop in obj]
                        )
                        existing_result = await self.get_objects(collection_name, filters=filters, limit=1)
                        if existing_result.get("objects"):
                            logger.warning(f"Object with properties {unique_properties} already exists")
                            chunk_results.append(existing_result["objects"][0]["id"])
                            continue

                    # Insert new object
                    insert_result = await self.insert_object(collection_name, obj)
                    if insert_result.get("success"):
                        chunk_results.append(insert_result["object_id"])
                    else:
                        return insert_result  # Return error if any insertion fails

                inserted_ids.extend(chunk_results)

            return {
                "success": True,
                "inserted_ids": inserted_ids,
                "count": len(inserted_ids),
            }
        except Exception as e:
            logger.error(f"Error batch inserting objects into {collection_name}: {e}")
            return {"error": True, "message": str(e)}

    async def aggregate(
        self,
        collection_name: str,
        group_by: list[str] | None = None,
        properties: list[str] | None = None,
    ) -> dict[str, Any]:
        """Perform aggregation on a collection."""
        try:
            if not self._client:
                return {"error": True, "message": "Weaviate client not initialized"}

            collection = self._client.collections.get(collection_name)
            query = collection.aggregate

            if group_by:
                query = query.group_by(group_by)
            if properties:
                for prop in properties:
                    query = query.with_fields(prop)

            results = await query.over_all(total_count=True)
            logger.info(f"Aggregation results for collection {collection_name}: {results}")
            return {"results": results}
        except Exception as e:
            logger.error(f"Error performing aggregation in collection {collection_name}: {e}")
            return {"error": True, "message": str(e)}
