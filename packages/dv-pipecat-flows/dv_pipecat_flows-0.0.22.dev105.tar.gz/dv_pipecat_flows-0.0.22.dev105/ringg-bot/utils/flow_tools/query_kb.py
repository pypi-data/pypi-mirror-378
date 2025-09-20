"""Flow-native query_kb tool implementation."""

import random
import time
from typing import List
from pipecat_flows import FlowManager
from pipecat_flows.types import FlowResult
from pipecat.frames.frames import TTSSpeakFrame, LLMMessagesAppendFrame
from weaviate.classes.query import Filter


async def query_kb(flow_manager: FlowManager, kb_id: str, question: str, **kwargs) -> FlowResult:
    """
    Retrieve and synthesize a concise answer from the knowledge base based on the given question. The input should include detailed context and any relevant keywords to enable accurate and targeted search results. This tool uses a retrieval-augmented generation approach to extract key information from stored records, so providing maximum relevant details will improve the quality of the generated answer.

    Args:
        kb_id: The unique identifier of the knowledge base to query
        question: The question to query the knowledge base with. Include as much context and specific details as possible to ensure that the retrieval-augmented generation process can fetch the most relevant records and generate an accurate answer.
        **kwargs: Additional search fields for deterministic KB queries (e.g., customer_id, subscription_status)

    Returns:
        FlowResult with retrieved KB chunks
    """
    s = flow_manager.state
    logger = s.get("bot_logger")
    monitor = s.get("function_call_monitor", [])
    pre_query_phrases: List[str] = s.get("pre_query_phrases", [])
    weaviate_client = s.get("weaviate_client")

    # Get workspace_id for multi-tenancy
    workspace_id = s.get("workspace_id")

    # Get current node and function config
    current_node = flow_manager.current_node
    nodes_runtime_config = s.get("nodes_runtime_config", {})

    # Get collection names from global config (new multi-tenant collection structure)
    collection_name = s.get("collection_name")  # Main chunks collection
    facets_collection_name = s.get("facets_collection_name")  # Facets collection for metadata

    # Get KB type from runtime config if available
    kb_function_name = next(
        (
            name
            for name in nodes_runtime_config.get(current_node, {}).get("functions", {}).keys()
            if name.startswith("query_kb")
        ),
        "query_kb",
    )
    kb_config = (
        nodes_runtime_config.get(current_node, {}).get("functions", {}).get(kb_function_name, {})
    )
    kb_type = kb_config.get("type", "non_deterministic")

    monitor.append("query_knowledge_base_called")

    if logger:
        logger.info(
            f"Query KB - Node: {current_node}, KB ID: {kb_id}, Collection: {collection_name}, "
            f"Workspace: {workspace_id}, KB Type: {kb_type}, Search Fields: {kwargs}"
        )

    # 60% chance: speak a pre-query phrase AND append to context
    if pre_query_phrases and random.random() < 0.6:
        phrase = random.choice(pre_query_phrases)
        await flow_manager.llm.push_frame(TTSSpeakFrame(text=phrase))
        await flow_manager.llm.push_frame(
            LLMMessagesAppendFrame(
                messages=[{"role": "assistant", "content": phrase}], run_llm=False
            )
        )

    # Check if KB is configured
    if not kb_id:
        if logger:
            logger.error(f"KB ID not provided as parameter")
        return ({"status": "error", "error": "KB ID is required"}, None)

    if not weaviate_client:
        if logger:
            logger.error("Weaviate client not initialized")
        return ({"status": "error", "error": "Weaviate client not available"}, None)

    if not collection_name:
        if logger:
            logger.error("Collection name not configured")
        return ({"status": "error", "error": "Collection name not configured"}, None)

    if kb_type == "deterministic" and not facets_collection_name:
        if logger:
            logger.error("Facets collection name not configured for deterministic KB")
        return ({"status": "error", "error": "Facets collection not configured"}, None)

    if not workspace_id:
        if logger:
            logger.error("Workspace ID not available for multi-tenant query")
        return ({"status": "error", "error": "Workspace ID not configured"}, None)

    try:
        start = time.perf_counter()

        if kb_type == "deterministic":
            # For deterministic KBs, query chunks directly with cross-reference filters to facets
            collection = weaviate_client.collections.get(collection_name)

            # Build base filter for KB ID
            chunks_filter = Filter.by_property("knowledge_base_id").equal(kb_id)

            # Add cross-reference filters for search fields through facets
            if kwargs:
                for field_name, field_value in kwargs.items():
                    if field_value is not None:
                        # Filter chunks that have facets matching the search criteria
                        # Use .with_where() to ensure both conditions apply to the same facet
                        facet_filter = Filter.by_ref("has_facet").with_where(
                            Filter.by_property("key").equal(field_name)
                            & Filter.by_property("str_val").equal(str(field_value))
                        )
                        chunks_filter = chunks_filter & facet_filter

            # Single query to get chunks with matching facets
            resp = await collection.with_tenant(str(workspace_id)).query.fetch_objects(
                filters=chunks_filter, limit=5
            )

        else:
            # For non-deterministic KBs, use vector search with semantic similarity
            collection = weaviate_client.collections.get(collection_name)
            filters = Filter.by_property("knowledge_base_id").equal(kb_id)

            resp = await collection.with_tenant(str(workspace_id)).query.near_text(
                query=question, limit=5, filters=filters
            )

        took = time.perf_counter() - start
        if logger:
            logger.info(f"KB query ({kb_type}) took {took:.2f}s, found {len(resp.objects)} results")

        if not resp.objects:
            answer = "No relevant information found."
        else:
            answer = "\n".join(obj.properties["chunk"] for obj in resp.objects)

        # Don't add tool message here - pipecat framework handles tool result messages automatically
        return ({"status": "success", "data": {"answer": answer}}, None)

    except Exception as e:
        if logger:
            logger.error(f"Error during KB query: {str(e)}")
        return ({"status": "error", "error": "Failed to query knowledge base"}, None)
