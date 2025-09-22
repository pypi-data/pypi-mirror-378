## secretsmith

The secretsmith Python package allows **connecting to Vault or OpenBao**,
with support for several authentication methods, including using a token
or AppRole.

It also provides a simple wrapper to **query secrets from a kv2 store**.

This is a high-level wrapper around [hvac](https://python-hvac.org/).

At Nasqueron, we use this package to avoid writing boilerplate code in each
application that needs to interact with Vault or OpenBao to:
  - read a configuration file to determine login parameters
  - query a simple password from kv2 store from a path

When more and more applications need to interact with Vault or OpenBao,
and use the same authentication methods, the same patterns to query secrets,
to maintain this wrapper high-level library becomes useful.

### Login

Secretsmith uses the `hvac` library to connect to Vault or OpenBao.

If nothing is specified, it will try to connect to Vault using the environment
variables `VAULT_ADDR` and `VAULT_TOKEN`, or reading a token file at the
default path. Especially convenient during the development workflow.

When it's ready to be deployed, write a configuration file explaining how to
connect to Vault or OpenBao.

#### How to use in code?

Call secretsmith.login() with the path to the configuration file:

```python
import secretsmith

VAULT_CONFIG_PATH = '/path/to/config.yaml'

vault_client = secretsmith.login(config_path=VAULT_CONFIG_PATH)
```

Then, you can use the client as a hvac library Vault client.

We provide helper methods for common tasks, but you can also directly use hvac.

#### Configuration file

Secretsmith uses a YAML configuration file to determine the login parameters:

```
vault:
  server:
    url: https://127.0.0.1:8200
  auth:
    token: hvs.000000000000000000000000 
```

When using AppRole, the configuration file will look like:

```
vault:
  server:
    url: https://127.0.0.1:8200
    verify: /path/to/ca.pem
  auth:
    method: approle
    role_id: e5a7b66e-5d08-da9c-7075-71984634b882
    secret_id: 841771dc-11c9-bbc7-bcac-6a3945a69cd9
```

The format is based on the Vault execution module for SaltStack.

The following parameters are supported:
  - `server` - a block to specify the Vault or OpenBao server parameters
    - `url` - the URL
    - `verify` - the path to a CA certificate to verify the server's certificate
    - `namespace` - the namespace to use (by default, will follow environment)
  - `auth` - a block to specify the authentication method and parameters
    - `method` - what authentication backend to use, by default 'token'

Additional parameters are supported in the `auth` block depending
on the authentication method.

When the method is `token`:
  - `token` - the token to use
  - `token_file` - alternatively, the path to a file containing the token

When the method is `approle`:
    - `role_id` - the AppRole role ID (required)
    - `secret_id` - the AppRole secret ID (optional)

### Querying secrets

For kv2, we also provide helper methods for more common use cases.

If you store a password in the password field of the 'secret/app/db' path:

```python
import secretsmith
from secretsmith.vault import secrets

vault_client = secretsmith.login()
password = secrets.get_password(vault_client, "secret", "app/db")
```

To get the full k/v store at the 'secret/app/db' path:

```python
secret = secrets.read_secret(vault_client, "secret", "app/db")
```

If you also store custom metadata, you can use:

```python
secret, metadata = secrets.read_secret_with_custom_metadata(vault_client, "secret", "app/db")
```

In all those examples, you need to replace "secret" by your kv2 mount point.
The "secret" mount point is the default one if you didn't configure Vault.
