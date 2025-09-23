from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Dict, Optional

import hvac  # type: ignore
from tenacity import RetryError, retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from secrets_sdk.secret_uri import parse as parse_uri
from secrets_sdk.vault_strategies.base_vault_strategy import BaseVaultStrategy
from secrets_sdk.vault_strategies.errors import (
    VaultAuthenticationError,
    VaultOperationError,
    VaultSecretNotFoundError,
    VaultSecretVersionDeletedError,
    VaultSecretVersionDestroyedError,
    VaultTimeoutError,
)


@dataclass
class VaultConfigData:
    url: str
    token: str | None
    timeout: int = 30
    verify_ssl: bool = True
    pool_size: int = 10


class HashiCorpVaultStrategy(BaseVaultStrategy):
    def __init__(self, config: Dict[str, Any]):
        self.config = VaultConfigData(
            url=config["url"],
            token=config.get("token"),
            timeout=int(config.get("timeout", 30)),
            verify_ssl=bool(config.get("verify_ssl", True)),
            pool_size=int(config.get("pool_size", 10)),
        )
        self._skip_auth_check = bool(config.get("skip_auth_check", False))
        self._executor = ThreadPoolExecutor(max_workers=self.config.pool_size)
        self._setup_client()

    def _setup_client(self) -> None:
        self.client = hvac.Client(
            url=self.config.url,
            token=self.config.token,
            timeout=self.config.timeout,
            verify=self.config.verify_ssl,
        )
        if not self._skip_auth_check and not self.client.is_authenticated():
            raise VaultAuthenticationError("Failed to authenticate with HashiCorp Vault")

    async def _run(self, func, *args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, lambda: func(*args, **kwargs))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type((ConnectionError, TimeoutError, VaultTimeoutError)),
        reraise=True,
    )
    async def _read_secret_kvv2(self, path: str, version: Optional[int]) -> Dict[str, Any]:
        try:
            if version is not None:
                resp = await self._run(self.client.secrets.kv.v2.read_secret_version, path=path, version=version)
            else:
                resp = await self._run(self.client.secrets.kv.v2.read_secret_version, path=path)
            if not resp or "data" not in resp:
                raise VaultOperationError("Invalid response format from Vault")
            return resp
        except hvac.exceptions.InvalidPath as e:  # type: ignore[attr-defined]
            raise VaultSecretNotFoundError(f"Secret not found at '{path}'") from e
        except hvac.exceptions.Forbidden as e:  # type: ignore[attr-defined]
            raise VaultAuthenticationError(f"Access denied to secret at '{path}'") from e
        except RetryError as e:  # pragma: no cover
            raise e
        except Exception as e:
            raise VaultOperationError(f"Failed to read secret: {e}") from e

    async def get_credentials(self, credential_reference: str) -> Dict[str, Any]:
        version: Optional[int] = None
        fragment_key: Optional[str] = None
        path = credential_reference
        if "://" in credential_reference:
            uri = parse_uri(credential_reference, tenant_id="dev", allowed_mounts=["secret"])  # type: ignore[arg-type]
            if uri.engine and uri.engine != "kv2":
                raise VaultOperationError(f"Unsupported engine '{uri.engine}' for HashiCorp Vault")
            path = "/".join([uri.mount] + list(uri.path_segments))
            fragment_key = uri.fragment_key
            for k, v in uri.params:
                if k == "version":
                    version = int(v)
                    break
        resp = await self._read_secret_kvv2(path, version)
        inner = (resp or {}).get("data", {})
        metadata = inner.get("metadata", {})
        if version is not None:
            if metadata.get("destroyed") is True:
                raise VaultSecretVersionDestroyedError(f"Version {version} destroyed for '{path}'")
            deletion_time = metadata.get("deletion_time")
            if deletion_time and str(deletion_time).strip():
                raise VaultSecretVersionDeletedError(f"Version {version} deleted for '{path}'")
        payload = inner.get("data")
        if payload is None:
            raise VaultOperationError("Malformed response from Vault")
        if fragment_key:
            return {fragment_key: payload.get(fragment_key)} if isinstance(payload, dict) else {fragment_key: None}
        return payload


