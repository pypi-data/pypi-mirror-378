"""Mixtrain CLI Client

This module provides the HTTP client and core functionality for the Mixtrain SDK.
It handles authentication, API communication, and dataset operations.

"""

import os
from functools import lru_cache
from logging import getLogger
from typing import Any, Dict, Optional

import httpx
from pyiceberg.catalog import load_catalog
from pyiceberg.table import Table

from .utils import auth as auth_utils
from .utils.config import get_config

logger = getLogger(__name__)


def call_api(
    method: str,
    path: str,
    json: Optional[Dict[str, Any]] = None,
    files: Optional[Dict[str, Any]] = None,
    *,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
):
    with httpx.Client(timeout=10.0) as client:
        try:
            config = get_config()
            logger.debug(
                f"Calling {config.platform_url} {method} {path} with json {json}"
            )
            # Only add extra query parameters from params if provided
            query_params = params if params else None
            request_headers = headers.copy() if headers else {}

            # Check for API key first (takes precedence over user auth token)
            api_key = os.getenv("MIXTRAIN_API_KEY")
            if api_key:
                if not api_key.startswith("mix-"):
                    raise Exception(
                        "Invalid API key format. API keys must start with 'mix-'"
                    )
                request_headers["X-API-Key"] = api_key
            else:
                # Fallback to JWT token
                auth_token = config.get_auth_token()
                if not auth_token:
                    raise Exception(
                        "No auth token or API key found. Set MIXTRAIN_API_KEY environment variable or authenticate with 'mixtrain login'"
                    )
                request_headers["Authorization"] = f"Bearer {auth_token}"
            if files:
                logger.debug(f"Calling {method} {path} with files {files}")
                response = client.request(
                    method,
                    f"{config.platform_url}{path}",
                    files=files,
                    params=query_params,
                    headers=request_headers,
                )
            else:
                logger.debug(f"Calling {method} {path} with json {json}")
                response = client.request(
                    method,
                    f"{config.platform_url}{path}",
                    json=json,
                    params=query_params,
                    headers=request_headers,
                )
            if response.status_code != 200:
                logger.error(
                    f"Error response {response.status_code} while requesting {response.request.url!r}: {response.json()}"
                )
                raise Exception(
                    f"Error: {response.json().get('detail', response.text)}"
                )
            return response
        except httpx.RequestError as exc:
            logger.error(f"An error occurred while requesting {exc.request.url!r}.")
            logger.exception(exc)
            raise
        except httpx.HTTPStatusError as exc:
            error_detail = exc.response.json().get("detail", str(exc))
            logger.debug(
                f"Error response {exc.response.status_code} while requesting {exc.request.url!r}: {error_detail}"
            )
            logger.exception(exc)
            raise Exception(error_detail)


def upload_file(dataset_name: str, file_path: str):
    """Upload a file to a dataset"""
    config = get_config()
    workspace_name = config.workspace_name
    with open(file_path, "rb") as f:
        response = call_api(
            "POST",
            f"/datasets/{workspace_name}/{dataset_name}/upload",
            files={"file": f},
        )
        return response.json().get("data")


def create_dataset_from_file(
    name: str, file_path: str, description: Optional[str] = None
):
    """Create a dataset from a file using the lakehouse API."""
    config = get_config()
    workspace_name = config.workspace_name

    headers = {}
    if description:
        headers["X-Description"] = description

    with open(file_path, "rb") as f:
        files = {"file": (file_path.split("/")[-1], f, "application/octet-stream")}
        response = call_api(
            "POST",
            f"/lakehouse/workspaces/{workspace_name}/tables/{name}",
            files=files,
            headers=headers,
        )
    return response.json()


def list_datasets():
    """List all datasets in the current workspace"""
    config = get_config()
    workspace_name = config.workspace_name
    response = call_api("GET", f"/lakehouse/workspaces/{workspace_name}/tables")
    return response.json()


def delete_dataset(name: str):
    """Delete a dataset"""
    config = get_config()
    workspace_name = config.workspace_name
    response = call_api(
        "DELETE", f"/lakehouse/workspaces/{workspace_name}/tables/{name}"
    )
    return response


def set_workspace(workspace_name: str):
    """Set the active workspace"""
    config = get_config()
    config.set_workspace(workspace_name)


def get_workspace() -> str:
    """Get the current workspace name"""
    config = get_config()
    return config.workspace_name


def authenticate_browser() -> str:
    """Authenticate using browser-based OAuth flow."""
    return auth_utils.authenticate_browser(get_config, call_api)


def authenticate_with_token(token: str, provider: str) -> str:
    """Authenticate using OAuth token (GitHub or Google)."""
    return auth_utils.authenticate_with_token(token, provider, get_config, call_api)


def authenticate_github(access_token: str) -> str:
    """Authenticate using GitHub access token."""
    return auth_utils.authenticate_github(access_token, get_config, call_api)


def authenticate_google(id_token: str) -> str:
    """Authenticate using Google ID token."""
    return auth_utils.authenticate_google(id_token, get_config, call_api)


@lru_cache(maxsize=1)
def get_workspace_name():
    config = get_config()
    return config.workspace_name


@lru_cache(maxsize=1)
def get_catalog(workspace_name: str):
    try:
        provider_secrets = call_api(
            "GET", f"/workspaces/{workspace_name}/dataset-providers/6"
        ).json()
        if provider_secrets["provider_type"] != "apache_iceberg":
            raise Exception(
                f"Dataset provider {provider_secrets['provider_type']} is not supported"
            )

        if (
            os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") is None
            and provider_secrets["secrets"]["CATALOG_WAREHOUSE_URI"].startswith("gs://")
            and provider_secrets["secrets"]["SERVICE_ACCOUNT_JSON"]
        ):
            service_account_json = provider_secrets["secrets"]["SERVICE_ACCOUNT_JSON"]
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
                f"/tmp/{workspace_name}/service_account.json"
            )

            # Set up Google Cloud credentials (temporary file)
            os.makedirs(f"/tmp/mixtrain/{workspace_name}", exist_ok=True)
            with open(f"/tmp/mixtrain/{workspace_name}/service_account.json", "w") as f:
                f.write(service_account_json)

            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
                f"/tmp/{workspace_name}/service_account.json"
            )

        # Load the catalog
        catalog_config = {
            "type": provider_secrets["secrets"]["CATALOG_TYPE"],
            "uri": provider_secrets["secrets"]["CATALOG_URI"],
            "warehouse": provider_secrets["secrets"]["CATALOG_WAREHOUSE_URI"],
        }
        catalog = load_catalog("default", **catalog_config)
        return catalog
    except Exception as e:
        raise Exception(f"Failed to load catalog: {e}")


def get_dataset(name: str) -> Table:
    """Get an Iceberg table using workspace secrets and PyIceberg catalog API.

    This creates a catalog connection using the workspace's dataset provider secrets.
    """

    config = get_config()
    workspace_name = config.workspace_name

    # Extract catalog configuration from secrets
    catalog = get_catalog(workspace_name)
    # Load the table
    table_identifier = f"{workspace_name}.{name}"
    table = catalog.load_table(table_identifier)
    return table


def list_dataset_providers():
    """List available and onboarded dataset providers."""
    config = get_config()
    workspace_name = config.workspace_name
    response = call_api("GET", f"/workspaces/{workspace_name}/dataset-providers/")
    return response.json()


def create_dataset_provider(provider_type: str, secrets: Dict[str, str]):
    """Onboard a new dataset provider for the workspace."""
    config = get_config()
    workspace_name = config.workspace_name
    payload = {"provider_type": provider_type, "secrets": secrets}
    response = call_api(
        "POST", f"/workspaces/{workspace_name}/dataset-providers/", json=payload
    )
    return response.json()


def update_dataset_provider(provider_id: int, secrets: Dict[str, str]):
    """Update secrets for an existing dataset provider."""
    config = get_config()
    workspace_name = config.workspace_name
    payload = {"secrets": secrets}
    response = call_api(
        "PUT",
        f"/workspaces/{workspace_name}/dataset-providers/{provider_id}",
        json=payload,
    )
    return response.json()


def delete_dataset_provider(provider_id: int):
    """Remove a dataset provider from the workspace."""
    config = get_config()
    workspace_name = config.workspace_name
    response = call_api(
        "DELETE", f"/workspaces/{workspace_name}/dataset-providers/{provider_id}"
    )
    return response.json()


def get_dataset_metadata(name: str):
    """Get detailed metadata for a table."""
    return get_dataset(name).metadata


def create_workspace(name: str, description: str = ""):
    """Create a new workspace."""
    response = call_api(
        "POST",
        "/workspaces/",
        json={"name": name, "description": description},
    )
    return response.json()


def delete_workspace(workspace_name: str):
    """Delete a workspace."""
    response = call_api("DELETE", f"/workspaces/{workspace_name}")
    return response


def list_workspaces():
    """List all workspaces the user has access to."""
    response = call_api("GET", "/workspaces/list")
    return response.json()


def list_model_providers():
    """List available and onboarded model providers."""
    config = get_config()
    workspace_name = config.workspace_name
    response = call_api("GET", f"/workspaces/{workspace_name}/models/providers")
    return response.json()


def create_model_provider(provider_type: str, secrets: Dict[str, str]):
    """Onboard a new model provider for the workspace."""
    config = get_config()
    workspace_name = config.workspace_name
    payload = {"provider_type": provider_type, "secrets": secrets}
    response = call_api(
        "POST", f"/workspaces/{workspace_name}/models/providers", json=payload
    )
    return response.json()


def update_model_provider(provider_id: int, secrets: Dict[str, str]):
    """Update secrets for an existing model provider."""
    config = get_config()
    workspace_name = config.workspace_name
    payload = {"secrets": secrets}
    response = call_api(
        "PUT",
        f"/workspaces/{workspace_name}/models/providers/{provider_id}",
        json=payload,
    )
    return response.json()


def delete_model_provider(provider_id: int):
    """Remove a model provider from the workspace."""
    config = get_config()
    workspace_name = config.workspace_name
    response = call_api(
        "DELETE", f"/workspaces/{workspace_name}/models/providers/{provider_id}"
    )
    return response.json()


def list_models():
    """List all internal models in the current workspace."""
    config = get_config()
    workspace_name = config.workspace_name
    response = call_api("GET", f"/workspaces/{workspace_name}/models/")
    return response.json()


def list_routing_configs(status: Optional[str] = None):
    """List all routing configurations in the workspace.

    Args:
        status: Optional filter by status ('active', 'inactive')

    Returns:
        Dict with 'data' key containing list of routing configuration summaries
    """
    config = get_config()
    workspace_name = config.workspace_name
    params = {"status": status} if status else None
    response = call_api(
        "GET", f"/workspaces/{workspace_name}/inference/configs", params=params
    )
    result = response.json()
    # Ensure consistent format: always return dict with 'data' key
    if isinstance(result, list):
        return {"data": result}
    return result


def get_routing_config(config_id: int, version: Optional[int] = None):
    """Get a specific routing configuration.

    Args:
        config_id: ID of the routing configuration
        version: Optional specific version to retrieve

    Returns:
        Dict with 'data' key containing full routing configuration with rules and metadata
    """
    config = get_config()
    workspace_name = config.workspace_name
    params = {"version": version} if version else None
    response = call_api(
        "GET",
        f"/workspaces/{workspace_name}/inference/configs/{config_id}",
        params=params,
    )
    result = response.json()
    # Ensure consistent format: always return dict with 'data' key
    if not isinstance(result, dict) or "data" not in result:
        return {"data": result}
    return result


def get_active_routing_config():
    """Get the currently active routing configuration for the workspace.

    Returns:
        Dict with 'data' key containing active routing configuration or None if no active config
    """
    config = get_config()
    workspace_name = config.workspace_name
    response = call_api("GET", f"/workspaces/{workspace_name}/inference/active-config")
    result = response.json()
    if result:
        # Ensure consistent format: always return dict with 'data' key
        if not isinstance(result, dict) or "data" not in result:
            return {"data": result}
        return result
    return None


def create_routing_config(name: str, description: str, rules: list):
    """Create a new routing configuration.

    Args:
        name: Name of the configuration
        description: Description of the configuration
        rules: List of routing rules

    Returns:
        Created routing configuration
    """
    config = get_config()
    workspace_name = config.workspace_name
    payload = {"name": name, "description": description, "rules": rules}
    response = call_api(
        "POST", f"/workspaces/{workspace_name}/inference/configs", json=payload
    )
    return response.json()


def update_routing_config(
    config_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    rules: Optional[list] = None,
):
    """Update a routing configuration (creates a new version).

    Args:
        config_id: ID of the configuration to update
        name: Optional new name
        description: Optional new description
        rules: Optional new rules list

    Returns:
        Updated routing configuration
    """
    config = get_config()
    workspace_name = config.workspace_name
    payload = {}
    if name is not None:
        payload["name"] = name
    if description is not None:
        payload["description"] = description
    if rules is not None:
        payload["rules"] = rules

    response = call_api(
        "PUT",
        f"/workspaces/{workspace_name}/inference/configs/{config_id}",
        json=payload,
    )
    return response.json()


def activate_routing_config(config_id: int, version: Optional[int] = None):
    """Activate a routing configuration.

    Args:
        config_id: ID of the configuration to activate
        version: Optional specific version to activate

    Returns:
        Activation result
    """
    config = get_config()
    workspace_name = config.workspace_name
    payload = {}
    if version is not None:
        payload["version"] = version

    response = call_api(
        "POST",
        f"/workspaces/{workspace_name}/inference/configs/{config_id}/activate",
        json=payload,
    )
    return response.json()


def delete_routing_config(config_id: int):
    """Delete a routing configuration and all its versions.

    Args:
        config_id: ID of the configuration to delete

    Returns:
        Deletion result
    """
    config = get_config()
    workspace_name = config.workspace_name
    response = call_api(
        "DELETE", f"/workspaces/{workspace_name}/inference/configs/{config_id}"
    )
    return response.json()


def test_routing_config(config_id: int, test_data: Dict[str, Any]):
    """Test routing configuration against sample data.

    Args:
        config_id: ID of the configuration to test
        test_data: Sample request data for testing

    Returns:
        Test results with matched rule and targets
    """
    config = get_config()
    workspace_name = config.workspace_name
    payload = {"test_data": test_data}
    response = call_api(
        "POST",
        f"/workspaces/{workspace_name}/inference/configs/{config_id}/test",
        json=payload,
    )
    return response.json()


def get_routing_config_versions(config_id: int):
    """Get all versions of a routing configuration.

    Args:
        config_id: ID of the configuration

    Returns:
        List of all configuration versions
    """
    config = get_config()
    workspace_name = config.workspace_name
    response = call_api(
        "GET", f"/workspaces/{workspace_name}/inference/configs/{config_id}/versions"
    )
    return response.json()
