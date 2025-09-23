from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.asyncio.admin.functions import AsyncFunctionsAdmin
from vector_bridge.asyncio.admin.instructions import AsyncInstructionsAdmin
from vector_bridge.asyncio.admin.integrations import AsyncIntegrationsAdmin
from vector_bridge.asyncio.admin.mcp import AsyncMCPAdmin
from vector_bridge.asyncio.admin.organization import AsyncOrganizationAdmin
from vector_bridge.asyncio.admin.security_groups import \
    AsyncSecurityGroupsAdmin
from vector_bridge.asyncio.admin.settings import AsyncSettingsAdmin
from vector_bridge.asyncio.admin.vector_db import AsyncVectorDBAdmin


class AsyncAdminClient:
    """Async admin client providing access to all admin endpoints that require authentication."""

    def __init__(self, client: AsyncVectorBridgeClient):
        self.client = client

        # Initialize async admin subclients
        self.settings = AsyncSettingsAdmin(client)
        self.organization = AsyncOrganizationAdmin(client)
        self.security_groups = AsyncSecurityGroupsAdmin(client)
        self.integrations = AsyncIntegrationsAdmin(client)
        self.instructions = AsyncInstructionsAdmin(client)
        self.functions = AsyncFunctionsAdmin(client)
        self.mcp = AsyncMCPAdmin(client)
        self.vector_db = AsyncVectorDBAdmin(client)
