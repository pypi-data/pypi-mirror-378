# API

## V1

Types:

```python
from scalekit_demo.types.api import (
    AuthMethod,
    Workspace,
    V1RetrieveResponse,
    V1AuthDiscoveryResponse,
    V1AuthSignupResponse,
    V1ExecuteToolResponse,
    V1FetchBulkResponse,
    V1RetrieveAuthCustomizationsResponse,
    V1RetrieveAuthFeaturesResponse,
    V1RetrieveAuthOrganizationsResponse,
    V1RetrieveAuthmethodsResponse,
    V1RetrieveConnectedAccountsSearchResponse,
    V1RetrieveOrganizationsSearchResponse,
    V1RetrieveUsersSearchResponse,
    V1SignupResponse,
    V1ToolsSetDefaultResponse,
)
```

Methods:

- <code title="get /api/v1/domains/{origin}">client.api.v1.<a href="./src/scalekit_demo/resources/api/v1/v1.py">retrieve</a>(origin) -> <a href="./src/scalekit_demo/types/api/v1_retrieve_response.py">V1RetrieveResponse</a></code>
- <code title="post /api/v1/auth:discovery">client.api.v1.<a href="./src/scalekit_demo/resources/api/v1/v1.py">auth_discovery</a>(\*\*<a href="src/scalekit_demo/types/api/v1_auth_discovery_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1_auth_discovery_response.py">V1AuthDiscoveryResponse</a></code>
- <code title="post /api/v1/auth:signup">client.api.v1.<a href="./src/scalekit_demo/resources/api/v1/v1.py">auth_signup</a>(\*\*<a href="src/scalekit_demo/types/api/v1_auth_signup_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1_auth_signup_response.py">V1AuthSignupResponse</a></code>
- <code title="post /api/v1/connected_accounts:delete">client.api.v1.<a href="./src/scalekit_demo/resources/api/v1/v1.py">connected_accounts_delete</a>(\*\*<a href="src/scalekit_demo/types/api/v1_connected_accounts_delete_params.py">params</a>) -> object</code>
- <code title="post /api/v1/execute_tool">client.api.v1.<a href="./src/scalekit_demo/resources/api/v1/v1.py">execute_tool</a>(\*\*<a href="src/scalekit_demo/types/api/v1_execute_tool_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1_execute_tool_response.py">V1ExecuteToolResponse</a></code>
- <code title="post /api/v1/fetch:bulk">client.api.v1.<a href="./src/scalekit_demo/resources/api/v1/v1.py">fetch_bulk</a>(\*\*<a href="src/scalekit_demo/types/api/v1_fetch_bulk_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1_fetch_bulk_response.py">V1FetchBulkResponse</a></code>
- <code title="get /api/v1/auth:customizations">client.api.v1.<a href="./src/scalekit_demo/resources/api/v1/v1.py">retrieve_auth_customizations</a>() -> <a href="./src/scalekit_demo/types/api/v1_retrieve_auth_customizations_response.py">V1RetrieveAuthCustomizationsResponse</a></code>
- <code title="get /api/v1/auth:features">client.api.v1.<a href="./src/scalekit_demo/resources/api/v1/v1.py">retrieve_auth_features</a>() -> <a href="./src/scalekit_demo/types/api/v1_retrieve_auth_features_response.py">V1RetrieveAuthFeaturesResponse</a></code>
- <code title="get /api/v1/auth:organizations">client.api.v1.<a href="./src/scalekit_demo/resources/api/v1/v1.py">retrieve_auth_organizations</a>() -> <a href="./src/scalekit_demo/types/api/v1_retrieve_auth_organizations_response.py">V1RetrieveAuthOrganizationsResponse</a></code>
- <code title="get /api/v1/authmethods">client.api.v1.<a href="./src/scalekit_demo/resources/api/v1/v1.py">retrieve_authmethods</a>(\*\*<a href="src/scalekit_demo/types/api/v1_retrieve_authmethods_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1_retrieve_authmethods_response.py">V1RetrieveAuthmethodsResponse</a></code>
- <code title="get /api/v1/connected_accounts:search">client.api.v1.<a href="./src/scalekit_demo/resources/api/v1/v1.py">retrieve_connected_accounts_search</a>(\*\*<a href="src/scalekit_demo/types/api/v1_retrieve_connected_accounts_search_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1_retrieve_connected_accounts_search_response.py">V1RetrieveConnectedAccountsSearchResponse</a></code>
- <code title="get /api/v1/organizations:search">client.api.v1.<a href="./src/scalekit_demo/resources/api/v1/v1.py">retrieve_organizations_search</a>(\*\*<a href="src/scalekit_demo/types/api/v1_retrieve_organizations_search_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1_retrieve_organizations_search_response.py">V1RetrieveOrganizationsSearchResponse</a></code>
- <code title="get /api/v1/session:active">client.api.v1.<a href="./src/scalekit_demo/resources/api/v1/v1.py">retrieve_session_active</a>() -> None</code>
- <code title="get /api/v1/sessions:me">client.api.v1.<a href="./src/scalekit_demo/resources/api/v1/v1.py">retrieve_sessions_me</a>(\*\*<a href="src/scalekit_demo/types/api/v1_retrieve_sessions_me_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/environments/get_current_session_response.py">GetCurrentSessionResponse</a></code>
- <code title="get /api/v1/users:search">client.api.v1.<a href="./src/scalekit_demo/resources/api/v1/v1.py">retrieve_users_search</a>(\*\*<a href="src/scalekit_demo/types/api/v1_retrieve_users_search_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1_retrieve_users_search_response.py">V1RetrieveUsersSearchResponse</a></code>
- <code title="post /api/v1/signup">client.api.v1.<a href="./src/scalekit_demo/resources/api/v1/v1.py">signup</a>(\*\*<a href="src/scalekit_demo/types/api/v1_signup_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1_signup_response.py">V1SignupResponse</a></code>
- <code title="post /api/v1/tools:set_default">client.api.v1.<a href="./src/scalekit_demo/resources/api/v1/v1.py">tools_set_default</a>(\*\*<a href="src/scalekit_demo/types/api/v1_tools_set_default_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1_tools_set_default_response.py">V1ToolsSetDefaultResponse</a></code>
- <code title="patch /api/v1/roles:set_defaults">client.api.v1.<a href="./src/scalekit_demo/resources/api/v1/v1.py">update_roles_set_defaults</a>(\*\*<a href="src/scalekit_demo/types/api/v1_update_roles_set_defaults_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/update_default_roles_response.py">UpdateDefaultRolesResponse</a></code>
- <code title="patch /api/v1/workspaces:onboard">client.api.v1.<a href="./src/scalekit_demo/resources/api/v1/v1.py">update_workspaces_onboard</a>(\*\*<a href="src/scalekit_demo/types/api/v1_update_workspaces_onboard_params.py">params</a>) -> None</code>

### Auth

Types:

```python
from scalekit_demo.types.api.v1 import (
    OtpRequest,
    VerifyPasswordLessResponse,
    AuthRetrieveStateResponse,
)
```

Methods:

- <code title="post /api/v1/auth/logout">client.api.v1.auth.<a href="./src/scalekit_demo/resources/api/v1/auth.py">logout</a>() -> None</code>
- <code title="post /api/v1/auth/passwordless:resend">client.api.v1.auth.<a href="./src/scalekit_demo/resources/api/v1/auth.py">passwordless_resend</a>() -> None</code>
- <code title="post /api/v1/auth/passwordless:verify">client.api.v1.auth.<a href="./src/scalekit_demo/resources/api/v1/auth.py">passwordless_verify</a>(\*\*<a href="src/scalekit_demo/types/api/v1/auth_passwordless_verify_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/verify_password_less_response.py">object</a></code>
- <code title="get /api/v1/auth/state">client.api.v1.auth.<a href="./src/scalekit_demo/resources/api/v1/auth.py">retrieve_state</a>() -> <a href="./src/scalekit_demo/types/api/v1/auth_retrieve_state_response.py">AuthRetrieveStateResponse</a></code>

### Billing

Types:

```python
from scalekit_demo.types.api.v1 import PriceTier, BillingRetrieveProductcatalogResponse
```

Methods:

- <code title="get /api/v1/billing/productcatalog">client.api.v1.billing.<a href="./src/scalekit_demo/resources/api/v1/billing.py">retrieve_productcatalog</a>() -> <a href="./src/scalekit_demo/types/api/v1/billing_retrieve_productcatalog_response.py">BillingRetrieveProductcatalogResponse</a></code>

### Clients

Types:

```python
from scalekit_demo.types.api.v1 import (
    Client,
    ClientRetrieveResponse,
    ClientUpdateResponse,
    ClientListResponse,
)
```

Methods:

- <code title="get /api/v1/clients/{client_id}">client.api.v1.clients.<a href="./src/scalekit_demo/resources/api/v1/clients/clients.py">retrieve</a>(client_id) -> <a href="./src/scalekit_demo/types/api/v1/client_retrieve_response.py">ClientRetrieveResponse</a></code>
- <code title="patch /api/v1/clients/{client_id}">client.api.v1.clients.<a href="./src/scalekit_demo/resources/api/v1/clients/clients.py">update</a>(client_id, \*\*<a href="src/scalekit_demo/types/api/v1/client_update_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/client_update_response.py">ClientUpdateResponse</a></code>
- <code title="get /api/v1/clients">client.api.v1.clients.<a href="./src/scalekit_demo/resources/api/v1/clients/clients.py">list</a>(\*\*<a href="src/scalekit_demo/types/api/v1/client_list_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/client_list_response.py">ClientListResponse</a></code>

#### Secrets

Types:

```python
from scalekit_demo.types.api.v1.clients import (
    UpdateClientSecret,
    UpdateClientSecretResponse,
    SecretCreateResponse,
)
```

Methods:

- <code title="post /api/v1/clients/{client_id}/secrets">client.api.v1.clients.secrets.<a href="./src/scalekit_demo/resources/api/v1/clients/secrets.py">create</a>(client_id) -> <a href="./src/scalekit_demo/types/api/v1/clients/secret_create_response.py">SecretCreateResponse</a></code>
- <code title="patch /api/v1/clients/{client_id}/secrets/{secret_id}">client.api.v1.clients.secrets.<a href="./src/scalekit_demo/resources/api/v1/clients/secrets.py">update</a>(secret_id, \*, client_id, \*\*<a href="src/scalekit_demo/types/api/v1/clients/secret_update_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/clients/update_client_secret_response.py">UpdateClientSecretResponse</a></code>
- <code title="delete /api/v1/clients/{client_id}/secrets/{secret_id}">client.api.v1.clients.secrets.<a href="./src/scalekit_demo/resources/api/v1/clients/secrets.py">delete</a>(secret_id, \*, client_id) -> None</code>

### ConnectedAccounts

Types:

```python
from scalekit_demo.types.api.v1 import (
    AuthorizationDetails,
    ConnectedAccount,
    ConnectedAccountForList,
    ConnectedAccountCreateResponse,
    ConnectedAccountListResponse,
    ConnectedAccountRetrieveAuthResponse,
)
```

Methods:

- <code title="post /api/v1/connected_accounts">client.api.v1.connected_accounts.<a href="./src/scalekit_demo/resources/api/v1/connected_accounts/connected_accounts.py">create</a>(\*\*<a href="src/scalekit_demo/types/api/v1/connected_account_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/connected_account_create_response.py">ConnectedAccountCreateResponse</a></code>
- <code title="get /api/v1/connected_accounts">client.api.v1.connected_accounts.<a href="./src/scalekit_demo/resources/api/v1/connected_accounts/connected_accounts.py">list</a>(\*\*<a href="src/scalekit_demo/types/api/v1/connected_account_list_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/connected_account_list_response.py">ConnectedAccountListResponse</a></code>
- <code title="get /api/v1/connected_accounts/auth">client.api.v1.connected_accounts.<a href="./src/scalekit_demo/resources/api/v1/connected_accounts/connected_accounts.py">retrieve_auth</a>(\*\*<a href="src/scalekit_demo/types/api/v1/connected_account_retrieve_auth_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/connected_account_retrieve_auth_response.py">ConnectedAccountRetrieveAuthResponse</a></code>

#### MagicLink

Types:

```python
from scalekit_demo.types.api.v1.connected_accounts import (
    MagicLinkCreateResponse,
    MagicLinkRedirectResponse,
)
```

Methods:

- <code title="post /api/v1/connected_accounts/magic_link">client.api.v1.connected_accounts.magic_link.<a href="./src/scalekit_demo/resources/api/v1/connected_accounts/magic_link.py">create</a>(\*\*<a href="src/scalekit_demo/types/api/v1/connected_accounts/magic_link_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/connected_accounts/magic_link_create_response.py">MagicLinkCreateResponse</a></code>
- <code title="post /api/v1/connected_accounts/magic_link/redirect">client.api.v1.connected_accounts.magic_link.<a href="./src/scalekit_demo/resources/api/v1/connected_accounts/magic_link.py">redirect</a>(\*\*<a href="src/scalekit_demo/types/api/v1/connected_accounts/magic_link_redirect_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/connected_accounts/magic_link_redirect_response.py">MagicLinkRedirectResponse</a></code>

### Connections

Types:

```python
from scalekit_demo.types.api.v1 import (
    Connection,
    CreateConnection,
    CreateConnectionResponse,
    GetConnectionResponse,
    ListConnection,
    OAuthConnectionConfig,
    OidcConnectionConfig,
    PasswordLessConfig,
    StaticAuthConfig,
    ToggleConnectionResponse,
    UpdateConnection,
    UpdateConnectionResponse,
    ConnectionRetrieveResponse,
    ConnectionListResponse,
    ConnectionRetrieveAppResponse,
)
```

Methods:

- <code title="post /api/v1/connections">client.api.v1.connections.<a href="./src/scalekit_demo/resources/api/v1/connections/connections.py">create</a>(\*\*<a href="src/scalekit_demo/types/api/v1/connection_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/create_connection_response.py">CreateConnectionResponse</a></code>
- <code title="get /api/v1/connections/{connection_id}/test-requests/{test_request_id}">client.api.v1.connections.<a href="./src/scalekit_demo/resources/api/v1/connections/connections.py">retrieve</a>(test_request_id, \*, connection_id) -> <a href="./src/scalekit_demo/types/api/v1/connection_retrieve_response.py">ConnectionRetrieveResponse</a></code>
- <code title="patch /api/v1/connections/{connection_id}">client.api.v1.connections.<a href="./src/scalekit_demo/resources/api/v1/connections/connections.py">update</a>(connection_id, \*\*<a href="src/scalekit_demo/types/api/v1/connection_update_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/update_connection_response.py">UpdateConnectionResponse</a></code>
- <code title="get /api/v1/connections">client.api.v1.connections.<a href="./src/scalekit_demo/resources/api/v1/connections/connections.py">list</a>(\*\*<a href="src/scalekit_demo/types/api/v1/connection_list_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/connection_list_response.py">ConnectionListResponse</a></code>
- <code title="delete /api/v1/connections/{connection_id}">client.api.v1.connections.<a href="./src/scalekit_demo/resources/api/v1/connections/connections.py">delete</a>(connection_id) -> None</code>
- <code title="get /api/v1/connections/app">client.api.v1.connections.<a href="./src/scalekit_demo/resources/api/v1/connections/connections.py">retrieve_app</a>(\*\*<a href="src/scalekit_demo/types/api/v1/connection_retrieve_app_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/connection_retrieve_app_response.py">ConnectionRetrieveAppResponse</a></code>
- <code title="patch /api/v1/connections/{connection_id}:disable">client.api.v1.connections.<a href="./src/scalekit_demo/resources/api/v1/connections/connections.py">update_connection_id_disable</a>(connection_id) -> <a href="./src/scalekit_demo/types/api/v1/toggle_connection_response.py">ToggleConnectionResponse</a></code>
- <code title="patch /api/v1/connections/{connection_id}:enable">client.api.v1.connections.<a href="./src/scalekit_demo/resources/api/v1/connections/connections.py">update_connection_id_enable</a>(connection_id) -> <a href="./src/scalekit_demo/types/api/v1/toggle_connection_response.py">ToggleConnectionResponse</a></code>

#### AuthRequests

Types:

```python
from scalekit_demo.types.api.v1.connections import User
```

Methods:

- <code title="post /api/v1/connections/{connection_id}/auth-requests/{login_request_id}/user">client.api.v1.connections.auth_requests.<a href="./src/scalekit_demo/resources/api/v1/connections/auth_requests.py">user</a>(login_request_id, \*, connection_id, \*\*<a href="src/scalekit_demo/types/api/v1/connections/auth_request_user_params.py">params</a>) -> None</code>

### DirectoryUserAttributes

Types:

```python
from scalekit_demo.types.api.v1 import (
    CreateUserAttributeResponse,
    ListUserAttributesResponse,
    UpdateUserAttributeResponse,
    UserAttribute,
)
```

Methods:

- <code title="patch /api/v1/directory-user-attributes/{key}">client.api.v1.directory_user_attributes.<a href="./src/scalekit_demo/resources/api/v1/directory_user_attributes.py">update</a>(path_key, \*\*<a href="src/scalekit_demo/types/api/v1/directory_user_attribute_update_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/update_user_attribute_response.py">UpdateUserAttributeResponse</a></code>
- <code title="delete /api/v1/directory-user-attributes/{key}">client.api.v1.directory_user_attributes.<a href="./src/scalekit_demo/resources/api/v1/directory_user_attributes.py">delete</a>(key) -> None</code>
- <code title="post /api/v1/directory-user-attributes">client.api.v1.directory_user_attributes.<a href="./src/scalekit_demo/resources/api/v1/directory_user_attributes.py">directory_user_attributes</a>(\*\*<a href="src/scalekit_demo/types/api/v1/directory_user_attribute_directory_user_attributes_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/create_user_attribute_response.py">CreateUserAttributeResponse</a></code>
- <code title="get /api/v1/directory-user-attributes">client.api.v1.directory_user_attributes.<a href="./src/scalekit_demo/resources/api/v1/directory_user_attributes.py">retrieve_directory_user_attributes</a>() -> <a href="./src/scalekit_demo/types/api/v1/list_user_attributes_response.py">ListUserAttributesResponse</a></code>

### Environments

Types:

```python
from scalekit_demo.types.api.v1 import (
    Environment,
    GetDNSRecordsRequest,
    GetEnvironmentResponse,
    UpdateEnvironmentResponse,
    UpdatePortalCustomizationResponse,
    EnvironmentCreateResponse,
    EnvironmentListResponse,
    EnvironmentAssetResponse,
    EnvironmentCustomDomainsResponse,
    EnvironmentDNSResponse,
    EnvironmentSAMLCertificatesGenerateResponse,
)
```

Methods:

- <code title="post /api/v1/environments">client.api.v1.environments.<a href="./src/scalekit_demo/resources/api/v1/environments/environments.py">create</a>(\*\*<a href="src/scalekit_demo/types/api/v1/environment_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/environment_create_response.py">EnvironmentCreateResponse</a></code>
- <code title="get /api/v1/environments/{id}">client.api.v1.environments.<a href="./src/scalekit_demo/resources/api/v1/environments/environments.py">retrieve</a>(id) -> <a href="./src/scalekit_demo/types/api/v1/get_environment_response.py">GetEnvironmentResponse</a></code>
- <code title="patch /api/v1/environments/{id}">client.api.v1.environments.<a href="./src/scalekit_demo/resources/api/v1/environments/environments.py">update</a>(id, \*\*<a href="src/scalekit_demo/types/api/v1/environment_update_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/update_environment_response.py">UpdateEnvironmentResponse</a></code>
- <code title="get /api/v1/environments">client.api.v1.environments.<a href="./src/scalekit_demo/resources/api/v1/environments/environments.py">list</a>(\*\*<a href="src/scalekit_demo/types/api/v1/environment_list_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/environment_list_response.py">EnvironmentListResponse</a></code>
- <code title="delete /api/v1/environments/{id}">client.api.v1.environments.<a href="./src/scalekit_demo/resources/api/v1/environments/environments.py">delete</a>(id) -> None</code>
- <code title="post /api/v1/environments/{id}/asset">client.api.v1.environments.<a href="./src/scalekit_demo/resources/api/v1/environments/environments.py">asset</a>(id, \*\*<a href="src/scalekit_demo/types/api/v1/environment_asset_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/environment_asset_response.py">EnvironmentAssetResponse</a></code>
- <code title="post /api/v1/environments/{id}/custom-domains">client.api.v1.environments.<a href="./src/scalekit_demo/resources/api/v1/environments/environments.py">custom_domains</a>(path_id, \*\*<a href="src/scalekit_demo/types/api/v1/environment_custom_domains_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/environment_custom_domains_response.py">EnvironmentCustomDomainsResponse</a></code>
- <code title="post /api/v1/environments/{id}/custom-domains:check">client.api.v1.environments.<a href="./src/scalekit_demo/resources/api/v1/environments/environments.py">custom_domains_check</a>(path_id, \*\*<a href="src/scalekit_demo/types/api/v1/environment_custom_domains_check_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/get_environment_response.py">GetEnvironmentResponse</a></code>
- <code title="post /api/v1/environments/{id}/dns">client.api.v1.environments.<a href="./src/scalekit_demo/resources/api/v1/environments/environments.py">dns</a>(path_id, \*\*<a href="src/scalekit_demo/types/api/v1/environment_dns_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/environment_dns_response.py">EnvironmentDNSResponse</a></code>
- <code title="post /api/v1/environments/{id}/dns:verify">client.api.v1.environments.<a href="./src/scalekit_demo/resources/api/v1/environments/environments.py">dns_verify</a>(path_id, \*\*<a href="src/scalekit_demo/types/api/v1/environment_dns_verify_params.py">params</a>) -> None</code>
- <code title="post /api/v1/environments/{id}/saml-certificates:generate">client.api.v1.environments.<a href="./src/scalekit_demo/resources/api/v1/environments/environments.py">saml_certificates_generate</a>(path_id, \*\*<a href="src/scalekit_demo/types/api/v1/environment_saml_certificates_generate_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/environment_saml_certificates_generate_response.py">EnvironmentSAMLCertificatesGenerateResponse</a></code>
- <code title="put /api/v1/environments/{id}/customizations">client.api.v1.environments.<a href="./src/scalekit_demo/resources/api/v1/environments/environments.py">update_customizations</a>(id, \*\*<a href="src/scalekit_demo/types/api/v1/environment_update_customizations_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/update_portal_customization_response.py">UpdatePortalCustomizationResponse</a></code>
- <code title="patch /api/v1/environments/{id}:update">client.api.v1.environments.<a href="./src/scalekit_demo/resources/api/v1/environments/environments.py">update_id_update</a>(id, \*\*<a href="src/scalekit_demo/types/api/v1/environment_update_id_update_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/update_environment_response.py">UpdateEnvironmentResponse</a></code>

#### PortalCustomizations

Types:

```python
from scalekit_demo.types.api.v1.environments import GetPortalCustomizationResponse
```

Methods:

- <code title="put /api/v1/environments/{id}/portal_customizations">client.api.v1.environments.portal_customizations.<a href="./src/scalekit_demo/resources/api/v1/environments/portal_customizations.py">create</a>(id, \*\*<a href="src/scalekit_demo/types/api/v1/environments/portal_customization_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/update_portal_customization_response.py">UpdatePortalCustomizationResponse</a></code>
- <code title="get /api/v1/environments/{id}/portal_customizations">client.api.v1.environments.portal_customizations.<a href="./src/scalekit_demo/resources/api/v1/environments/portal_customizations.py">list</a>(id) -> <a href="./src/scalekit_demo/types/api/v1/environments/get_portal_customization_response.py">GetPortalCustomizationResponse</a></code>

#### SessionsMe

Types:

```python
from scalekit_demo.types.api.v1.environments import GetCurrentSessionResponse
```

Methods:

- <code title="get /api/v1/environments/{id}/sessions:me">client.api.v1.environments.sessions_me.<a href="./src/scalekit_demo/resources/api/v1/environments/sessions_me.py">retrieve_sessions_me</a>(id) -> <a href="./src/scalekit_demo/types/api/v1/environments/get_current_session_response.py">GetCurrentSessionResponse</a></code>

#### Scopes

Types:

```python
from scalekit_demo.types.api.v1.environments import (
    CreateScope,
    CreateScopeResponse,
    ListScopesResponse,
    Scope,
)
```

Methods:

- <code title="post /api/v1/environments/{env_id}/scopes">client.api.v1.environments.scopes.<a href="./src/scalekit_demo/resources/api/v1/environments/scopes.py">create</a>(env_id, \*\*<a href="src/scalekit_demo/types/api/v1/environments/scope_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/environments/create_scope_response.py">CreateScopeResponse</a></code>
- <code title="get /api/v1/environments/{env_id}/scopes">client.api.v1.environments.scopes.<a href="./src/scalekit_demo/resources/api/v1/environments/scopes.py">list</a>(env_id) -> <a href="./src/scalekit_demo/types/api/v1/environments/list_scopes_response.py">ListScopesResponse</a></code>

#### Contexts

Types:

```python
from scalekit_demo.types.api.v1.environments import ContextListResponse
```

Methods:

- <code title="put /api/v1/environments/{environment_id}/contexts">client.api.v1.environments.contexts.<a href="./src/scalekit_demo/resources/api/v1/environments/contexts.py">create</a>(environment_id, \*\*<a href="src/scalekit_demo/types/api/v1/environments/context_create_params.py">params</a>) -> None</code>
- <code title="get /api/v1/environments/{environment_id}/contexts">client.api.v1.environments.contexts.<a href="./src/scalekit_demo/resources/api/v1/environments/contexts.py">list</a>(environment_id) -> <a href="./src/scalekit_demo/types/api/v1/environments/context_list_response.py">ContextListResponse</a></code>

#### Features

Types:

```python
from scalekit_demo.types.api.v1.environments import EnvironmentFeature, GetFeaturesResponse
```

Methods:

- <code title="put /api/v1/environments/{id}/features">client.api.v1.environments.features.<a href="./src/scalekit_demo/resources/api/v1/environments/features/features.py">create</a>(id, \*\*<a href="src/scalekit_demo/types/api/v1/environments/feature_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/environments/get_features_response.py">GetFeaturesResponse</a></code>
- <code title="get /api/v1/environments/{id}/features">client.api.v1.environments.features.<a href="./src/scalekit_demo/resources/api/v1/environments/features/features.py">list</a>(id) -> <a href="./src/scalekit_demo/types/api/v1/environments/get_features_response.py">GetFeaturesResponse</a></code>
- <code title="post /api/v1/environments/{id}/features/{feature_id}:disable">client.api.v1.environments.features.<a href="./src/scalekit_demo/resources/api/v1/environments/features/features.py">feature_id_disable</a>(feature_id, \*, id) -> None</code>
- <code title="post /api/v1/environments/{id}/features/{feature_id}:enable">client.api.v1.environments.features.<a href="./src/scalekit_demo/resources/api/v1/environments/features/features.py">feature_id_enable</a>(feature_id, \*, id) -> None</code>

##### Fsa

Methods:

- <code title="post /api/v1/environments/{id}/features/fsa/enable">client.api.v1.environments.features.fsa.<a href="./src/scalekit_demo/resources/api/v1/environments/features/fsa.py">enable</a>(path_id, \*\*<a href="src/scalekit_demo/types/api/v1/environments/features/fsa_enable_params.py">params</a>) -> None</code>

#### SessionSettings

Types:

```python
from scalekit_demo.types.api.v1.environments import (
    SessionSettings,
    SessionSettingRetrieveSessionSettingsResponse,
    SessionSettingSessionSettingsResponse,
    SessionSettingUpdateSessionSettingsResponse,
)
```

Methods:

- <code title="get /api/v1/environments/{id}/session-settings">client.api.v1.environments.session_settings.<a href="./src/scalekit_demo/resources/api/v1/environments/session_settings.py">retrieve_session_settings</a>(id) -> <a href="./src/scalekit_demo/types/api/v1/environments/session_setting_retrieve_session_settings_response.py">SessionSettingRetrieveSessionSettingsResponse</a></code>
- <code title="post /api/v1/environments/{id}/session-settings">client.api.v1.environments.session_settings.<a href="./src/scalekit_demo/resources/api/v1/environments/session_settings.py">session_settings</a>(id, \*\*<a href="src/scalekit_demo/types/api/v1/environments/session_setting_session_settings_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/environments/session_setting_session_settings_response.py">SessionSettingSessionSettingsResponse</a></code>
- <code title="patch /api/v1/environments/{id}/session-settings">client.api.v1.environments.session_settings.<a href="./src/scalekit_demo/resources/api/v1/environments/session_settings.py">update_session_settings</a>(id, \*\*<a href="src/scalekit_demo/types/api/v1/environments/session_setting_update_session_settings_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/environments/session_setting_update_session_settings_response.py">SessionSettingUpdateSessionSettingsResponse</a></code>

#### Settings

##### UserManagement

Types:

```python
from scalekit_demo.types.api.v1.environments.settings import (
    UserManagement,
    UserManagementRetrieveUserManagementResponse,
    UserManagementUpdateUserManagementResponse,
    UserManagementUserManagementResponse,
)
```

Methods:

- <code title="get /api/v1/environments/{id}/settings/user-management">client.api.v1.environments.settings.user_management.<a href="./src/scalekit_demo/resources/api/v1/environments/settings/user_management.py">retrieve_user_management</a>(id) -> <a href="./src/scalekit_demo/types/api/v1/environments/settings/user_management_retrieve_user_management_response.py">UserManagementRetrieveUserManagementResponse</a></code>
- <code title="patch /api/v1/environments/{id}/settings/user-management">client.api.v1.environments.settings.user_management.<a href="./src/scalekit_demo/resources/api/v1/environments/settings/user_management.py">update_user_management</a>(id, \*\*<a href="src/scalekit_demo/types/api/v1/environments/settings/user_management_update_user_management_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/environments/settings/user_management_update_user_management_response.py">UserManagementUpdateUserManagementResponse</a></code>
- <code title="post /api/v1/environments/{id}/settings/user-management">client.api.v1.environments.settings.user_management.<a href="./src/scalekit_demo/resources/api/v1/environments/settings/user_management.py">user_management</a>(id, \*\*<a href="src/scalekit_demo/types/api/v1/environments/settings/user_management_user_management_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/environments/settings/user_management_user_management_response.py">UserManagementUserManagementResponse</a></code>

### Events

Types:

```python
from scalekit_demo.types.api.v1 import EventCreateResponse, EventUpdateResponse
```

Methods:

- <code title="post /api/v1/events">client.api.v1.events.<a href="./src/scalekit_demo/resources/api/v1/events.py">create</a>(\*\*<a href="src/scalekit_demo/types/api/v1/event_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/event_create_response.py">EventCreateResponse</a></code>
- <code title="post /api/v1/events/frontend_events/{event_type}">client.api.v1.events.<a href="./src/scalekit_demo/resources/api/v1/events.py">update</a>(event_type, \*\*<a href="src/scalekit_demo/types/api/v1/event_update_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/event_update_response.py">EventUpdateResponse</a></code>

### Features

#### Fsa

Methods:

- <code title="post /api/v1/features/fsa/disable">client.api.v1.features.fsa.<a href="./src/scalekit_demo/resources/api/v1/features/fsa.py">disable</a>(\*\*<a href="src/scalekit_demo/types/api/v1/features/fsa_disable_params.py">params</a>) -> None</code>
- <code title="post /api/v1/features/fsa/enable">client.api.v1.features.fsa.<a href="./src/scalekit_demo/resources/api/v1/features/fsa.py">enable</a>(\*\*<a href="src/scalekit_demo/types/api/v1/features/fsa_enable_params.py">params</a>) -> None</code>

### Invites

#### Organizations

##### Users

Types:

```python
from scalekit_demo.types.api.v1.invites.organizations import UserUpdateResendResponse
```

Methods:

- <code title="patch /api/v1/invites/organizations/{organization_id}/users/{id}/resend">client.api.v1.invites.organizations.users.<a href="./src/scalekit_demo/resources/api/v1/invites/organizations/users.py">update_resend</a>(path_id, \*, path_organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/invites/organizations/user_update_resend_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/invites/organizations/user_update_resend_response.py">UserUpdateResendResponse</a></code>

### Logs

#### Authentication

Types:

```python
from scalekit_demo.types.api.v1.logs import AuthenticationRetrieveRequestsResponse
```

Methods:

- <code title="get /api/v1/logs/authentication/requests">client.api.v1.logs.authentication.<a href="./src/scalekit_demo/resources/api/v1/logs/authentication.py">retrieve_requests</a>(\*\*<a href="src/scalekit_demo/types/api/v1/logs/authentication_retrieve_requests_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/logs/authentication_retrieve_requests_response.py">AuthenticationRetrieveRequestsResponse</a></code>

### Mcp

Types:

```python
from scalekit_demo.types.api.v1 import Mcp, McpCreateResponse, McpRetrieveResponse, McpListResponse
```

Methods:

- <code title="post /api/v1/mcp">client.api.v1.mcp.<a href="./src/scalekit_demo/resources/api/v1/mcp.py">create</a>(\*\*<a href="src/scalekit_demo/types/api/v1/mcp_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/mcp_create_response.py">McpCreateResponse</a></code>
- <code title="get /api/v1/mcp/{mcp_id}">client.api.v1.mcp.<a href="./src/scalekit_demo/resources/api/v1/mcp.py">retrieve</a>(mcp_id) -> <a href="./src/scalekit_demo/types/api/v1/mcp_retrieve_response.py">McpRetrieveResponse</a></code>
- <code title="get /api/v1/mcp">client.api.v1.mcp.<a href="./src/scalekit_demo/resources/api/v1/mcp.py">list</a>(\*\*<a href="src/scalekit_demo/types/api/v1/mcp_list_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/mcp_list_response.py">McpListResponse</a></code>
- <code title="delete /api/v1/mcp/{mcp_id}">client.api.v1.mcp.<a href="./src/scalekit_demo/resources/api/v1/mcp.py">delete</a>(mcp_id) -> object</code>

### Members

Types:

```python
from scalekit_demo.types.api.v1 import (
    GetMemberResponse,
    Member,
    UpdateMember,
    UpdateMemberResponse,
    UpdateUserProfile,
    MemberCreateResponse,
    MemberListResponse,
)
```

Methods:

- <code title="post /api/v1/members">client.api.v1.members.<a href="./src/scalekit_demo/resources/api/v1/members.py">create</a>(\*\*<a href="src/scalekit_demo/types/api/v1/member_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/member_create_response.py">MemberCreateResponse</a></code>
- <code title="get /api/v1/members/{id}">client.api.v1.members.<a href="./src/scalekit_demo/resources/api/v1/members.py">retrieve</a>(id) -> <a href="./src/scalekit_demo/types/api/v1/get_member_response.py">GetMemberResponse</a></code>
- <code title="patch /api/v1/members/{id}">client.api.v1.members.<a href="./src/scalekit_demo/resources/api/v1/members.py">update</a>(id, \*\*<a href="src/scalekit_demo/types/api/v1/member_update_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/update_member_response.py">UpdateMemberResponse</a></code>
- <code title="get /api/v1/members">client.api.v1.members.<a href="./src/scalekit_demo/resources/api/v1/members.py">list</a>(\*\*<a href="src/scalekit_demo/types/api/v1/member_list_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/member_list_response.py">MemberListResponse</a></code>
- <code title="delete /api/v1/members/{id}">client.api.v1.members.<a href="./src/scalekit_demo/resources/api/v1/members.py">delete</a>(id) -> None</code>

### MembersThis

Methods:

- <code title="get /api/v1/members:this">client.api.v1.members_this.<a href="./src/scalekit_demo/resources/api/v1/members_this.py">retrieve_members_this</a>() -> <a href="./src/scalekit_demo/types/api/v1/get_member_response.py">GetMemberResponse</a></code>
- <code title="patch /api/v1/members:this">client.api.v1.members_this.<a href="./src/scalekit_demo/resources/api/v1/members_this.py">update_members_this</a>(\*\*<a href="src/scalekit_demo/types/api/v1/members_this_update_members_this_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/update_member_response.py">UpdateMemberResponse</a></code>

### Memberships

#### Organizations

##### Users

Types:

```python
from scalekit_demo.types.api.v1.memberships.organizations import (
    CreateMembership,
    UserUpdateResponse,
)
```

Methods:

- <code title="patch /api/v1/memberships/organizations/{organization_id}/users/{id}">client.api.v1.memberships.organizations.users.<a href="./src/scalekit_demo/resources/api/v1/memberships/organizations/users.py">update</a>(id, \*, organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/memberships/organizations/user_update_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/memberships/organizations/user_update_response.py">UserUpdateResponse</a></code>
- <code title="delete /api/v1/memberships/organizations/{organization_id}/users/{id}">client.api.v1.memberships.organizations.users.<a href="./src/scalekit_demo/resources/api/v1/memberships/organizations/users.py">delete</a>(id, \*, organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/memberships/organizations/user_delete_params.py">params</a>) -> None</code>

### OAuth

#### Consent

Types:

```python
from scalekit_demo.types.api.v1.oauth import Resource, ConsentRetrieveDetailsResponse
```

Methods:

- <code title="get /api/v1/oauth/consent/details">client.api.v1.oauth.consent.<a href="./src/scalekit_demo/resources/api/v1/oauth/consent.py">retrieve_details</a>() -> <a href="./src/scalekit_demo/types/api/v1/oauth/consent_retrieve_details_response.py">ConsentRetrieveDetailsResponse</a></code>

### Organizations

Types:

```python
from scalekit_demo.types.api.v1 import (
    GetOrganizationResponse,
    Organization,
    OrganizationCreateResponse,
    OrganizationUpdateResponse,
    OrganizationListResponse,
    OrganizationRetrieveConnectionsSearchResponse,
    OrganizationRetrieveUsersSearchResponse,
    OrganizationUpdateRolesSetDefaultsResponse,
)
```

Methods:

- <code title="post /api/v1/organizations">client.api.v1.organizations.<a href="./src/scalekit_demo/resources/api/v1/organizations/organizations.py">create</a>(\*\*<a href="src/scalekit_demo/types/api/v1/organization_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organization_create_response.py">OrganizationCreateResponse</a></code>
- <code title="get /api/v1/organizations/{id}">client.api.v1.organizations.<a href="./src/scalekit_demo/resources/api/v1/organizations/organizations.py">retrieve</a>(id, \*\*<a href="src/scalekit_demo/types/api/v1/organization_retrieve_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/get_organization_response.py">GetOrganizationResponse</a></code>
- <code title="patch /api/v1/organizations/{id}">client.api.v1.organizations.<a href="./src/scalekit_demo/resources/api/v1/organizations/organizations.py">update</a>(id, \*\*<a href="src/scalekit_demo/types/api/v1/organization_update_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organization_update_response.py">OrganizationUpdateResponse</a></code>
- <code title="get /api/v1/organizations">client.api.v1.organizations.<a href="./src/scalekit_demo/resources/api/v1/organizations/organizations.py">list</a>(\*\*<a href="src/scalekit_demo/types/api/v1/organization_list_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organization_list_response.py">OrganizationListResponse</a></code>
- <code title="delete /api/v1/organizations/{id}">client.api.v1.organizations.<a href="./src/scalekit_demo/resources/api/v1/organizations/organizations.py">delete</a>(id, \*\*<a href="src/scalekit_demo/types/api/v1/organization_delete_params.py">params</a>) -> None</code>
- <code title="get /api/v1/organizations/-/connections:search">client.api.v1.organizations.<a href="./src/scalekit_demo/resources/api/v1/organizations/organizations.py">retrieve_connections_search</a>(\*\*<a href="src/scalekit_demo/types/api/v1/organization_retrieve_connections_search_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organization_retrieve_connections_search_response.py">OrganizationRetrieveConnectionsSearchResponse</a></code>
- <code title="get /api/v1/organizations/{organization_id}/users:search">client.api.v1.organizations.<a href="./src/scalekit_demo/resources/api/v1/organizations/organizations.py">retrieve_users_search</a>(organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/organization_retrieve_users_search_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organization_retrieve_users_search_response.py">OrganizationRetrieveUsersSearchResponse</a></code>
- <code title="patch /api/v1/organizations/{org_id}/roles:set_defaults">client.api.v1.organizations.<a href="./src/scalekit_demo/resources/api/v1/organizations/organizations.py">update_roles_set_defaults</a>(path_org_id, \*\*<a href="src/scalekit_demo/types/api/v1/organization_update_roles_set_defaults_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organization_update_roles_set_defaults_response.py">OrganizationUpdateRolesSetDefaultsResponse</a></code>

#### Connections

Types:

```python
from scalekit_demo.types.api.v1.organizations import (
    ConnectionListResponse,
    ConnectionUpdateDomainsResponse,
)
```

Methods:

- <code title="post /api/v1/organizations/{organization_id}/connections">client.api.v1.organizations.connections.<a href="./src/scalekit_demo/resources/api/v1/organizations/connections.py">create</a>(organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/connection_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/create_connection_response.py">CreateConnectionResponse</a></code>
- <code title="get /api/v1/organizations/{organization_id}/connections/{id}">client.api.v1.organizations.connections.<a href="./src/scalekit_demo/resources/api/v1/organizations/connections.py">retrieve</a>(id, \*, organization_id) -> <a href="./src/scalekit_demo/types/api/v1/get_connection_response.py">GetConnectionResponse</a></code>
- <code title="patch /api/v1/organizations/{organization_id}/connections/{id}">client.api.v1.organizations.connections.<a href="./src/scalekit_demo/resources/api/v1/organizations/connections.py">update</a>(id, \*, organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/connection_update_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/update_connection_response.py">UpdateConnectionResponse</a></code>
- <code title="get /api/v1/organizations/-/connections">client.api.v1.organizations.connections.<a href="./src/scalekit_demo/resources/api/v1/organizations/connections.py">list</a>(\*\*<a href="src/scalekit_demo/types/api/v1/organizations/connection_list_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/connection_list_response.py">ConnectionListResponse</a></code>
- <code title="delete /api/v1/organizations/{organization_id}/connections/{id}">client.api.v1.organizations.connections.<a href="./src/scalekit_demo/resources/api/v1/organizations/connections.py">delete</a>(id, \*, organization_id) -> None</code>
- <code title="put /api/v1/organizations/{organization_id}/connections/{connection_id}/domains">client.api.v1.organizations.connections.<a href="./src/scalekit_demo/resources/api/v1/organizations/connections.py">update_domains</a>(path_connection_id, \*, path_organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/connection_update_domains_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/connection_update_domains_response.py">ConnectionUpdateDomainsResponse</a></code>
- <code title="patch /api/v1/organizations/{organization_id}/connections/{id}:disable">client.api.v1.organizations.connections.<a href="./src/scalekit_demo/resources/api/v1/organizations/connections.py">update_id_disable</a>(id, \*, organization_id) -> <a href="./src/scalekit_demo/types/api/v1/toggle_connection_response.py">ToggleConnectionResponse</a></code>
- <code title="patch /api/v1/organizations/{organization_id}/connections/{id}:enable">client.api.v1.organizations.connections.<a href="./src/scalekit_demo/resources/api/v1/organizations/connections.py">update_id_enable</a>(id, \*, organization_id) -> <a href="./src/scalekit_demo/types/api/v1/toggle_connection_response.py">ToggleConnectionResponse</a></code>

#### Email

##### Templates

Types:

```python
from scalekit_demo.types.api.v1.organizations.email import (
    CreateEmailTemplate,
    CreateEmailTemplateResponse,
    GetEmailTemplateResponse,
    ListEmailTemplateResponse,
    Template,
    UpdateTemplate,
)
```

Methods:

- <code title="post /api/v1/organizations/{organization_id}/email/templates">client.api.v1.organizations.email.templates.<a href="./src/scalekit_demo/resources/api/v1/organizations/email/templates/templates.py">create</a>(organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/email/template_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/email/create_email_template_response.py">CreateEmailTemplateResponse</a></code>
- <code title="get /api/v1/organizations/{organization_id}/email/templates/{template_id}">client.api.v1.organizations.email.templates.<a href="./src/scalekit_demo/resources/api/v1/organizations/email/templates/templates.py">retrieve</a>(template_id, \*, organization_id) -> <a href="./src/scalekit_demo/types/api/v1/organizations/email/get_email_template_response.py">GetEmailTemplateResponse</a></code>
- <code title="patch /api/v1/organizations/{organization_id}/email/templates/{template_id}">client.api.v1.organizations.email.templates.<a href="./src/scalekit_demo/resources/api/v1/organizations/email/templates/templates.py">update</a>(template_id, \*, organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/email/template_update_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/email/get_email_template_response.py">GetEmailTemplateResponse</a></code>
- <code title="get /api/v1/organizations/{organization_id}/email/templates">client.api.v1.organizations.email.templates.<a href="./src/scalekit_demo/resources/api/v1/organizations/email/templates/templates.py">list</a>(organization_id) -> <a href="./src/scalekit_demo/types/api/v1/organizations/email/list_email_template_response.py">ListEmailTemplateResponse</a></code>
- <code title="delete /api/v1/organizations/{organization_id}/email/templates/{template_id}">client.api.v1.organizations.email.templates.<a href="./src/scalekit_demo/resources/api/v1/organizations/email/templates/templates.py">delete</a>(template_id, \*, organization_id) -> None</code>

###### Disable

Methods:

- <code title="patch /api/v1/organizations/{organization_id}/email/templates/{template_id}:disable">client.api.v1.organizations.email.templates.disable.<a href="./src/scalekit_demo/resources/api/v1/organizations/email/templates/disable.py">update_template_id_disable</a>(template_id, \*, organization_id) -> None</code>

###### Enable

Types:

```python
from scalekit_demo.types.api.v1.organizations.email.templates import EnableEmailTemplateResponse
```

Methods:

- <code title="patch /api/v1/organizations/{organization_id}/email/templates/{template_id}:enable">client.api.v1.organizations.email.templates.enable.<a href="./src/scalekit_demo/resources/api/v1/organizations/email/templates/enable.py">update_template_id_enable</a>(template_id, \*, organization_id) -> <a href="./src/scalekit_demo/types/api/v1/organizations/email/templates/enable_email_template_response.py">EnableEmailTemplateResponse</a></code>

#### PortalLinks

Types:

```python
from scalekit_demo.types.api.v1.organizations import (
    Link,
    PortalLinkCreateResponse,
    PortalLinkListResponse,
)
```

Methods:

- <code title="put /api/v1/organizations/{id}/portal_links">client.api.v1.organizations.portal_links.<a href="./src/scalekit_demo/resources/api/v1/organizations/portal_links.py">create</a>(id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/portal_link_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/portal_link_create_response.py">PortalLinkCreateResponse</a></code>
- <code title="get /api/v1/organizations/{id}/portal_links">client.api.v1.organizations.portal_links.<a href="./src/scalekit_demo/resources/api/v1/organizations/portal_links.py">list</a>(id) -> <a href="./src/scalekit_demo/types/api/v1/organizations/portal_link_list_response.py">PortalLinkListResponse</a></code>
- <code title="delete /api/v1/organizations/{id}/portal_links/{link_id}">client.api.v1.organizations.portal_links.<a href="./src/scalekit_demo/resources/api/v1/organizations/portal_links.py">delete</a>(link_id, \*, id) -> None</code>
- <code title="delete /api/v1/organizations/{id}/portal_links">client.api.v1.organizations.portal_links.<a href="./src/scalekit_demo/resources/api/v1/organizations/portal_links.py">delete_all</a>(id) -> None</code>

#### SessionSettings

Types:

```python
from scalekit_demo.types.api.v1.organizations import (
    OrganizationSessionSettings,
    SessionSettingRetrieveSessionSettingsResponse,
    SessionSettingSessionSettingsResponse,
    SessionSettingUpdateSessionSettingsResponse,
)
```

Methods:

- <code title="delete /api/v1/organizations/{id}/session-settings">client.api.v1.organizations.session_settings.<a href="./src/scalekit_demo/resources/api/v1/organizations/session_settings.py">delete_session_settings</a>(id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/session_setting_delete_session_settings_params.py">params</a>) -> None</code>
- <code title="get /api/v1/organizations/{id}/session-settings">client.api.v1.organizations.session_settings.<a href="./src/scalekit_demo/resources/api/v1/organizations/session_settings.py">retrieve_session_settings</a>(id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/session_setting_retrieve_session_settings_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/session_setting_retrieve_session_settings_response.py">SessionSettingRetrieveSessionSettingsResponse</a></code>
- <code title="post /api/v1/organizations/{id}/session-settings">client.api.v1.organizations.session_settings.<a href="./src/scalekit_demo/resources/api/v1/organizations/session_settings.py">session_settings</a>(id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/session_setting_session_settings_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/session_setting_session_settings_response.py">SessionSettingSessionSettingsResponse</a></code>
- <code title="patch /api/v1/organizations/{id}/session-settings">client.api.v1.organizations.session_settings.<a href="./src/scalekit_demo/resources/api/v1/organizations/session_settings.py">update_session_settings</a>(id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/session_setting_update_session_settings_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/session_setting_update_session_settings_response.py">SessionSettingUpdateSessionSettingsResponse</a></code>

#### Settings

Methods:

- <code title="patch /api/v1/organizations/{id}/settings">client.api.v1.organizations.settings.<a href="./src/scalekit_demo/resources/api/v1/organizations/settings/settings.py">patch_all</a>(id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/setting_patch_all_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/get_organization_response.py">GetOrganizationResponse</a></code>

##### Usermanagement

Types:

```python
from scalekit_demo.types.api.v1.organizations.settings import (
    OrganizationUserManagementSettings,
    UsermanagementListResponse,
    UsermanagementPatchAllResponse,
)
```

Methods:

- <code title="get /api/v1/organizations/{organization_id}/settings/usermanagement">client.api.v1.organizations.settings.usermanagement.<a href="./src/scalekit_demo/resources/api/v1/organizations/settings/usermanagement.py">list</a>(organization_id) -> <a href="./src/scalekit_demo/types/api/v1/organizations/settings/usermanagement_list_response.py">UsermanagementListResponse</a></code>
- <code title="patch /api/v1/organizations/{organization_id}/settings/usermanagement">client.api.v1.organizations.settings.usermanagement.<a href="./src/scalekit_demo/resources/api/v1/organizations/settings/usermanagement.py">patch_all</a>(path_organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/settings/usermanagement_patch_all_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/settings/usermanagement_patch_all_response.py">UsermanagementPatchAllResponse</a></code>

#### Roles

Types:

```python
from scalekit_demo.types.api.v1.organizations import (
    Role,
    UpdateRole,
    RoleCreateResponse,
    RoleRetrieveResponse,
    RoleUpdateResponse,
    RoleListResponse,
    RoleRetrieveUsersCountResponse,
)
```

Methods:

- <code title="post /api/v1/organizations/{org_id}/roles">client.api.v1.organizations.roles.<a href="./src/scalekit_demo/resources/api/v1/organizations/roles.py">create</a>(org_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/role_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/role_create_response.py">RoleCreateResponse</a></code>
- <code title="get /api/v1/organizations/{org_id}/roles/{role_name}">client.api.v1.organizations.roles.<a href="./src/scalekit_demo/resources/api/v1/organizations/roles.py">retrieve</a>(role_name, \*, org_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/role_retrieve_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/role_retrieve_response.py">RoleRetrieveResponse</a></code>
- <code title="put /api/v1/organizations/{org_id}/roles/{role_name}">client.api.v1.organizations.roles.<a href="./src/scalekit_demo/resources/api/v1/organizations/roles.py">update</a>(role_name, \*, org_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/role_update_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/role_update_response.py">RoleUpdateResponse</a></code>
- <code title="get /api/v1/organizations/{org_id}/roles">client.api.v1.organizations.roles.<a href="./src/scalekit_demo/resources/api/v1/organizations/roles.py">list</a>(org_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/role_list_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/role_list_response.py">RoleListResponse</a></code>
- <code title="delete /api/v1/organizations/{org_id}/roles/{role_name}">client.api.v1.organizations.roles.<a href="./src/scalekit_demo/resources/api/v1/organizations/roles.py">delete</a>(role_name, \*, org_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/role_delete_params.py">params</a>) -> None</code>
- <code title="delete /api/v1/organizations/{org_id}/roles/{role_name}/base">client.api.v1.organizations.roles.<a href="./src/scalekit_demo/resources/api/v1/organizations/roles.py">delete_base</a>(role_name, \*, org_id) -> None</code>
- <code title="get /api/v1/organizations/{org_id}/roles/{role_name}/users:count">client.api.v1.organizations.roles.<a href="./src/scalekit_demo/resources/api/v1/organizations/roles.py">retrieve_users_count</a>(role_name, \*, org_id) -> <a href="./src/scalekit_demo/types/api/v1/organizations/role_retrieve_users_count_response.py">RoleRetrieveUsersCountResponse</a></code>

#### Clients

Types:

```python
from scalekit_demo.types.api.v1.organizations import (
    CustomClaim,
    M2MClient,
    OrganizationClient,
    ClientCreateResponse,
    ClientRetrieveResponse,
    ClientUpdateResponse,
    ClientListResponse,
)
```

Methods:

- <code title="post /api/v1/organizations/{organization_id}/clients">client.api.v1.organizations.clients.<a href="./src/scalekit_demo/resources/api/v1/organizations/clients/clients.py">create</a>(organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/client_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/client_create_response.py">ClientCreateResponse</a></code>
- <code title="get /api/v1/organizations/{organization_id}/clients/{client_id}">client.api.v1.organizations.clients.<a href="./src/scalekit_demo/resources/api/v1/organizations/clients/clients.py">retrieve</a>(client_id, \*, organization_id) -> <a href="./src/scalekit_demo/types/api/v1/organizations/client_retrieve_response.py">ClientRetrieveResponse</a></code>
- <code title="patch /api/v1/organizations/{organization_id}/clients/{client_id}">client.api.v1.organizations.clients.<a href="./src/scalekit_demo/resources/api/v1/organizations/clients/clients.py">update</a>(client_id, \*, organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/client_update_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/client_update_response.py">ClientUpdateResponse</a></code>
- <code title="get /api/v1/organizations/{organization_id}/clients">client.api.v1.organizations.clients.<a href="./src/scalekit_demo/resources/api/v1/organizations/clients/clients.py">list</a>(organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/client_list_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/client_list_response.py">ClientListResponse</a></code>
- <code title="delete /api/v1/organizations/{organization_id}/clients/{client_id}">client.api.v1.organizations.clients.<a href="./src/scalekit_demo/resources/api/v1/organizations/clients/clients.py">delete</a>(client_id, \*, organization_id) -> None</code>

##### Secrets

Types:

```python
from scalekit_demo.types.api.v1.organizations.clients import ClientSecret, SecretCreateResponse
```

Methods:

- <code title="post /api/v1/organizations/{organization_id}/clients/{client_id}/secrets">client.api.v1.organizations.clients.secrets.<a href="./src/scalekit_demo/resources/api/v1/organizations/clients/secrets.py">create</a>(client_id, \*, organization_id) -> <a href="./src/scalekit_demo/types/api/v1/organizations/clients/secret_create_response.py">SecretCreateResponse</a></code>
- <code title="delete /api/v1/organizations/{organization_id}/clients/{client_id}/secrets/{secret_id}">client.api.v1.organizations.clients.secrets.<a href="./src/scalekit_demo/resources/api/v1/organizations/clients/secrets.py">delete</a>(secret_id, \*, organization_id, client_id) -> None</code>

#### Directories

Types:

```python
from scalekit_demo.types.api.v1.organizations import (
    AttributeMappings,
    Directory,
    Secret,
    ToggleDirectoryResponse,
    DirectoryCreateResponse,
    DirectoryRetrieveResponse,
    DirectoryUpdateResponse,
    DirectoryListResponse,
    DirectoryRetrieveUsersResponse,
    DirectorySecretsResponse,
    DirectorySecretsRegenerateResponse,
    DirectoryUpdateAttributesResponse,
)
```

Methods:

- <code title="post /api/v1/organizations/{organization_id}/directories">client.api.v1.organizations.directories.<a href="./src/scalekit_demo/resources/api/v1/organizations/directories/directories.py">create</a>(organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/directory_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/directory_create_response.py">DirectoryCreateResponse</a></code>
- <code title="get /api/v1/organizations/{organization_id}/directories/{id}">client.api.v1.organizations.directories.<a href="./src/scalekit_demo/resources/api/v1/organizations/directories/directories.py">retrieve</a>(id, \*, organization_id) -> <a href="./src/scalekit_demo/types/api/v1/organizations/directory_retrieve_response.py">DirectoryRetrieveResponse</a></code>
- <code title="patch /api/v1/organizations/{organization_id}/directories/{id}">client.api.v1.organizations.directories.<a href="./src/scalekit_demo/resources/api/v1/organizations/directories/directories.py">update</a>(id, \*, organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/directory_update_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/directory_update_response.py">DirectoryUpdateResponse</a></code>
- <code title="get /api/v1/organizations/{organization_id}/directories">client.api.v1.organizations.directories.<a href="./src/scalekit_demo/resources/api/v1/organizations/directories/directories.py">list</a>(organization_id) -> <a href="./src/scalekit_demo/types/api/v1/organizations/directory_list_response.py">DirectoryListResponse</a></code>
- <code title="delete /api/v1/organizations/{organization_id}/directories/{id}">client.api.v1.organizations.directories.<a href="./src/scalekit_demo/resources/api/v1/organizations/directories/directories.py">delete</a>(id, \*, organization_id) -> None</code>
- <code title="get /api/v1/organizations/{organization_id}/directories/{directory_id}:sync">client.api.v1.organizations.directories.<a href="./src/scalekit_demo/resources/api/v1/organizations/directories/directories.py">retrieve_directory_id_sync</a>(directory_id, \*, organization_id) -> None</code>
- <code title="get /api/v1/organizations/{organization_id}/directories/{directory_id}/users">client.api.v1.organizations.directories.<a href="./src/scalekit_demo/resources/api/v1/organizations/directories/directories.py">retrieve_users</a>(directory_id, \*, organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/directory_retrieve_users_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/directory_retrieve_users_response.py">DirectoryRetrieveUsersResponse</a></code>
- <code title="post /api/v1/organizations/{organization_id}/directories/{directory_id}/secrets">client.api.v1.organizations.directories.<a href="./src/scalekit_demo/resources/api/v1/organizations/directories/directories.py">secrets</a>(directory_id, \*, organization_id) -> <a href="./src/scalekit_demo/types/api/v1/organizations/directory_secrets_response.py">DirectorySecretsResponse</a></code>
- <code title="post /api/v1/organizations/{organization_id}/directories/{directory_id}/secrets:regenerate">client.api.v1.organizations.directories.<a href="./src/scalekit_demo/resources/api/v1/organizations/directories/directories.py">secrets_regenerate</a>(directory_id, \*, organization_id) -> <a href="./src/scalekit_demo/types/api/v1/organizations/directory_secrets_regenerate_response.py">DirectorySecretsRegenerateResponse</a></code>
- <code title="put /api/v1/organizations/{organization_id}/directories/{id}/attributes">client.api.v1.organizations.directories.<a href="./src/scalekit_demo/resources/api/v1/organizations/directories/directories.py">update_attributes</a>(id, \*, organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/directory_update_attributes_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/directory_update_attributes_response.py">DirectoryUpdateAttributesResponse</a></code>
- <code title="put /api/v1/organizations/{organization_id}/directories/{id}/groups:assign">client.api.v1.organizations.directories.<a href="./src/scalekit_demo/resources/api/v1/organizations/directories/directories.py">update_groups_assign</a>(path_id, \*, path_organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/directory_update_groups_assign_params.py">params</a>) -> None</code>
- <code title="patch /api/v1/organizations/{organization_id}/directories/{id}:disable">client.api.v1.organizations.directories.<a href="./src/scalekit_demo/resources/api/v1/organizations/directories/directories.py">update_id_disable</a>(id, \*, organization_id) -> <a href="./src/scalekit_demo/types/api/v1/organizations/toggle_directory_response.py">ToggleDirectoryResponse</a></code>
- <code title="patch /api/v1/organizations/{organization_id}/directories/{id}:enable">client.api.v1.organizations.directories.<a href="./src/scalekit_demo/resources/api/v1/organizations/directories/directories.py">update_id_enable</a>(id, \*, organization_id) -> <a href="./src/scalekit_demo/types/api/v1/organizations/toggle_directory_response.py">ToggleDirectoryResponse</a></code>

##### Groups

Types:

```python
from scalekit_demo.types.api.v1.organizations.directories import (
    DirectoryGroup,
    ListDirectoryGroupsResponse,
    RoleAssignments,
    GroupUpdateRolesAssignResponse,
)
```

Methods:

- <code title="get /api/v1/organizations/{organization_id}/directories/{directory_id}/groups">client.api.v1.organizations.directories.groups.<a href="./src/scalekit_demo/resources/api/v1/organizations/directories/groups.py">list</a>(directory_id, \*, organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/directories/group_list_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/directories/list_directory_groups_response.py">ListDirectoryGroupsResponse</a></code>
- <code title="get /api/v1/organizations/{organization_id}/directories/{directory_id}/groups/summary">client.api.v1.organizations.directories.groups.<a href="./src/scalekit_demo/resources/api/v1/organizations/directories/groups.py">retrieve_summary</a>(directory_id, \*, organization_id) -> <a href="./src/scalekit_demo/types/api/v1/organizations/directories/list_directory_groups_response.py">ListDirectoryGroupsResponse</a></code>
- <code title="put /api/v1/organizations/{organization_id}/directories/{id}/groups/-/roles:assign">client.api.v1.organizations.directories.groups.<a href="./src/scalekit_demo/resources/api/v1/organizations/directories/groups.py">update_roles_assign</a>(id, \*, organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/directories/group_update_roles_assign_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/directories/group_update_roles_assign_response.py">GroupUpdateRolesAssignResponse</a></code>

#### Domains

Types:

```python
from scalekit_demo.types.api.v1.organizations import (
    Domain,
    DomainCreateResponse,
    DomainRetrieveResponse,
    DomainUpdateResponse,
    DomainListResponse,
    DomainUpdateIDVerifyResponse,
)
```

Methods:

- <code title="post /api/v1/organizations/{organization_id}/domains">client.api.v1.organizations.domains.<a href="./src/scalekit_demo/resources/api/v1/organizations/domains.py">create</a>(organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/domain_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/domain_create_response.py">DomainCreateResponse</a></code>
- <code title="get /api/v1/organizations/{organization_id}/domains/{id}">client.api.v1.organizations.domains.<a href="./src/scalekit_demo/resources/api/v1/organizations/domains.py">retrieve</a>(id, \*, organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/domain_retrieve_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/domain_retrieve_response.py">DomainRetrieveResponse</a></code>
- <code title="patch /api/v1/organizations/{organization_id}/domains/{id}">client.api.v1.organizations.domains.<a href="./src/scalekit_demo/resources/api/v1/organizations/domains.py">update</a>(id, \*, organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/domain_update_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/domain_update_response.py">DomainUpdateResponse</a></code>
- <code title="get /api/v1/organizations/{organization_id}/domains">client.api.v1.organizations.domains.<a href="./src/scalekit_demo/resources/api/v1/organizations/domains.py">list</a>(organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/domain_list_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/domain_list_response.py">DomainListResponse</a></code>
- <code title="delete /api/v1/organizations/{organization_id}/domains/{id}">client.api.v1.organizations.domains.<a href="./src/scalekit_demo/resources/api/v1/organizations/domains.py">delete</a>(id, \*, organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/domain_delete_params.py">params</a>) -> None</code>
- <code title="patch /api/v1/organizations/{organization_id}/domains/{id}:verify">client.api.v1.organizations.domains.<a href="./src/scalekit_demo/resources/api/v1/organizations/domains.py">update_id_verify</a>(id, \*, organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/domain_update_id_verify_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/domain_update_id_verify_response.py">DomainUpdateIDVerifyResponse</a></code>

#### Users

Types:

```python
from scalekit_demo.types.api.v1.organizations import (
    UserCreateResponse,
    UserListResponse,
    UserRetrievePermissionsResponse,
)
```

Methods:

- <code title="post /api/v1/organizations/{organization_id}/users">client.api.v1.organizations.users.<a href="./src/scalekit_demo/resources/api/v1/organizations/users/users.py">create</a>(organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/user_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/user_create_response.py">UserCreateResponse</a></code>
- <code title="get /api/v1/organizations/{organization_id}/users">client.api.v1.organizations.users.<a href="./src/scalekit_demo/resources/api/v1/organizations/users/users.py">list</a>(organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/user_list_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/user_list_response.py">UserListResponse</a></code>
- <code title="get /api/v1/organizations/{organization_id}/users/{user_id}/permissions">client.api.v1.organizations.users.<a href="./src/scalekit_demo/resources/api/v1/organizations/users/users.py">retrieve_permissions</a>(user_id, \*, organization_id) -> <a href="./src/scalekit_demo/types/api/v1/organizations/user_retrieve_permissions_response.py">UserRetrievePermissionsResponse</a></code>

##### Roles

Types:

```python
from scalekit_demo.types.api.v1.organizations.users import RoleCreateResponse, RoleListResponse
```

Methods:

- <code title="post /api/v1/organizations/{organization_id}/users/{user_id}/roles">client.api.v1.organizations.users.roles.<a href="./src/scalekit_demo/resources/api/v1/organizations/users/roles.py">create</a>(user_id, \*, organization_id, \*\*<a href="src/scalekit_demo/types/api/v1/organizations/users/role_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/organizations/users/role_create_response.py">RoleCreateResponse</a></code>
- <code title="get /api/v1/organizations/{organization_id}/users/{user_id}/roles">client.api.v1.organizations.users.roles.<a href="./src/scalekit_demo/resources/api/v1/organizations/users/roles.py">list</a>(user_id, \*, organization_id) -> <a href="./src/scalekit_demo/types/api/v1/organizations/users/role_list_response.py">RoleListResponse</a></code>
- <code title="delete /api/v1/organizations/{organization_id}/users/{user_id}/roles/{role_name}">client.api.v1.organizations.users.roles.<a href="./src/scalekit_demo/resources/api/v1/organizations/users/roles.py">delete</a>(role_name, \*, organization_id, user_id) -> None</code>

### Passwordless

#### Email

Types:

```python
from scalekit_demo.types.api.v1.passwordless import SendPasswordlessResponse
```

Methods:

- <code title="post /api/v1/passwordless/email/resend">client.api.v1.passwordless.email.<a href="./src/scalekit_demo/resources/api/v1/passwordless/email.py">resend</a>(\*\*<a href="src/scalekit_demo/types/api/v1/passwordless/email_resend_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/passwordless/send_passwordless_response.py">SendPasswordlessResponse</a></code>
- <code title="post /api/v1/passwordless/email/send">client.api.v1.passwordless.email.<a href="./src/scalekit_demo/resources/api/v1/passwordless/email.py">send</a>(\*\*<a href="src/scalekit_demo/types/api/v1/passwordless/email_send_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/passwordless/send_passwordless_response.py">SendPasswordlessResponse</a></code>
- <code title="post /api/v1/passwordless/email/verify">client.api.v1.passwordless.email.<a href="./src/scalekit_demo/resources/api/v1/passwordless/email.py">verify</a>(\*\*<a href="src/scalekit_demo/types/api/v1/passwordless/email_verify_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/verify_password_less_response.py">object</a></code>

### Permissions

Types:

```python
from scalekit_demo.types.api.v1 import (
    CreatePermission,
    Permission,
    PermissionCreateResponse,
    PermissionRetrieveResponse,
    PermissionUpdateResponse,
    PermissionListResponse,
)
```

Methods:

- <code title="post /api/v1/permissions">client.api.v1.permissions.<a href="./src/scalekit_demo/resources/api/v1/permissions.py">create</a>(\*\*<a href="src/scalekit_demo/types/api/v1/permission_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/permission_create_response.py">PermissionCreateResponse</a></code>
- <code title="get /api/v1/permissions/{permission_name}">client.api.v1.permissions.<a href="./src/scalekit_demo/resources/api/v1/permissions.py">retrieve</a>(permission_name) -> <a href="./src/scalekit_demo/types/api/v1/permission_retrieve_response.py">PermissionRetrieveResponse</a></code>
- <code title="put /api/v1/permissions/{permission_name}">client.api.v1.permissions.<a href="./src/scalekit_demo/resources/api/v1/permissions.py">update</a>(permission_name, \*\*<a href="src/scalekit_demo/types/api/v1/permission_update_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/permission_update_response.py">PermissionUpdateResponse</a></code>
- <code title="get /api/v1/permissions">client.api.v1.permissions.<a href="./src/scalekit_demo/resources/api/v1/permissions.py">list</a>(\*\*<a href="src/scalekit_demo/types/api/v1/permission_list_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/permission_list_response.py">PermissionListResponse</a></code>
- <code title="delete /api/v1/permissions/{permission_name}">client.api.v1.permissions.<a href="./src/scalekit_demo/resources/api/v1/permissions.py">delete</a>(permission_name) -> None</code>

### Providers

Types:

```python
from scalekit_demo.types.api.v1 import (
    ListValue,
    Provider,
    ProviderCreateResponse,
    ProviderUpdateResponse,
    ProviderListResponse,
)
```

Methods:

- <code title="post /api/v1/providers">client.api.v1.providers.<a href="./src/scalekit_demo/resources/api/v1/providers.py">create</a>(\*\*<a href="src/scalekit_demo/types/api/v1/provider_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/provider_create_response.py">ProviderCreateResponse</a></code>
- <code title="put /api/v1/providers/{identifier}">client.api.v1.providers.<a href="./src/scalekit_demo/resources/api/v1/providers.py">update</a>(identifier, \*\*<a href="src/scalekit_demo/types/api/v1/provider_update_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/provider_update_response.py">ProviderUpdateResponse</a></code>
- <code title="get /api/v1/providers">client.api.v1.providers.<a href="./src/scalekit_demo/resources/api/v1/providers.py">list</a>(\*\*<a href="src/scalekit_demo/types/api/v1/provider_list_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/provider_list_response.py">ProviderListResponse</a></code>
- <code title="delete /api/v1/providers/{identifier}">client.api.v1.providers.<a href="./src/scalekit_demo/resources/api/v1/providers.py">delete</a>(identifier) -> object</code>

### Resources

Types:

```python
from scalekit_demo.types.api.v1 import (
    GetResourceResponse,
    ResourceCreateResponse,
    ResourceUpdateResponse,
    ResourceListResponse,
    ResourceClientsRegisterResponse,
)
```

Methods:

- <code title="post /api/v1/resources">client.api.v1.resources.<a href="./src/scalekit_demo/resources/api/v1/resources/resources.py">create</a>(\*\*<a href="src/scalekit_demo/types/api/v1/resource_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/resource_create_response.py">ResourceCreateResponse</a></code>
- <code title="get /api/v1/resources/{resource_id}">client.api.v1.resources.<a href="./src/scalekit_demo/resources/api/v1/resources/resources.py">retrieve</a>(resource_id) -> <a href="./src/scalekit_demo/types/api/v1/get_resource_response.py">GetResourceResponse</a></code>
- <code title="patch /api/v1/resources/{resource_id}">client.api.v1.resources.<a href="./src/scalekit_demo/resources/api/v1/resources/resources.py">update</a>(path_resource_id, \*\*<a href="src/scalekit_demo/types/api/v1/resource_update_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/resource_update_response.py">ResourceUpdateResponse</a></code>
- <code title="get /api/v1/resources">client.api.v1.resources.<a href="./src/scalekit_demo/resources/api/v1/resources/resources.py">list</a>(\*\*<a href="src/scalekit_demo/types/api/v1/resource_list_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/resource_list_response.py">ResourceListResponse</a></code>
- <code title="delete /api/v1/resources/{resource_id}">client.api.v1.resources.<a href="./src/scalekit_demo/resources/api/v1/resources/resources.py">delete</a>(resource_id) -> None</code>
- <code title="post /api/v1/resources/{res_id}/clients:register">client.api.v1.resources.<a href="./src/scalekit_demo/resources/api/v1/resources/resources.py">clients_register</a>(res_id, \*\*<a href="src/scalekit_demo/types/api/v1/resource_clients_register_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/resource_clients_register_response.py">ResourceClientsRegisterResponse</a></code>
- <code title="put /api/v1/resources/{resource_id}/provider:delete">client.api.v1.resources.<a href="./src/scalekit_demo/resources/api/v1/resources/resources.py">update_provider_delete</a>(resource_id) -> <a href="./src/scalekit_demo/types/api/v1/get_resource_response.py">GetResourceResponse</a></code>

#### Clients

Types:

```python
from scalekit_demo.types.api.v1.resources import ClientCreateResponse, ClientRetrieveResponse
```

Methods:

- <code title="post /api/v1/resources/{resource_id}/clients">client.api.v1.resources.clients.<a href="./src/scalekit_demo/resources/api/v1/resources/clients.py">create</a>(resource_id, \*\*<a href="src/scalekit_demo/types/api/v1/resources/client_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/resources/client_create_response.py">ClientCreateResponse</a></code>
- <code title="get /api/v1/resources/{resource_id}/clients/{client_id}">client.api.v1.resources.clients.<a href="./src/scalekit_demo/resources/api/v1/resources/clients.py">retrieve</a>(client_id, \*, resource_id) -> <a href="./src/scalekit_demo/types/api/v1/resources/client_retrieve_response.py">ClientRetrieveResponse</a></code>

### Roles

Types:

```python
from scalekit_demo.types.api.v1 import (
    UpdateDefaultRole,
    UpdateDefaultRolesRequest,
    UpdateDefaultRolesResponse,
    RoleCreateResponse,
    RoleRetrieveResponse,
    RoleUpdateResponse,
    RoleListResponse,
    RoleRetrieveDependentsResponse,
    RoleRetrievePermissionsAllResponse,
    RoleRetrieveUsersCountResponse,
)
```

Methods:

- <code title="post /api/v1/roles">client.api.v1.roles.<a href="./src/scalekit_demo/resources/api/v1/roles/roles.py">create</a>(\*\*<a href="src/scalekit_demo/types/api/v1/role_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/role_create_response.py">RoleCreateResponse</a></code>
- <code title="get /api/v1/roles/{role_name}">client.api.v1.roles.<a href="./src/scalekit_demo/resources/api/v1/roles/roles.py">retrieve</a>(role_name, \*\*<a href="src/scalekit_demo/types/api/v1/role_retrieve_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/role_retrieve_response.py">RoleRetrieveResponse</a></code>
- <code title="put /api/v1/roles/{role_name}">client.api.v1.roles.<a href="./src/scalekit_demo/resources/api/v1/roles/roles.py">update</a>(role_name, \*\*<a href="src/scalekit_demo/types/api/v1/role_update_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/role_update_response.py">RoleUpdateResponse</a></code>
- <code title="get /api/v1/roles">client.api.v1.roles.<a href="./src/scalekit_demo/resources/api/v1/roles/roles.py">list</a>(\*\*<a href="src/scalekit_demo/types/api/v1/role_list_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/role_list_response.py">RoleListResponse</a></code>
- <code title="delete /api/v1/roles/{role_name}">client.api.v1.roles.<a href="./src/scalekit_demo/resources/api/v1/roles/roles.py">delete</a>(role_name, \*\*<a href="src/scalekit_demo/types/api/v1/role_delete_params.py">params</a>) -> None</code>
- <code title="delete /api/v1/roles/{role_name}/base">client.api.v1.roles.<a href="./src/scalekit_demo/resources/api/v1/roles/roles.py">delete_base</a>(role_name) -> None</code>
- <code title="get /api/v1/roles/{role_name}/dependents">client.api.v1.roles.<a href="./src/scalekit_demo/resources/api/v1/roles/roles.py">retrieve_dependents</a>(role_name) -> <a href="./src/scalekit_demo/types/api/v1/role_retrieve_dependents_response.py">RoleRetrieveDependentsResponse</a></code>
- <code title="get /api/v1/roles/{role_name}/permissions:all">client.api.v1.roles.<a href="./src/scalekit_demo/resources/api/v1/roles/roles.py">retrieve_permissions_all</a>(role_name) -> <a href="./src/scalekit_demo/types/api/v1/role_retrieve_permissions_all_response.py">RoleRetrievePermissionsAllResponse</a></code>
- <code title="get /api/v1/roles/{role_name}/users:count">client.api.v1.roles.<a href="./src/scalekit_demo/resources/api/v1/roles/roles.py">retrieve_users_count</a>(role_name) -> <a href="./src/scalekit_demo/types/api/v1/role_retrieve_users_count_response.py">RoleRetrieveUsersCountResponse</a></code>
- <code title="patch /api/v1/roles/default">client.api.v1.roles.<a href="./src/scalekit_demo/resources/api/v1/roles/roles.py">update_default</a>(\*\*<a href="src/scalekit_demo/types/api/v1/role_update_default_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/update_default_roles_response.py">UpdateDefaultRolesResponse</a></code>

#### Permissions

Types:

```python
from scalekit_demo.types.api.v1.roles import PermissionCreateResponse, PermissionListResponse
```

Methods:

- <code title="post /api/v1/roles/{role_name}/permissions">client.api.v1.roles.permissions.<a href="./src/scalekit_demo/resources/api/v1/roles/permissions.py">create</a>(path_role_name, \*\*<a href="src/scalekit_demo/types/api/v1/roles/permission_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/roles/permission_create_response.py">PermissionCreateResponse</a></code>
- <code title="get /api/v1/roles/{role_name}/permissions">client.api.v1.roles.permissions.<a href="./src/scalekit_demo/resources/api/v1/roles/permissions.py">list</a>(role_name) -> <a href="./src/scalekit_demo/types/api/v1/roles/permission_list_response.py">PermissionListResponse</a></code>
- <code title="delete /api/v1/roles/{role_name}/permissions/{permission_name}">client.api.v1.roles.permissions.<a href="./src/scalekit_demo/resources/api/v1/roles/permissions.py">delete</a>(permission_name, \*, role_name) -> None</code>

### Scopes

Types:

```python
from scalekit_demo.types.api.v1 import ScopeUpdateResponse
```

Methods:

- <code title="post /api/v1/scopes">client.api.v1.scopes.<a href="./src/scalekit_demo/resources/api/v1/scopes.py">create</a>(\*\*<a href="src/scalekit_demo/types/api/v1/scope_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/environments/create_scope_response.py">CreateScopeResponse</a></code>
- <code title="patch /api/v1/scopes/{id}">client.api.v1.scopes.<a href="./src/scalekit_demo/resources/api/v1/scopes.py">update</a>(id, \*\*<a href="src/scalekit_demo/types/api/v1/scope_update_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/scope_update_response.py">ScopeUpdateResponse</a></code>
- <code title="get /api/v1/scopes">client.api.v1.scopes.<a href="./src/scalekit_demo/resources/api/v1/scopes.py">list</a>(\*\*<a href="src/scalekit_demo/types/api/v1/scope_list_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/environments/list_scopes_response.py">ListScopesResponse</a></code>
- <code title="delete /api/v1/scopes/{id}">client.api.v1.scopes.<a href="./src/scalekit_demo/resources/api/v1/scopes.py">delete</a>(id) -> None</code>

### Sessions

Types:

```python
from scalekit_demo.types.api.v1 import Location, SessionDetails, SessionRevokeResponse
```

Methods:

- <code title="get /api/v1/sessions/{session_id}">client.api.v1.sessions.<a href="./src/scalekit_demo/resources/api/v1/sessions.py">retrieve</a>(session_id) -> <a href="./src/scalekit_demo/types/api/v1/session_details.py">SessionDetails</a></code>
- <code title="post /api/v1/sessions/{session_id}/revoke">client.api.v1.sessions.<a href="./src/scalekit_demo/resources/api/v1/sessions.py">revoke</a>(session_id) -> <a href="./src/scalekit_demo/types/api/v1/session_revoke_response.py">SessionRevokeResponse</a></code>

### SSOUserAttributes

Methods:

- <code title="patch /api/v1/sso-user-attributes/{key}">client.api.v1.sso_user_attributes.<a href="./src/scalekit_demo/resources/api/v1/sso_user_attributes.py">update</a>(path_key, \*\*<a href="src/scalekit_demo/types/api/v1/sso_user_attribute_update_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/update_user_attribute_response.py">UpdateUserAttributeResponse</a></code>
- <code title="delete /api/v1/sso-user-attributes/{key}">client.api.v1.sso_user_attributes.<a href="./src/scalekit_demo/resources/api/v1/sso_user_attributes.py">delete</a>(key) -> None</code>
- <code title="get /api/v1/sso-user-attributes">client.api.v1.sso_user_attributes.<a href="./src/scalekit_demo/resources/api/v1/sso_user_attributes.py">retrieve_sso_user_attributes</a>() -> <a href="./src/scalekit_demo/types/api/v1/list_user_attributes_response.py">ListUserAttributesResponse</a></code>
- <code title="post /api/v1/sso-user-attributes">client.api.v1.sso_user_attributes.<a href="./src/scalekit_demo/resources/api/v1/sso_user_attributes.py">sso_user_attributes</a>(\*\*<a href="src/scalekit_demo/types/api/v1/sso_user_attribute_sso_user_attributes_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/create_user_attribute_response.py">CreateUserAttributeResponse</a></code>

### Tools

Types:

```python
from scalekit_demo.types.api.v1 import (
    Tool,
    ToolCreateResponse,
    ToolListResponse,
    ToolRetrieveScopedResponse,
)
```

Methods:

- <code title="post /api/v1/tools">client.api.v1.tools.<a href="./src/scalekit_demo/resources/api/v1/tools.py">create</a>(\*\*<a href="src/scalekit_demo/types/api/v1/tool_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/tool_create_response.py">ToolCreateResponse</a></code>
- <code title="get /api/v1/tools">client.api.v1.tools.<a href="./src/scalekit_demo/resources/api/v1/tools.py">list</a>(\*\*<a href="src/scalekit_demo/types/api/v1/tool_list_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/tool_list_response.py">ToolListResponse</a></code>
- <code title="delete /api/v1/tools/{id}">client.api.v1.tools.<a href="./src/scalekit_demo/resources/api/v1/tools.py">delete</a>(id) -> None</code>
- <code title="get /api/v1/tools/scoped">client.api.v1.tools.<a href="./src/scalekit_demo/resources/api/v1/tools.py">retrieve_scoped</a>(\*\*<a href="src/scalekit_demo/types/api/v1/tool_retrieve_scoped_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/tool_retrieve_scoped_response.py">ToolRetrieveScopedResponse</a></code>

### Totp

Types:

```python
from scalekit_demo.types.api.v1 import (
    TotpRegistration,
    VerifyCodeResponse,
    TotpEnableResponse,
    TotpRegistrationResponse,
)
```

Methods:

- <code title="post /api/v1/totp/{registration_id}/disable">client.api.v1.totp.<a href="./src/scalekit_demo/resources/api/v1/totp.py">disable</a>(path_registration_id, \*\*<a href="src/scalekit_demo/types/api/v1/totp_disable_params.py">params</a>) -> None</code>
- <code title="post /api/v1/totp/{registration_id}/enable">client.api.v1.totp.<a href="./src/scalekit_demo/resources/api/v1/totp.py">enable</a>(path_registration_id, \*\*<a href="src/scalekit_demo/types/api/v1/totp_enable_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/totp_enable_response.py">TotpEnableResponse</a></code>
- <code title="post /api/v1/totp/registration">client.api.v1.totp.<a href="./src/scalekit_demo/resources/api/v1/totp.py">registration</a>(\*\*<a href="src/scalekit_demo/types/api/v1/totp_registration_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/totp_registration_response.py">TotpRegistrationResponse</a></code>
- <code title="post /api/v1/totp/{registration_id}/verify">client.api.v1.totp.<a href="./src/scalekit_demo/resources/api/v1/totp.py">verify</a>(path_registration_id, \*\*<a href="src/scalekit_demo/types/api/v1/totp_verify_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/verify_code_response.py">VerifyCodeResponse</a></code>

### UserProfileAttributes

Methods:

- <code title="patch /api/v1/user-profile-attributes/{key}">client.api.v1.user_profile_attributes.<a href="./src/scalekit_demo/resources/api/v1/user_profile_attributes.py">update</a>(path_key, \*\*<a href="src/scalekit_demo/types/api/v1/user_profile_attribute_update_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/update_user_attribute_response.py">UpdateUserAttributeResponse</a></code>
- <code title="delete /api/v1/user-profile-attributes/{key}">client.api.v1.user_profile_attributes.<a href="./src/scalekit_demo/resources/api/v1/user_profile_attributes.py">delete</a>(key) -> None</code>
- <code title="get /api/v1/user-profile-attributes">client.api.v1.user_profile_attributes.<a href="./src/scalekit_demo/resources/api/v1/user_profile_attributes.py">retrieve_user_profile_attributes</a>() -> <a href="./src/scalekit_demo/types/api/v1/list_user_attributes_response.py">ListUserAttributesResponse</a></code>
- <code title="post /api/v1/user-profile-attributes">client.api.v1.user_profile_attributes.<a href="./src/scalekit_demo/resources/api/v1/user_profile_attributes.py">user_profile_attributes</a>(\*\*<a href="src/scalekit_demo/types/api/v1/user_profile_attribute_user_profile_attributes_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/create_user_attribute_response.py">CreateUserAttributeResponse</a></code>

### Webhooks

Types:

```python
from scalekit_demo.types.api.v1 import WebhookUpdateResponse, WebhookRetrievePortalURLResponse
```

Methods:

- <code title="post /api/v1/webhooks/test-event/{event_type}">client.api.v1.webhooks.<a href="./src/scalekit_demo/resources/api/v1/webhooks/webhooks.py">update</a>(event_type) -> <a href="./src/scalekit_demo/types/api/v1/webhook_update_response.py">WebhookUpdateResponse</a></code>
- <code title="get /api/v1/webhooks/portal-url">client.api.v1.webhooks.<a href="./src/scalekit_demo/resources/api/v1/webhooks/webhooks.py">retrieve_portal_url</a>() -> <a href="./src/scalekit_demo/types/api/v1/webhook_retrieve_portal_url_response.py">WebhookRetrievePortalURLResponse</a></code>

### Workspaces

Types:

```python
from scalekit_demo.types.api.v1 import (
    GetWorkspaceResponse,
    UpdateWorkspace,
    UpdateWorkspaceResponse,
)
```

Methods:

- <code title="get /api/v1/workspaces/{id}">client.api.v1.workspaces.<a href="./src/scalekit_demo/resources/api/v1/workspaces/workspaces.py">retrieve</a>(id) -> <a href="./src/scalekit_demo/types/api/v1/get_workspace_response.py">GetWorkspaceResponse</a></code>
- <code title="patch /api/v1/workspaces/{id}">client.api.v1.workspaces.<a href="./src/scalekit_demo/resources/api/v1/workspaces/workspaces.py">update</a>(id, \*\*<a href="src/scalekit_demo/types/api/v1/workspace_update_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/update_workspace_response.py">UpdateWorkspaceResponse</a></code>

#### Billing

Types:

```python
from scalekit_demo.types.api.v1.workspaces import (
    BillingRetrieveCustomerPortalResponse,
    BillingRetrievePricingTableResponse,
    BillingRetrieveSubscriptionsResponse,
)
```

Methods:

- <code title="get /api/v1/workspaces/{id}/billing/customer-portal">client.api.v1.workspaces.billing.<a href="./src/scalekit_demo/resources/api/v1/workspaces/billing.py">retrieve_customer_portal</a>(id) -> <a href="./src/scalekit_demo/types/api/v1/workspaces/billing_retrieve_customer_portal_response.py">BillingRetrieveCustomerPortalResponse</a></code>
- <code title="get /api/v1/workspaces/{id}/billing/pricing-table">client.api.v1.workspaces.billing.<a href="./src/scalekit_demo/resources/api/v1/workspaces/billing.py">retrieve_pricing_table</a>(id) -> <a href="./src/scalekit_demo/types/api/v1/workspaces/billing_retrieve_pricing_table_response.py">BillingRetrievePricingTableResponse</a></code>
- <code title="get /api/v1/workspaces/{id}/billing/subscriptions">client.api.v1.workspaces.billing.<a href="./src/scalekit_demo/resources/api/v1/workspaces/billing.py">retrieve_subscriptions</a>(id) -> <a href="./src/scalekit_demo/types/api/v1/workspaces/billing_retrieve_subscriptions_response.py">BillingRetrieveSubscriptionsResponse</a></code>

### WorkspacesThis

Types:

```python
from scalekit_demo.types.api.v1 import (
    WorkspacesThisRetrieveBillingInfoResponse,
    WorkspacesThisRetrieveBillingUsageResponse,
)
```

Methods:

- <code title="get /api/v1/workspaces:this/billing:info">client.api.v1.workspaces_this.<a href="./src/scalekit_demo/resources/api/v1/workspaces_this.py">retrieve_billing_info</a>() -> <a href="./src/scalekit_demo/types/api/v1/workspaces_this_retrieve_billing_info_response.py">WorkspacesThisRetrieveBillingInfoResponse</a></code>
- <code title="get /api/v1/workspaces:this/billing:usage">client.api.v1.workspaces_this.<a href="./src/scalekit_demo/resources/api/v1/workspaces_this.py">retrieve_billing_usage</a>() -> <a href="./src/scalekit_demo/types/api/v1/workspaces_this_retrieve_billing_usage_response.py">WorkspacesThisRetrieveBillingUsageResponse</a></code>
- <code title="get /api/v1/workspaces:this">client.api.v1.workspaces_this.<a href="./src/scalekit_demo/resources/api/v1/workspaces_this.py">retrieve_workspaces_this</a>() -> <a href="./src/scalekit_demo/types/api/v1/get_workspace_response.py">GetWorkspaceResponse</a></code>
- <code title="patch /api/v1/workspaces:this">client.api.v1.workspaces_this.<a href="./src/scalekit_demo/resources/api/v1/workspaces_this.py">update_workspaces_this</a>(\*\*<a href="src/scalekit_demo/types/api/v1/workspaces_this_update_workspaces_this_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/update_workspace_response.py">UpdateWorkspaceResponse</a></code>

### Email

#### Servers

Types:

```python
from scalekit_demo.types.api.v1.email import (
    EmailServer,
    GetEmailServerResponse,
    SmtpServerSettings,
    ServerCreateResponse,
    ServerListResponse,
    ServerUpdateServerIDEnableResponse,
)
```

Methods:

- <code title="post /api/v1/email/servers">client.api.v1.email.servers.<a href="./src/scalekit_demo/resources/api/v1/email/servers.py">create</a>(\*\*<a href="src/scalekit_demo/types/api/v1/email/server_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/email/server_create_response.py">ServerCreateResponse</a></code>
- <code title="get /api/v1/email/servers/{server_id}">client.api.v1.email.servers.<a href="./src/scalekit_demo/resources/api/v1/email/servers.py">retrieve</a>(server_id) -> <a href="./src/scalekit_demo/types/api/v1/email/get_email_server_response.py">GetEmailServerResponse</a></code>
- <code title="put /api/v1/email/servers/{server_id}">client.api.v1.email.servers.<a href="./src/scalekit_demo/resources/api/v1/email/servers.py">update</a>(server_id, \*\*<a href="src/scalekit_demo/types/api/v1/email/server_update_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/email/get_email_server_response.py">GetEmailServerResponse</a></code>
- <code title="get /api/v1/email/servers">client.api.v1.email.servers.<a href="./src/scalekit_demo/resources/api/v1/email/servers.py">list</a>() -> <a href="./src/scalekit_demo/types/api/v1/email/server_list_response.py">ServerListResponse</a></code>
- <code title="delete /api/v1/email/servers/{server_id}">client.api.v1.email.servers.<a href="./src/scalekit_demo/resources/api/v1/email/servers.py">delete</a>(server_id) -> None</code>
- <code title="patch /api/v1/email/servers/{server_id}:disable">client.api.v1.email.servers.<a href="./src/scalekit_demo/resources/api/v1/email/servers.py">update_server_id_disable</a>(server_id) -> None</code>
- <code title="patch /api/v1/email/servers/{server_id}:enable">client.api.v1.email.servers.<a href="./src/scalekit_demo/resources/api/v1/email/servers.py">update_server_id_enable</a>(server_id) -> <a href="./src/scalekit_demo/types/api/v1/email/server_update_server_id_enable_response.py">ServerUpdateServerIDEnableResponse</a></code>

#### Templates

Types:

```python
from scalekit_demo.types.api.v1.email import (
    TemplateRetrievePlaceholdersResponse,
    TemplateRetrieveUsecasesResponse,
)
```

Methods:

- <code title="get /api/v1/email/templates/placeholders">client.api.v1.email.templates.<a href="./src/scalekit_demo/resources/api/v1/email/templates.py">retrieve_placeholders</a>(\*\*<a href="src/scalekit_demo/types/api/v1/email/template_retrieve_placeholders_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/email/template_retrieve_placeholders_response.py">TemplateRetrievePlaceholdersResponse</a></code>
- <code title="get /api/v1/email/templates/usecases">client.api.v1.email.templates.<a href="./src/scalekit_demo/resources/api/v1/email/templates.py">retrieve_usecases</a>() -> <a href="./src/scalekit_demo/types/api/v1/email/template_retrieve_usecases_response.py">TemplateRetrieveUsecasesResponse</a></code>

#### Configuration

Types:

```python
from scalekit_demo.types.api.v1.email import ConfigurationCreateResponse, ConfigurationListResponse
```

Methods:

- <code title="post /api/v1/emails/configuration">client.api.v1.email.configuration.<a href="./src/scalekit_demo/resources/api/v1/email/configuration.py">create</a>(\*\*<a href="src/scalekit_demo/types/api/v1/email/configuration_create_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/email/configuration_create_response.py">ConfigurationCreateResponse</a></code>
- <code title="get /api/v1/emails/configuration">client.api.v1.email.configuration.<a href="./src/scalekit_demo/resources/api/v1/email/configuration.py">list</a>() -> <a href="./src/scalekit_demo/types/api/v1/email/configuration_list_response.py">ConfigurationListResponse</a></code>

### User

Types:

```python
from scalekit_demo.types.api.v1 import (
    UserRetrieveResponse,
    UserUpdateResponse,
    UserListResponse,
    UserRetrieveSessionsResponse,
)
```

Methods:

- <code title="get /api/v1/users/{id}">client.api.v1.user.<a href="./src/scalekit_demo/resources/api/v1/user.py">retrieve</a>(id, \*\*<a href="src/scalekit_demo/types/api/v1/user_retrieve_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/user_retrieve_response.py">UserRetrieveResponse</a></code>
- <code title="patch /api/v1/users/{id}">client.api.v1.user.<a href="./src/scalekit_demo/resources/api/v1/user.py">update</a>(id, \*\*<a href="src/scalekit_demo/types/api/v1/user_update_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/user_update_response.py">UserUpdateResponse</a></code>
- <code title="get /api/v1/users">client.api.v1.user.<a href="./src/scalekit_demo/resources/api/v1/user.py">list</a>(\*\*<a href="src/scalekit_demo/types/api/v1/user_list_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/user_list_response.py">UserListResponse</a></code>
- <code title="delete /api/v1/users/{id}">client.api.v1.user.<a href="./src/scalekit_demo/resources/api/v1/user.py">delete</a>(id, \*\*<a href="src/scalekit_demo/types/api/v1/user_delete_params.py">params</a>) -> None</code>
- <code title="get /api/v1/users/{user_id}/sessions">client.api.v1.user.<a href="./src/scalekit_demo/resources/api/v1/user.py">retrieve_sessions</a>(user_id, \*\*<a href="src/scalekit_demo/types/api/v1/user_retrieve_sessions_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/user_retrieve_sessions_response.py">UserRetrieveSessionsResponse</a></code>
- <code title="post /api/v1/user/{user_id}/totp:verify">client.api.v1.user.<a href="./src/scalekit_demo/resources/api/v1/user.py">totp_verify</a>(path_user_id, \*\*<a href="src/scalekit_demo/types/api/v1/user_totp_verify_params.py">params</a>) -> <a href="./src/scalekit_demo/types/api/v1/verify_code_response.py">VerifyCodeResponse</a></code>

# Migrations

Types:

```python
from scalekit_demo.types import (
    MigrationCreateFsaDataResponse,
    MigrationCreateStripeCustomersResponse,
)
```

Methods:

- <code title="post /migrations/fsa-data">client.migrations.<a href="./src/scalekit_demo/resources/migrations.py">create_fsa_data</a>(\*\*<a href="src/scalekit_demo/types/migration_create_fsa_data_params.py">params</a>) -> <a href="./src/scalekit_demo/types/migration_create_fsa_data_response.py">MigrationCreateFsaDataResponse</a></code>
- <code title="post /migrations/stripe-customers">client.migrations.<a href="./src/scalekit_demo/resources/migrations.py">create_stripe_customers</a>(\*\*<a href="src/scalekit_demo/types/migration_create_stripe_customers_params.py">params</a>) -> <a href="./src/scalekit_demo/types/migration_create_stripe_customers_response.py">MigrationCreateStripeCustomersResponse</a></code>
