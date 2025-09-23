from unittest.mock import MagicMock, patch

import pytest
from hvac.exceptions import InvalidPath

from aixtools.vault.vault import VaultAuthError, VaultClient


@pytest.fixture
def patched_vault_client():
    with patch("aixtools.vault.vault.hvac.Client") as mock_hvac_client_cls:
        fake_hvac_client = MagicMock()
        fake_hvac_client.is_authenticated.return_value = True
        mock_hvac_client_cls.return_value = fake_hvac_client

        client = VaultClient()
        return client


@pytest.fixture
def valid_params():
    return {
        "vault_mount_point": "secret",
        "path_prefix": "path",
        "env": "dev",
        "user_id": "test-user",
        "service_name": "test-service",
        "user_api_key": "test-api-key",
    }


def test_store_user_service_api_key_success(patched_vault_client, valid_params):
    patched_vault_client.client.secrets.kv.v2.create_or_update_secret.return_value = {}

    patched_vault_client.store_user_service_api_key(
        user_id=valid_params["user_id"],
        service_name=valid_params["service_name"],
        user_api_key=valid_params["user_api_key"],
    )

    secret_path = (
        f"{valid_params['path_prefix']}/{valid_params['env']}/{valid_params['user_id']}/{valid_params['service_name']}"
    )

    patched_vault_client.client.secrets.kv.v2.create_or_update_secret.assert_called_once_with(
        secret_path,
        secret={"user-api-key": valid_params["user_api_key"]},
        mount_point=valid_params["vault_mount_point"],
    )


def test_store_user_service_api_key_invalid_path(patched_vault_client, valid_params):
    patched_vault_client.client.secrets.kv.v2.create_or_update_secret.side_effect = Exception("Invalid Path")

    with pytest.raises(VaultAuthError, match="Invalid Path"):
        patched_vault_client.store_user_service_api_key(
            user_id=valid_params["user_id"],
            service_name=valid_params["service_name"],
            user_api_key=valid_params["user_api_key"],
        )
        patched_vault_client.client.assert_not_called()


def test_read_user_service_api_key_success(patched_vault_client):
    """Test successful read of user service API key."""
    mock_response = {"data": {"data": {"user-api-key": "test-api-key"}}}
    patched_vault_client.client.secrets.kv.v2.read_secret_version.return_value = mock_response

    result = patched_vault_client.read_user_service_api_key(user_id="test-user", service_name="test-service")

    assert result == "test-api-key"
    patched_vault_client.client.secrets.kv.v2.read_secret_version.assert_called_once_with(
        "path/dev/test-user/test-service", mount_point="secret", raise_on_deleted_version=True
    )


def test_read_user_service_api_key_secret_not_found(patched_vault_client):
    """Test read_user_service_api_key when the secret path does not exist."""
    patched_vault_client.client.secrets.kv.v2.read_secret_version.side_effect = InvalidPath

    result = patched_vault_client.read_user_service_api_key(user_id="test-user", service_name="test-service")

    assert result is None
    patched_vault_client.client.secrets.kv.v2.read_secret_version.assert_called_once_with(
        "path/dev/test-user/test-service", mount_point="secret", raise_on_deleted_version=True
    )


def test_read_user_service_api_key_unexpected_error(patched_vault_client):
    """Test read_user_service_api_key when an unexpected exception occurs."""
    patched_vault_client.client.secrets.kv.v2.read_secret_version.side_effect = Exception("Unexpected error")

    with pytest.raises(VaultAuthError, match="Unexpected error"):
        patched_vault_client.read_user_service_api_key(user_id="test-user", service_name="test-service")

    patched_vault_client.client.secrets.kv.v2.read_secret_version.assert_called_once_with(
        "path/dev/test-user/test-service", mount_point="secret", raise_on_deleted_version=True
    )


def test_store_user_service_secret_success(patched_vault_client, valid_params):
    """Test successful storage of complete user service secret."""
    secret_data = {"api_key": "test-api-key", "token": "test-token", "endpoint": "https://api.example.com"}
    patched_vault_client.client.secrets.kv.v2.create_or_update_secret.return_value = {}

    patched_vault_client.store_user_service_secret(
        user_id=valid_params["user_id"],
        service_name=valid_params["service_name"],
        secret_data=secret_data,
    )

    secret_path = (
        f"{valid_params['path_prefix']}/{valid_params['env']}/{valid_params['user_id']}/{valid_params['service_name']}"
    )

    patched_vault_client.client.secrets.kv.v2.create_or_update_secret.assert_called_once_with(
        secret_path,
        secret=secret_data,
        mount_point=valid_params["vault_mount_point"],
    )


def test_store_user_service_secret_error(patched_vault_client, valid_params):
    """Test store_user_service_secret when an error occurs."""
    secret_data = {"api_key": "test-api-key", "token": "test-token"}
    patched_vault_client.client.secrets.kv.v2.create_or_update_secret.side_effect = Exception("Storage error")

    with pytest.raises(VaultAuthError, match="Storage error"):
        patched_vault_client.store_user_service_secret(
            user_id=valid_params["user_id"],
            service_name=valid_params["service_name"],
            secret_data=secret_data,
        )


def test_read_user_service_secret_success(patched_vault_client):
    """Test successful read of complete user service secret."""
    secret_data = {"api_key": "test-api-key", "token": "test-token", "endpoint": "https://api.example.com"}
    mock_response = {"data": {"data": secret_data}}
    patched_vault_client.client.secrets.kv.v2.read_secret_version.return_value = mock_response

    result = patched_vault_client.read_user_service_secret(user_id="test-user", service_name="test-service")

    assert result == secret_data
    patched_vault_client.client.secrets.kv.v2.read_secret_version.assert_called_once_with(
        "path/dev/test-user/test-service", mount_point="secret", raise_on_deleted_version=True
    )


def test_read_user_service_secret_not_found(patched_vault_client):
    """Test read_user_service_secret when the secret path does not exist."""
    patched_vault_client.client.secrets.kv.v2.read_secret_version.side_effect = InvalidPath

    result = patched_vault_client.read_user_service_secret(user_id="test-user", service_name="test-service")

    assert result is None
    patched_vault_client.client.secrets.kv.v2.read_secret_version.assert_called_once_with(
        "path/dev/test-user/test-service", mount_point="secret", raise_on_deleted_version=True
    )


def test_read_user_service_secret_error(patched_vault_client):
    """Test read_user_service_secret when an unexpected exception occurs."""
    patched_vault_client.client.secrets.kv.v2.read_secret_version.side_effect = Exception("Read error")

    with pytest.raises(VaultAuthError, match="Read error"):
        patched_vault_client.read_user_service_secret(user_id="test-user", service_name="test-service")

    patched_vault_client.client.secrets.kv.v2.read_secret_version.assert_called_once_with(
        "path/dev/test-user/test-service", mount_point="secret", raise_on_deleted_version=True
    )
