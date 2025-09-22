#   -------------------------------------------------------------
#   Secretsmith :: Vault :: KV secrets engine - version 2
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   Project:        Nasqueron
#   License:        BSD-2-Clause
#   -------------------------------------------------------------


from typing import Any, Dict, Tuple

from hvac import Client


#   -------------------------------------------------------------
#   Fetch secret from kv engine
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def read_secret(client: Client, mount_point: str, secret_path: str) -> Dict[str, str]:
    secret = client.secrets.kv.read_secret_version(
        mount_point=mount_point,
        path=secret_path,
        raise_on_deleted_version=True,
    )
    return secret["data"]["data"]


def read_secret_with_metadata(
    client: Client, mount_point: str, secret_path: str
) -> Tuple[dict[str, str], dict[str, Any]]:
    """
    Read a secret and return the data and the metadata dictionaries.
    """
    secret = client.secrets.kv.read_secret_version(
        mount_point=mount_point,
        path=secret_path,
        raise_on_deleted_version=True,
    )

    return secret["data"]["data"], secret["data"]["metadata"]


def read_secret_with_custom_metadata(
    client: Client, mount_point: str, secret_path: str
) -> Tuple[dict[str, str], dict[str, Any]]:
    """
    Read a secret and return the data and the metadata dictionaries.

    The custom metadata keys are directly merged into the metadata dictionary.
    """
    data, metadata = read_secret_with_metadata(client, mount_point, secret_path)

    if "custom_metadata" in metadata:
        metadata.update(metadata["custom_metadata"])
        del metadata["custom_metadata"]

    return data, metadata


#   -------------------------------------------------------------
#   Helpers to select common fields
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def get_username(client: Client, mount_point: str, secret_path: str) -> str:
    return get_field(client, mount_point, secret_path, "username")


def get_password(client: Client, mount_point: str, secret_path: str) -> str:
    return get_field(client, mount_point, secret_path, "password")


def get_field(client: Client, mount_point: str, secret_path: str, field: str) -> str:
    secret = read_secret(client, mount_point, secret_path)

    try:
        return secret[field]
    except KeyError:
        raise ValueError(f"Missing {field} field in {mount_point}/{secret_path}")
