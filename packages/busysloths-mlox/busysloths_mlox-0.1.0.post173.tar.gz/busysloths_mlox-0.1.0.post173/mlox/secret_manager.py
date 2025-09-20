import os
import json
import logging

from cryptography.fernet import Fernet

from abc import ABC, abstractmethod
from typing import Any, Dict
from dataclasses import dataclass, field

from mlox.infra import Infrastructure
from mlox.server import AbstractServer
from mlox.utils import (
    _get_encryption_key,
    dict_to_dataclass,
    load_from_json,
    dataclass_to_dict,
)
from mlox.remote import (
    fs_create_dir,
    fs_touch,
    fs_read_file,
    fs_write_file,
    fs_list_files,
)


@dataclass
class AbstractSecretManager(ABC):
    """A simple interface for secret managers."""

    @abstractmethod
    def is_working(self) -> bool:
        """Check if the secret manager is working."""
        pass

    @abstractmethod
    def list_secrets(self, keys_only: bool = False) -> Dict[str, Any]:
        """List all secrets stored in the secret manager."""
        pass

    @abstractmethod
    def save_secret(self, name: str, my_secret: Dict | str) -> None:
        """Save a secret to the secret manager."""
        pass

    @abstractmethod
    def load_secret(self, name: str) -> Dict | str | None:
        """Load a secret from the secret manager."""
        pass

    @classmethod
    @abstractmethod
    def instantiate_secret_manager(
        cls, info: Dict[str, Any]
    ) -> "AbstractSecretManager | None":
        """Load the infrastructure configuration from the secret manager."""
        pass

    @abstractmethod
    def get_access_secrets(self) -> Dict[str, Any] | None:
        """Get MLOX access information from the secret manager."""
        pass


@dataclass
class AbstractSecretManagerService(ABC):
    @abstractmethod
    def get_secret_manager(self, infra: Infrastructure) -> AbstractSecretManager:
        pass


@dataclass
class TinySecretManager(AbstractSecretManager):
    """A simple secret manager that encrypts and decrypts secrets saved on a remote machine."""

    path: str
    master_token: str
    server: AbstractServer
    cache: Dict[str, Any]
    _connection_works: bool = False

    def __init__(
        self,
        server_config_file: str,
        secrets_relative_path: str,
        master_token: str,
        server_dict: Dict[str, Any] | None = None,
        secrets_abs_path: str | None = None,
    ):
        self.cache = {}
        self.master_token = master_token

        if not server_dict:
            server_dict = load_from_json(server_config_file, master_token)

        if not server_dict:
            raise ValueError(
                "Server configuration is missing or invalid. Cannot initialize TinySecretManager."
            )
        server = dict_to_dataclass(server_dict, [AbstractServer])
        if not server:
            raise ValueError("Server is not set. Cannot initialize TinySecretManager.")
        self.server = server
        if not server.mlox_user:
            raise ValueError(
                "Server user is not set. Cannot initialize TinySecretManager."
            )
        if secrets_abs_path:
            self.path = secrets_abs_path
        else:
            self.path = f"{server.mlox_user.home}/{secrets_relative_path}"
        with server.get_server_connection() as conn:
            fs_create_dir(conn, self.path)
            if conn.is_connected:
                self._connection_works = True
        list_secrets = self.list_secrets(keys_only=False, use_cache=False)
        self.cache.update(list_secrets)

    def is_working(self) -> bool:
        return self._connection_works

    def list_secrets(
        self, keys_only: bool = False, use_cache: bool = True
    ) -> Dict[str, Any]:
        if use_cache:
            if keys_only:
                return {k: None for k in self.cache.keys()}
            return self.cache
        secrets: Dict[str, Any] = {}
        with self.server.get_server_connection() as conn:
            files = fs_list_files(conn, self.path)
            for file in files:
                if file.endswith(".json"):
                    name = file[:-5]
                    if keys_only:
                        secrets[name] = None
                    else:
                        secret_value = None
                        try:
                            file_path = f"{self.path}/{file}"
                            encrypted_data = fs_read_file(
                                conn, file_path, encoding="utf-8", format="json"
                            )
                            # Decrypt the data
                            key = _get_encryption_key(password=self.master_token)
                            fernet = Fernet(key)
                            json_string = fernet.decrypt(encrypted_data).decode("utf-8")
                            secret_value = json.loads(json_string)
                        except BaseException:
                            continue
                        secrets[name] = secret_value
        return secrets

    def save_secret(self, name: str, my_secret: Dict | str) -> None:
        name += ".json"
        filepath = os.path.join(self.path, name)
        with self.server.get_server_connection() as conn:
            fs_touch(conn, filepath)

        """Saves a secret to a file."""
        if isinstance(my_secret, str):
            # Check if it's already a valid JSON string
            try:
                my_secret = json.loads(my_secret)
            except json.JSONDecodeError:
                logging.info("Provided string secret is not valid JSON.")

        json_string = json.dumps(my_secret, indent=2)
        # Encrypt the JSON string
        key = _get_encryption_key(password=self.master_token)
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(json_string.encode("utf-8"))

        with self.server.get_server_connection() as conn:
            fs_write_file(conn, filepath, encrypted_data)

        self.cache[name] = my_secret

    def load_secret(self, name: str) -> Dict | str | None:
        if name in self.cache:
            return self.cache[name]
        name += ".json"
        filepath = os.path.join(self.path, name)

        encrypted_data = None
        with self.server.get_server_connection() as conn:
            try:
                encrypted_data = fs_read_file(
                    conn, filepath, encoding="utf-8", format="json"
                )
            except BaseException:
                logging.error(f"Error reading secret '{name}'.")
                return None

        # Decrypt the data
        key = _get_encryption_key(password=self.master_token)
        fernet = Fernet(key)
        try:
            json_string = fernet.decrypt(encrypted_data).decode("utf-8")
        except Exception as e:
            logging.error(f"Error decrypting secret '{name}': {e}")
            return None
        return json.loads(json_string)

    @classmethod
    def instantiate_secret_manager(
        cls, info: Dict[str, Any]
    ) -> "AbstractSecretManager | None":
        try:
            server_dict = info.get("keyfile", None)
            password = info.get("secrets_master_token", None)
            abs_path = info.get("secrets_abs_path", None)
            return TinySecretManager(
                "", "", password, server_dict=server_dict, secrets_abs_path=abs_path
            )
        except Exception as e:
            logging.error(f"Error initializing secret manager: {e}")
        return None

    def get_access_secrets(self) -> Dict[str, Any] | None:
        server_dict = dataclass_to_dict(self.server)
        return {
            "keyfile": server_dict,
            "secrets_abs_path": self.path,
            "secrets_master_token": self.master_token,
        }


@dataclass
class InMemorySecretManager(AbstractSecretManager):
    """A lightweight, ephemeral secret manager that keeps secrets in memory.
    Useful for tests and local runs where no remote secret storage is available.
    """

    _store: Dict[str, Any] = field(default_factory=dict, init=False)

    def __post_init__(self):
        if not self._store:
            self._store = {}

    def is_working(self) -> bool:
        return True

    def list_secrets(self, keys_only: bool = False) -> Dict[str, Any]:
        if keys_only:
            return {k: None for k in self._store.keys()}
        return dict(self._store)

    def save_secret(self, name: str, my_secret: Dict | str) -> None:
        # store raw dict/string; caller controls encryption if needed
        self._store[name] = my_secret

    def load_secret(self, name: str) -> Dict | str | None:
        return self._store.get(name)

    @classmethod
    def instantiate_secret_manager(
        cls, info: Dict[str, Any]
    ) -> "InMemorySecretManager | None":
        # info may contain an initial 'secrets' dict
        inst = InMemorySecretManager()
        inst._store.update(info.get("secrets", {}))
        return inst

    def get_access_secrets(self) -> Dict[str, Any] | None:
        # expose the entire store as access info for persistence if needed
        return {"secrets": dict(self._store)}


if __name__ == "__main__":
    # Make sure your environment variable is set!
    password = os.environ.get("MLOX_CONFIG_PASSWORD", None)
    if not password:
        print("Error: MLOX_CONFIG_PASSWORD environment variable is not set.")
        exit(1)

    secret_manager = TinySecretManager("/mlox333.key", ".secrets", password)
    # print(secret_manager.load_secret("TEST_SECRET"))
    # secret_manager.save_secret(
    #     "TEST_SECRET",
    #     {
    #         "superkey": "supervalue",
    #         "anotherkey": "anothervalue",
    #         "listkey": ["item1", "item2"],
    #     },
    # )
    infra = secret_manager.load_secret("MLOX_CONFIG_INFRASTRUCTURE")
    print(infra)
