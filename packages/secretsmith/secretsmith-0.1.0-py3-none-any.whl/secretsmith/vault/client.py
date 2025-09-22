#   -------------------------------------------------------------
#   Secretsmith :: Vault :: client
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   Project:        Nasqueron
#   License:        BSD-2-Clause
#   -------------------------------------------------------------


import os
from typing import Dict

from hvac import Client

from secretsmith.vault.config import load_config


#   -------------------------------------------------------------
#   General login
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def login(config_path: str | None = None) -> Client:
    if config_path is None:
        config = {}
    else:
        config = load_config(config_path).get("vault", {})

    return from_config(config)


def from_config(config: Dict) -> Client:
    config_server = config.get("server", {})
    url = config_server.get("url", None)
    verify = config_server.get("verify", None)
    namespace = resolve_namespace(config_server)

    config_auth = config.get("auth", {})
    auth_method = config_auth.get("method", "token")
    if auth_method == "token":
        token = resolve_token(config_auth)
    else:
        token = None

    client = Client(url=url, token=token, verify=verify, namespace=namespace)

    if auth_method == "approle":
        login_with_approle(client, config_auth)
    elif auth_method != "token":
        raise ValueError(f"Unknown auth method: {auth_method}")

    return client


def resolve_token(config_auth):
    if "tokenfile" in config_auth:
        with open(config_auth["tokenfile"]) as fd:
            return fd.read().strip()

    return config_auth.get("token", None)


def resolve_namespace(config: dict) -> str | None:
    try:
        return config["namespace"]
    except KeyError:
        return os.environ.get("VAULT_NAMESPACE", None)


#   -------------------------------------------------------------
#   Additional authentication backends
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def login_with_approle(client: Client, config_auth: dict):
    if "role_id" not in config_auth:
        raise ValueError("Missing role_id in auth configuration")

    client.auth.approle.login(
        role_id=config_auth["role_id"],
        secret_id=config_auth.get("secret_id", None),
    )
