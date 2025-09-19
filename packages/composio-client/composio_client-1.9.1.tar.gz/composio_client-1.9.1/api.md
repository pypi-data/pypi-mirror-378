# AuthConfigs

Types:

```python
from composio_client.types import (
    AuthConfigCreateResponse,
    AuthConfigRetrieveResponse,
    AuthConfigListResponse,
)
```

Methods:

- <code title="post /api/v3/auth_configs">client.auth_configs.<a href="./src/composio_client/resources/auth_configs.py">create</a>(\*\*<a href="src/composio_client/types/auth_config_create_params.py">params</a>) -> <a href="./src/composio_client/types/auth_config_create_response.py">AuthConfigCreateResponse</a></code>
- <code title="get /api/v3/auth_configs/{nanoid}">client.auth_configs.<a href="./src/composio_client/resources/auth_configs.py">retrieve</a>(nanoid) -> <a href="./src/composio_client/types/auth_config_retrieve_response.py">AuthConfigRetrieveResponse</a></code>
- <code title="patch /api/v3/auth_configs/{nanoid}">client.auth_configs.<a href="./src/composio_client/resources/auth_configs.py">update</a>(nanoid, \*\*<a href="src/composio_client/types/auth_config_update_params.py">params</a>) -> object</code>
- <code title="get /api/v3/auth_configs">client.auth_configs.<a href="./src/composio_client/resources/auth_configs.py">list</a>(\*\*<a href="src/composio_client/types/auth_config_list_params.py">params</a>) -> <a href="./src/composio_client/types/auth_config_list_response.py">AuthConfigListResponse</a></code>
- <code title="delete /api/v3/auth_configs/{nanoid}">client.auth_configs.<a href="./src/composio_client/resources/auth_configs.py">delete</a>(nanoid) -> object</code>
- <code title="patch /api/v3/auth_configs/{nanoid}/{status}">client.auth_configs.<a href="./src/composio_client/resources/auth_configs.py">update_status</a>(status, \*, nanoid) -> object</code>

# ConnectedAccounts

Types:

```python
from composio_client.types import (
    ConnectedAccountCreateResponse,
    ConnectedAccountRetrieveResponse,
    ConnectedAccountListResponse,
    ConnectedAccountDeleteResponse,
    ConnectedAccountRefreshResponse,
    ConnectedAccountUpdateStatusResponse,
)
```

Methods:

- <code title="post /api/v3/connected_accounts">client.connected_accounts.<a href="./src/composio_client/resources/connected_accounts.py">create</a>(\*\*<a href="src/composio_client/types/connected_account_create_params.py">params</a>) -> <a href="./src/composio_client/types/connected_account_create_response.py">ConnectedAccountCreateResponse</a></code>
- <code title="get /api/v3/connected_accounts/{nanoid}">client.connected_accounts.<a href="./src/composio_client/resources/connected_accounts.py">retrieve</a>(nanoid) -> <a href="./src/composio_client/types/connected_account_retrieve_response.py">ConnectedAccountRetrieveResponse</a></code>
- <code title="get /api/v3/connected_accounts">client.connected_accounts.<a href="./src/composio_client/resources/connected_accounts.py">list</a>(\*\*<a href="src/composio_client/types/connected_account_list_params.py">params</a>) -> <a href="./src/composio_client/types/connected_account_list_response.py">ConnectedAccountListResponse</a></code>
- <code title="delete /api/v3/connected_accounts/{nanoid}">client.connected_accounts.<a href="./src/composio_client/resources/connected_accounts.py">delete</a>(nanoid) -> <a href="./src/composio_client/types/connected_account_delete_response.py">ConnectedAccountDeleteResponse</a></code>
- <code title="post /api/v3/connected_accounts/{nanoid}/refresh">client.connected_accounts.<a href="./src/composio_client/resources/connected_accounts.py">refresh</a>(nanoid, \*\*<a href="src/composio_client/types/connected_account_refresh_params.py">params</a>) -> <a href="./src/composio_client/types/connected_account_refresh_response.py">ConnectedAccountRefreshResponse</a></code>
- <code title="patch /api/v3/connected_accounts/{nanoId}/status">client.connected_accounts.<a href="./src/composio_client/resources/connected_accounts.py">update_status</a>(nano_id, \*\*<a href="src/composio_client/types/connected_account_update_status_params.py">params</a>) -> <a href="./src/composio_client/types/connected_account_update_status_response.py">ConnectedAccountUpdateStatusResponse</a></code>

# Link

Types:

```python
from composio_client.types import LinkCreateResponse, LinkRetrieveResponse, LinkSubmitResponse
```

Methods:

- <code title="post /api/v3/connected_accounts/link">client.link.<a href="./src/composio_client/resources/link.py">create</a>(\*\*<a href="src/composio_client/types/link_create_params.py">params</a>) -> <a href="./src/composio_client/types/link_create_response.py">LinkCreateResponse</a></code>
- <code title="get /api/v3/internal/connected_accounts/link/{token}">client.link.<a href="./src/composio_client/resources/link.py">retrieve</a>(token) -> <a href="./src/composio_client/types/link_retrieve_response.py">LinkRetrieveResponse</a></code>
- <code title="post /api/v3/internal/connected_accounts/link/{token}">client.link.<a href="./src/composio_client/resources/link.py">submit</a>(token, \*\*<a href="src/composio_client/types/link_submit_params.py">params</a>) -> <a href="./src/composio_client/types/link_submit_response.py">LinkSubmitResponse</a></code>

# Org

## APIKey

Types:

```python
from composio_client.types.org import APIKeyRetrieveResponse, APIKeyRegenerateResponse
```

Methods:

- <code title="get /api/v3/org/api_key">client.org.api_key.<a href="./src/composio_client/resources/org/api_key.py">retrieve</a>() -> <a href="./src/composio_client/types/org/api_key_retrieve_response.py">APIKeyRetrieveResponse</a></code>
- <code title="post /api/v3/org/api_key/regenerate">client.org.api_key.<a href="./src/composio_client/resources/org/api_key.py">regenerate</a>() -> <a href="./src/composio_client/types/org/api_key_regenerate_response.py">APIKeyRegenerateResponse</a></code>

## Project

Types:

```python
from composio_client.types.org import (
    ProjectCreateResponse,
    ProjectRetrieveResponse,
    ProjectListResponse,
    ProjectDeleteResponse,
)
```

Methods:

- <code title="post /api/v3/org/project/new">client.org.project.<a href="./src/composio_client/resources/org/project/project.py">create</a>(\*\*<a href="src/composio_client/types/org/project_create_params.py">params</a>) -> <a href="./src/composio_client/types/org/project_create_response.py">ProjectCreateResponse</a></code>
- <code title="get /api/v3/org/project/{projectId}">client.org.project.<a href="./src/composio_client/resources/org/project/project.py">retrieve</a>(project_id) -> <a href="./src/composio_client/types/org/project_retrieve_response.py">ProjectRetrieveResponse</a></code>
- <code title="get /api/v3/org/project/list">client.org.project.<a href="./src/composio_client/resources/org/project/project.py">list</a>(\*\*<a href="src/composio_client/types/org/project_list_params.py">params</a>) -> <a href="./src/composio_client/types/org/project_list_response.py">ProjectListResponse</a></code>
- <code title="delete /api/v3/org/project/delete/{projectId}">client.org.project.<a href="./src/composio_client/resources/org/project/project.py">delete</a>(project_id) -> <a href="./src/composio_client/types/org/project_delete_response.py">ProjectDeleteResponse</a></code>

### APIKeys

Types:

```python
from composio_client.types.org.project import (
    APIKeyCreateResponse,
    APIKeyListResponse,
    APIKeyDeleteResponse,
)
```

Methods:

- <code title="post /api/v3/org/project/{projectId}/api_keys/create">client.org.project.api_keys.<a href="./src/composio_client/resources/org/project/api_keys.py">create</a>(project_id, \*\*<a href="src/composio_client/types/org/project/api_key_create_params.py">params</a>) -> <a href="./src/composio_client/types/org/project/api_key_create_response.py">APIKeyCreateResponse</a></code>
- <code title="get /api/v3/org/project/{projectId}/api_keys/list">client.org.project.api_keys.<a href="./src/composio_client/resources/org/project/api_keys.py">list</a>(project_id) -> <a href="./src/composio_client/types/org/project/api_key_list_response.py">APIKeyListResponse</a></code>
- <code title="delete /api/v3/org/project/{projectId}/api_keys/remove/{id}">client.org.project.api_keys.<a href="./src/composio_client/resources/org/project/api_keys.py">delete</a>(id, \*, project_id) -> <a href="./src/composio_client/types/org/project/api_key_delete_response.py">APIKeyDeleteResponse</a></code>

### Webhook

Types:

```python
from composio_client.types.org.project import (
    WebhookRetrieveResponse,
    WebhookUpdateResponse,
    WebhookDeleteResponse,
    WebhookRefreshResponse,
)
```

Methods:

- <code title="get /api/v3/org/project/webhook">client.org.project.webhook.<a href="./src/composio_client/resources/org/project/webhook.py">retrieve</a>(\*\*<a href="src/composio_client/types/org/project/webhook_retrieve_params.py">params</a>) -> <a href="./src/composio_client/types/org/project/webhook_retrieve_response.py">WebhookRetrieveResponse</a></code>
- <code title="post /api/v3/org/project/webhook/update">client.org.project.webhook.<a href="./src/composio_client/resources/org/project/webhook.py">update</a>(\*\*<a href="src/composio_client/types/org/project/webhook_update_params.py">params</a>) -> <a href="./src/composio_client/types/org/project/webhook_update_response.py">WebhookUpdateResponse</a></code>
- <code title="delete /api/v3/org/project/webhook">client.org.project.webhook.<a href="./src/composio_client/resources/org/project/webhook.py">delete</a>(\*\*<a href="src/composio_client/types/org/project/webhook_delete_params.py">params</a>) -> <a href="./src/composio_client/types/org/project/webhook_delete_response.py">WebhookDeleteResponse</a></code>
- <code title="post /api/v3/org/project/webhook/refresh">client.org.project.webhook.<a href="./src/composio_client/resources/org/project/webhook.py">refresh</a>() -> <a href="./src/composio_client/types/org/project/webhook_refresh_response.py">WebhookRefreshResponse</a></code>

### Trigger

Types:

```python
from composio_client.types.org.project import TriggerUpdateResponse, TriggerListResponse
```

Methods:

- <code title="patch /api/v3/org/project/trigger">client.org.project.trigger.<a href="./src/composio_client/resources/org/project/trigger.py">update</a>(\*\*<a href="src/composio_client/types/org/project/trigger_update_params.py">params</a>) -> <a href="./src/composio_client/types/org/project/trigger_update_response.py">TriggerUpdateResponse</a></code>
- <code title="get /api/v3/org/project/trigger">client.org.project.trigger.<a href="./src/composio_client/resources/org/project/trigger.py">list</a>() -> <a href="./src/composio_client/types/org/project/trigger_list_response.py">TriggerListResponse</a></code>

# TeamMembers

Types:

```python
from composio_client.types import (
    TeamMemberUpdateResponse,
    TeamMemberListResponse,
    TeamMemberRemoveResponse,
)
```

Methods:

- <code title="put /api/v3/team-members/update/{id}">client.team_members.<a href="./src/composio_client/resources/team_members.py">update</a>(id, \*\*<a href="src/composio_client/types/team_member_update_params.py">params</a>) -> <a href="./src/composio_client/types/team_member_update_response.py">TeamMemberUpdateResponse</a></code>
- <code title="get /api/v3/team-members/list">client.team_members.<a href="./src/composio_client/resources/team_members.py">list</a>() -> <a href="./src/composio_client/types/team_member_list_response.py">TeamMemberListResponse</a></code>
- <code title="post /api/v3/team-members/invite">client.team_members.<a href="./src/composio_client/resources/team_members.py">invite</a>() -> None</code>
- <code title="delete /api/v3/team-members/remove/{id}">client.team_members.<a href="./src/composio_client/resources/team_members.py">remove</a>(id) -> <a href="./src/composio_client/types/team_member_remove_response.py">TeamMemberRemoveResponse</a></code>

# Toolkits

Types:

```python
from composio_client.types import (
    ToolkitRetrieveResponse,
    ToolkitListResponse,
    ToolkitRetrieveCategoriesResponse,
)
```

Methods:

- <code title="get /api/v3/toolkits/{slug}">client.toolkits.<a href="./src/composio_client/resources/toolkits.py">retrieve</a>(slug) -> <a href="./src/composio_client/types/toolkit_retrieve_response.py">ToolkitRetrieveResponse</a></code>
- <code title="get /api/v3/toolkits">client.toolkits.<a href="./src/composio_client/resources/toolkits.py">list</a>(\*\*<a href="src/composio_client/types/toolkit_list_params.py">params</a>) -> <a href="./src/composio_client/types/toolkit_list_response.py">ToolkitListResponse</a></code>
- <code title="get /api/v3/toolkits/categories">client.toolkits.<a href="./src/composio_client/resources/toolkits.py">retrieve_categories</a>(\*\*<a href="src/composio_client/types/toolkit_retrieve_categories_params.py">params</a>) -> <a href="./src/composio_client/types/toolkit_retrieve_categories_response.py">ToolkitRetrieveCategoriesResponse</a></code>

# Tools

Types:

```python
from composio_client.types import (
    ToolRetrieveResponse,
    ToolListResponse,
    ToolExecuteResponse,
    ToolGetInputResponse,
    ToolProxyResponse,
    ToolRetrieveEnumResponse,
)
```

Methods:

- <code title="get /api/v3/tools/{tool_slug}">client.tools.<a href="./src/composio_client/resources/tools.py">retrieve</a>(tool_slug, \*\*<a href="src/composio_client/types/tool_retrieve_params.py">params</a>) -> <a href="./src/composio_client/types/tool_retrieve_response.py">ToolRetrieveResponse</a></code>
- <code title="get /api/v3/tools">client.tools.<a href="./src/composio_client/resources/tools.py">list</a>(\*\*<a href="src/composio_client/types/tool_list_params.py">params</a>) -> <a href="./src/composio_client/types/tool_list_response.py">ToolListResponse</a></code>
- <code title="post /api/v3/tools/execute/{tool_slug}">client.tools.<a href="./src/composio_client/resources/tools.py">execute</a>(tool_slug, \*\*<a href="src/composio_client/types/tool_execute_params.py">params</a>) -> <a href="./src/composio_client/types/tool_execute_response.py">ToolExecuteResponse</a></code>
- <code title="post /api/v3/tools/execute/{tool_slug}/input">client.tools.<a href="./src/composio_client/resources/tools.py">get_input</a>(tool_slug, \*\*<a href="src/composio_client/types/tool_get_input_params.py">params</a>) -> <a href="./src/composio_client/types/tool_get_input_response.py">ToolGetInputResponse</a></code>
- <code title="post /api/v3/tools/execute/proxy">client.tools.<a href="./src/composio_client/resources/tools.py">proxy</a>(\*\*<a href="src/composio_client/types/tool_proxy_params.py">params</a>) -> <a href="./src/composio_client/types/tool_proxy_response.py">ToolProxyResponse</a></code>
- <code title="get /api/v3/tools/enum">client.tools.<a href="./src/composio_client/resources/tools.py">retrieve_enum</a>() -> <a href="./src/composio_client/types/tool_retrieve_enum_response.py">ToolRetrieveEnumResponse</a></code>

# TriggerInstances

Types:

```python
from composio_client.types import TriggerInstanceListActiveResponse, TriggerInstanceUpsertResponse
```

Methods:

- <code title="get /api/v3/trigger_instances/active">client.trigger_instances.<a href="./src/composio_client/resources/trigger_instances/trigger_instances.py">list_active</a>(\*\*<a href="src/composio_client/types/trigger_instance_list_active_params.py">params</a>) -> <a href="./src/composio_client/types/trigger_instance_list_active_response.py">TriggerInstanceListActiveResponse</a></code>
- <code title="post /api/v3/trigger_instances/{slug}/upsert">client.trigger_instances.<a href="./src/composio_client/resources/trigger_instances/trigger_instances.py">upsert</a>(slug, \*\*<a href="src/composio_client/types/trigger_instance_upsert_params.py">params</a>) -> <a href="./src/composio_client/types/trigger_instance_upsert_response.py">TriggerInstanceUpsertResponse</a></code>

## Handle

Types:

```python
from composio_client.types.trigger_instances import HandleRetrieveResponse, HandleExecuteResponse
```

Methods:

- <code title="get /api/v3/trigger_instances/{slug}/{projectId}/handle">client.trigger_instances.handle.<a href="./src/composio_client/resources/trigger_instances/handle.py">retrieve</a>(project_id, \*, slug) -> str</code>
- <code title="post /api/v3/trigger_instances/{slug}/{projectId}/handle">client.trigger_instances.handle.<a href="./src/composio_client/resources/trigger_instances/handle.py">execute</a>(project_id, \*, slug) -> str</code>

## Manage

Types:

```python
from composio_client.types.trigger_instances import ManageUpdateResponse, ManageDeleteResponse
```

Methods:

- <code title="patch /api/v3/trigger_instances/manage/{triggerId}">client.trigger_instances.manage.<a href="./src/composio_client/resources/trigger_instances/manage.py">update</a>(trigger_id, \*\*<a href="src/composio_client/types/trigger_instances/manage_update_params.py">params</a>) -> <a href="./src/composio_client/types/trigger_instances/manage_update_response.py">ManageUpdateResponse</a></code>
- <code title="delete /api/v3/trigger_instances/manage/{triggerId}">client.trigger_instances.manage.<a href="./src/composio_client/resources/trigger_instances/manage.py">delete</a>(trigger_id) -> <a href="./src/composio_client/types/trigger_instances/manage_delete_response.py">ManageDeleteResponse</a></code>

# TriggersTypes

Types:

```python
from composio_client.types import (
    TriggersTypeRetrieveResponse,
    TriggersTypeListResponse,
    TriggersTypeRetrieveEnumResponse,
)
```

Methods:

- <code title="get /api/v3/triggers_types/{slug}">client.triggers_types.<a href="./src/composio_client/resources/triggers_types.py">retrieve</a>(slug, \*\*<a href="src/composio_client/types/triggers_type_retrieve_params.py">params</a>) -> <a href="./src/composio_client/types/triggers_type_retrieve_response.py">TriggersTypeRetrieveResponse</a></code>
- <code title="get /api/v3/triggers_types">client.triggers_types.<a href="./src/composio_client/resources/triggers_types.py">list</a>(\*\*<a href="src/composio_client/types/triggers_type_list_params.py">params</a>) -> <a href="./src/composio_client/types/triggers_type_list_response.py">TriggersTypeListResponse</a></code>
- <code title="get /api/v3/triggers_types/list/enum">client.triggers_types.<a href="./src/composio_client/resources/triggers_types.py">retrieve_enum</a>() -> <a href="./src/composio_client/types/triggers_type_retrieve_enum_response.py">TriggersTypeRetrieveEnumResponse</a></code>

# Mcp

Types:

```python
from composio_client.types import (
    McpCreateResponse,
    McpRetrieveResponse,
    McpUpdateResponse,
    McpListResponse,
    McpDeleteResponse,
    McpRetrieveAppResponse,
    McpValidateResponse,
)
```

Methods:

- <code title="post /api/v3/mcp/servers">client.mcp.<a href="./src/composio_client/resources/mcp/mcp.py">create</a>(\*\*<a href="src/composio_client/types/mcp_create_params.py">params</a>) -> <a href="./src/composio_client/types/mcp_create_response.py">McpCreateResponse</a></code>
- <code title="get /api/v3/mcp/{id}">client.mcp.<a href="./src/composio_client/resources/mcp/mcp.py">retrieve</a>(id) -> <a href="./src/composio_client/types/mcp_retrieve_response.py">McpRetrieveResponse</a></code>
- <code title="patch /api/v3/mcp/{id}">client.mcp.<a href="./src/composio_client/resources/mcp/mcp.py">update</a>(id, \*\*<a href="src/composio_client/types/mcp_update_params.py">params</a>) -> <a href="./src/composio_client/types/mcp_update_response.py">McpUpdateResponse</a></code>
- <code title="get /api/v3/mcp/servers">client.mcp.<a href="./src/composio_client/resources/mcp/mcp.py">list</a>(\*\*<a href="src/composio_client/types/mcp_list_params.py">params</a>) -> <a href="./src/composio_client/types/mcp_list_response.py">McpListResponse</a></code>
- <code title="delete /api/v3/mcp/{id}">client.mcp.<a href="./src/composio_client/resources/mcp/mcp.py">delete</a>(id) -> <a href="./src/composio_client/types/mcp_delete_response.py">McpDeleteResponse</a></code>
- <code title="get /api/v3/mcp/app/{appKey}">client.mcp.<a href="./src/composio_client/resources/mcp/mcp.py">retrieve_app</a>(app_key, \*\*<a href="src/composio_client/types/mcp_retrieve_app_params.py">params</a>) -> <a href="./src/composio_client/types/mcp_retrieve_app_response.py">McpRetrieveAppResponse</a></code>
- <code title="get /api/v3/mcp/validate/{uuid}">client.mcp.<a href="./src/composio_client/resources/mcp/mcp.py">validate</a>(uuid) -> <a href="./src/composio_client/types/mcp_validate_response.py">McpValidateResponse</a></code>

## Custom

Types:

```python
from composio_client.types.mcp import CustomCreateResponse
```

Methods:

- <code title="post /api/v3/mcp/servers/custom">client.mcp.custom.<a href="./src/composio_client/resources/mcp/custom.py">create</a>(\*\*<a href="src/composio_client/types/mcp/custom_create_params.py">params</a>) -> <a href="./src/composio_client/types/mcp/custom_create_response.py">CustomCreateResponse</a></code>

## Generate

Types:

```python
from composio_client.types.mcp import GenerateURLResponse
```

Methods:

- <code title="post /api/v3/mcp/servers/generate">client.mcp.generate.<a href="./src/composio_client/resources/mcp/generate.py">url</a>(\*\*<a href="src/composio_client/types/mcp/generate_url_params.py">params</a>) -> <a href="./src/composio_client/types/mcp/generate_url_response.py">GenerateURLResponse</a></code>

# Files

Types:

```python
from composio_client.types import FileListResponse, FileCreatePresignedURLResponse
```

Methods:

- <code title="get /api/v3/files/list">client.files.<a href="./src/composio_client/resources/files.py">list</a>(\*\*<a href="src/composio_client/types/file_list_params.py">params</a>) -> <a href="./src/composio_client/types/file_list_response.py">FileListResponse</a></code>
- <code title="post /api/v3/files/upload/request">client.files.<a href="./src/composio_client/resources/files.py">create_presigned_url</a>(\*\*<a href="src/composio_client/types/file_create_presigned_url_params.py">params</a>) -> <a href="./src/composio_client/types/file_create_presigned_url_response.py">FileCreatePresignedURLResponse</a></code>

# Migration

Types:

```python
from composio_client.types import MigrationRetrieveNanoidResponse
```

Methods:

- <code title="get /api/v3/migration/get-nanoid">client.migration.<a href="./src/composio_client/resources/migration.py">retrieve_nanoid</a>(\*\*<a href="src/composio_client/types/migration_retrieve_nanoid_params.py">params</a>) -> <a href="./src/composio_client/types/migration_retrieve_nanoid_response.py">MigrationRetrieveNanoidResponse</a></code>

# Cli

Types:

```python
from composio_client.types import (
    CliCreateSessionResponse,
    CliGetSessionResponse,
    CliLinkSessionResponse,
)
```

Methods:

- <code title="post /api/v3/cli/create-session">client.cli.<a href="./src/composio_client/resources/cli.py">create_session</a>() -> <a href="./src/composio_client/types/cli_create_session_response.py">CliCreateSessionResponse</a></code>
- <code title="get /api/v3/cli/get-session">client.cli.<a href="./src/composio_client/resources/cli.py">get_session</a>(\*\*<a href="src/composio_client/types/cli_get_session_params.py">params</a>) -> <a href="./src/composio_client/types/cli_get_session_response.py">CliGetSessionResponse</a></code>
- <code title="put /api/v3/cli/link-session">client.cli.<a href="./src/composio_client/resources/cli.py">link_session</a>(\*\*<a href="src/composio_client/types/cli_link_session_params.py">params</a>) -> <a href="./src/composio_client/types/cli_link_session_response.py">CliLinkSessionResponse</a></code>
