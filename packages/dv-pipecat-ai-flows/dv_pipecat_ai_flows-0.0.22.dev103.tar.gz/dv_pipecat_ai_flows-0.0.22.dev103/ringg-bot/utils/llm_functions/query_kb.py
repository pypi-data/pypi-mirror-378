import random
import time

from weaviate.classes.query import Filter
from pipecat.frames.frames import FunctionCallResultProperties


async def query_knowledge_base(
    function_name,
    tool_call_id,
    arguments,
    tts,
    pre_query_phrases,
    kb_name_to_id_map,
    weaviate_client,
    collection_name,
    result_callback,
    function_call_monitor,
    logger,
    workspace_id=None,
    facets_collection_name=None,
    kb_data=None,
):
    """
    Enhanced query_knowledge_base function supporting both deterministic and non-deterministic KBs.

    Args:
        kb_data: List of KB configurations from call_config.kb_data
        workspace_id: Workspace ID for multi-tenancy
        facets_collection_name: Collection name for facets (deterministic KBs)
        Other args: Standard parameters
    """
    function_call_monitor.append("query_knowledge_base_called")

    # 60% chance: speak a pre-query phrase
    if random.random() < 0.6 and pre_query_phrases:
        phrase = random.choice(pre_query_phrases)
        await tts.say(phrase)

    question = arguments.get("question", "")
    kb_id = arguments.get("kb_id")

    logger.info(
        f"Querying knowledge base - Tool Call ID: {tool_call_id}, KB ID: {kb_id}, Question: {question}"
    )

    try:
        # Determine KB configuration and type
        kb_type = "non_deterministic"  # Default
        kb_config = None

        # Find KB configuration from kb_data
        if kb_data and kb_id:
            for kb_entry in kb_data:
                if kb_entry.get("kb_id") == kb_id:
                    kb_config = kb_entry
                    kb_type = kb_entry.get("type", "non_deterministic")
                    break

        # Validation
        if not kb_id:
            logger.error(f"KB ID not provided in {tool_call_id}")
            answer = "KB ID is required."
            await result_callback(answer)
            return

        if not weaviate_client:
            logger.error("Weaviate client not initialized")
            answer = "Knowledge base service not available."
            await result_callback(answer)
            return

        if not collection_name:
            logger.error("Collection name not configured")
            answer = "Knowledge base not properly configured."
            await result_callback(answer)
            return

        if kb_type == "deterministic" and not facets_collection_name:
            logger.error("Facets collection name not configured for deterministic KB")
            answer = "Knowledge base facets not configured."
            await result_callback(answer)
            return

        start = time.perf_counter()

        if kb_type == "deterministic":
            # For deterministic KBs, query chunks directly with cross-reference filters to facets
            collection = weaviate_client.collections.get(collection_name)

            # Build base filter for KB ID
            chunks_filter = Filter.by_property("knowledge_base_id").equal(kb_id)

            # Add cross-reference filters for search fields through facets
            search_fields = {k: v for k, v in arguments.items() if k not in ["question", "kb_id"]}
            if search_fields:
                for field_name, field_value in search_fields.items():
                    if field_value is not None:
                        # Filter chunks that have facets matching the search criteria
                        facet_filter = Filter.by_ref("has_facet").with_where(
                            Filter.by_property("key").equal(field_name)
                            & Filter.by_property("str_val").equal(str(field_value))
                        )
                        chunks_filter = chunks_filter & facet_filter

            # Single query to get chunks with matching facets
            if workspace_id:
                response = await collection.with_tenant(str(workspace_id)).query.fetch_objects(
                    filters=chunks_filter, limit=5
                )
            else:
                response = await collection.query.fetch_objects(filters=chunks_filter, limit=5)

        else:
            # For non-deterministic KBs, use vector search with semantic similarity
            collection = weaviate_client.collections.get(collection_name)
            filters = Filter.by_property("knowledge_base_id").equal(kb_id)

            if workspace_id:
                response = await collection.with_tenant(str(workspace_id)).query.near_text(
                    query=question, limit=5, filters=filters
                )
            else:
                response = await collection.query.near_text(
                    query=question, limit=5, filters=filters
                )

        took = time.perf_counter() - start
        logger.info(f"KB query ({kb_type}) took {took:.2f}s, found {len(response.objects)} results")

        if not response.objects:
            answer = "No relevant information found."
        else:
            answer = "\n".join(obj.properties["chunk"] for obj in response.objects)

        await result_callback(answer, properties=FunctionCallResultProperties(run_llm=True))

    except Exception as e:
        logger.error(f"Error during knowledge base query {tool_call_id}: {str(e)}")
        answer = "Technical issue in fetching the relevant information."
        await result_callback(answer, properties=FunctionCallResultProperties(run_llm=True))
