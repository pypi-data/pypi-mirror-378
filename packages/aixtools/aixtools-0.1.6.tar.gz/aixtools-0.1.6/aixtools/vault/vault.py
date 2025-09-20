# ruff: noqa: PLR0913
"""
Provides a Vault client for storing and retrieving user service api keys.
"""

import logging
from typing import Optional

import hvac
from hvac.exceptions import InvalidPath

from aixtools.utils import config

logger = logging.getLogger(__name__)


class VaultAuthError(Exception):
    """Exception raised for vault authentication errors."""


class VaultClient:
    """Vault client for storing and retrieving user service api keys."""

    def __init__(self):
        self.client = hvac.Client(url=config.VAULT_ADDRESS, token=config.VAULT_TOKEN)

        if not self.client.is_authenticated():
            raise VaultAuthError("Vault client authentication failed. Check vault_token.")

    def store_user_service_api_key(self, *, user_id: str, service_name: str, user_api_key: str):
        """
        Store user's service api key in the Vault at the specified vault mount
        point, where the path is <path_prefix>/<env>/<user_id>/<service_name>.
        """
        secret_path = None
        try:
            secret_path = f"{config.VAULT_PATH_PREFIX}/{config.VAULT_ENV}/{user_id}/{service_name}"
            print("secret_path", secret_path)
            secret_dict = {"user-api-key": user_api_key}
            self.client.secrets.kv.v2.create_or_update_secret(
                secret_path, secret=secret_dict, mount_point=config.VAULT_MOUNT_POINT
            )

            logger.info("Secret written to path %s", secret_path)
        except Exception as e:
            logger.error("Failed to write secret to path %s: %s", secret_path, str(e))
            raise VaultAuthError(e) from e

    def read_user_service_api_key(self, *, user_id: str, service_name) -> Optional[str]:
        """
        Read user's service api key in from vault at the specified mount point,
        where the path is <path_prefix>/<env>/<user_id>/<service_name>.
        """
        secret_path = None

        try:
            secret_path = f"{config.VAULT_PATH_PREFIX}/{config.VAULT_ENV}/{user_id}/{service_name}"
            logger.info("Reading secret from path %s", secret_path)
            response = self.client.secrets.kv.v2.read_secret_version(
                secret_path, mount_point=config.VAULT_MOUNT_POINT, raise_on_deleted_version=True
            )
            secret_data = response["data"]["data"]
            user_api_key = secret_data["user-api-key"]
            logger.info("Secret read from path %s ", secret_path)
            return user_api_key
        except InvalidPath:
            # Secret path does not exist
            logger.warning("Secret path does not exist %s ", secret_path)
            return None

        except Exception as e:
            logger.error("Failed to read secret from path %s: %s", secret_path, str(e))
            raise VaultAuthError(e) from e
