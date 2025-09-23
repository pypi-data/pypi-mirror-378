from vector_bridge import VectorBridgeClient
from vector_bridge.sync.admin.functions import FunctionsAdmin
from vector_bridge.sync.admin.instructions import InstructionsAdmin
from vector_bridge.sync.admin.integrations import IntegrationsAdmin
from vector_bridge.sync.admin.mcp import MCPAdmin
from vector_bridge.sync.admin.organization import OrganizationAdmin
from vector_bridge.sync.admin.security_groups import SecurityGroupsAdmin
from vector_bridge.sync.admin.settings import SettingsAdmin
from vector_bridge.sync.admin.vector_db import VectorDBAdmin


class AdminClient:
    """Admin client providing access to all admin endpoints that require authentication."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client

        # Initialize admin subclients
        self.settings = SettingsAdmin(client)
        self.organization = OrganizationAdmin(client)
        self.security_groups = SecurityGroupsAdmin(client)
        self.integrations = IntegrationsAdmin(client)
        self.instructions = InstructionsAdmin(client)
        self.functions = FunctionsAdmin(client)
        self.mcp = MCPAdmin(client)
        self.vector_db = VectorDBAdmin(client)
