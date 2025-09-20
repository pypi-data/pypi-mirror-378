base_tools = [  # noqa: D100
    {
        "name": "end_call",
        "description": "End the current call when the conversation has reached a natural conclusion or user says bye or tells to cut the call or speak with you later as they are busy.",
        "parameters": {
            "type": "object",
            "properties": {
                "final_message": {
                    "type": "string",
                    "description": "The final message to say to the user before ending the call. Should be a polite goodbye message appropriate for the conversation context. Keep is short and less than 15 words.",
                }
            },
            "required": ["final_message"],
        },
    }
]


rag_tool = {
    "name": "query_knowledge_base",
    "description": (
        "Retrieve and synthesize a concise answer from the knowledge base based on the given question. "
        "The input should include detailed context and any relevant keywords to enable accurate and targeted search results. "
        "This tool uses a retrieval-augmented generation approach to extract key information from stored records, so providing maximum relevant details will improve the quality of the generated answer."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": (
                    "The question to query the knowledge base with. Include as much context and specific details as possible "
                    "to ensure that the retrieval-augmented generation process can fetch the most relevant records and generate an accurate answer."
                ),
            },
            "rag_file_name": {
                "type": "string",
                "description": (
                    "The name of the file that contains the knowledge base to search in order to answer the question. "
                    "Ensure the correct file is referenced to get relevant results."
                ),
            },
        },
        "required": ["question", "rag_file_name"],
    },
}


def create_rag_tools(kb_data):
    """
    Create dynamic RAG tools based on knowledge base data.

    Args:
        kb_data: List of KB entries with structure:
            [{
                "name": "kb_name",
                "kb_id": "uuid",
                "type": "deterministic" | "non_deterministic",
                "search_fields": [...] (optional, for deterministic KBs)
            }]

    Returns:
        List of tool dictionaries for RAG functionality
    """
    rag_tools = []

    if not kb_data:
        return rag_tools

    for kb_entry in kb_data:
        kb_name = kb_entry["name"]
        kb_type = kb_entry["type"]

        # Create tool name based on KB name
        tool_name = f"query_kb_{kb_name.lower().replace(' ', '_').replace('-', '_')}"

        # Base properties for all KB types
        properties = {
            "kb_id": {
                "type": "string",
                "description": "The unique identifier of the knowledge base to query",
            },
            "question": {
                "type": "string",
                "description": "The question to query the knowledge base with. Include as much context and specific details as possible to ensure that the retrieval-augmented generation process can fetch the most relevant records and generate an accurate answer.",
            },
        }
        required = ["kb_id", "question"]

        # Add search field properties for deterministic KBs
        if kb_type == "deterministic" and "search_fields" in kb_entry:
            search_fields = kb_entry["search_fields"]
            for field in search_fields:
                field_name = field.get("field_name")
                field_description = field.get("description", f"The {field_name} field")
                field_type = field.get("field_type", "string")

                if field_name:
                    properties[field_name] = {"type": field_type, "description": field_description}
                    required.append(field_name)

        # Generate appropriate description based on KB type
        if kb_type == "deterministic":
            description = f"Query the {kb_name} knowledge base for specific data using structured search parameters. This is a deterministic search that requires exact field values to retrieve precise results."
        else:
            description = f"Retrieve and synthesize a concise answer from the {kb_name} knowledge base based on the given question. The input should include detailed context and any relevant keywords to enable accurate and targeted search results. This tool uses a retrieval-augmented generation approach to extract key information from stored records, so providing maximum relevant details will improve the quality of the generated answer."

        # Create dynamic RAG tool
        rag_tool = {
            "name": tool_name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }

        rag_tools.append(rag_tool)

    return rag_tools
