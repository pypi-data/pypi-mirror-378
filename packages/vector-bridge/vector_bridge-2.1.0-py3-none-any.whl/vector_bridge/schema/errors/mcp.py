from vector_bridge.schema.errors.base import raise_for_status


def raise_for_mcp_detail(response_data: dict):
    """Raise appropriate exception for MCP-related errors."""
    raise_for_status(response_data)
